/*
 * CommunicationManager.cpp
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "CommunicationManager.h"
#include "StateManager.h"

// Attention: MAX_REQUEST_RETRY * RESPONSE_TIMEOUT_MSEC > control link delay must hold, otherwise nothing will work
#define RESPONSE_TIMEOUT_MSEC 1000
#define MAX_REQUEST_RETRY 3

CommunicationManager::CommunicationManager(StateManager* sm, std::string ip, int port)
{
	print_call();
	// initialization
	this->sm = sm;
	this->my_ip = ip;
	this->my_port = port;
	this->request_count = 0;

	// create publisher
	this->zpublisher = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::pub);
	this->zpublisher->bind("tcp://*:" + int_to_string(this->my_port));

	// pull socket to receive the request responses (on port = (orig_port + 1000)
	this->zresponsepull = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::pull);
	this->zresponsepull->bind("tcp://*:" + int_to_string(this->my_port + 1000));
	this->zresponsepull->set(zmqpp::socket_option::receive_timeout, RESPONSE_TIMEOUT_MSEC);
}

CommunicationManager::~CommunicationManager()
{
	// stop and delete subscriber thread
	this->request_subscriber_active = false;
	this->request_subscriber_thread->join();
	delete this->request_subscriber_thread;
	// close connections
	this->zpublisher->close();
	this->zresponsepull->close();
	for(std::pair<std::string, zmqpp::socket*> kv : this->zresponsepush_map)
	{
		if(kv.second != NULL)
			kv.second->close();
	}

	// delete objects
	delete this->zpublisher;
	delete this->zresponsepull;
}

void CommunicationManager::start()
{
	info("starting node with %lu peers\n", this->get_peer_nodes().size());
	// start subscriber thread
	this->request_subscriber_start();
}

/**
 * Request the global state by sending a state request to all peer nodes.
 * This is done by publishing a request to the zpublisher.
 */
std::list<StateItem> CommunicationManager::request_global_state(std::string k)
{
	print_call();
	// prepare results structure
	std::list<StateItem> results;

	// store local request ID to identify response
	unsigned long request_id = this->request_count;
	this->request_count++;

	// re-publish the request until result is complete or MAX_REQUEST_RETRY reached
	int request_try = 0;
	while(request_try < MAX_REQUEST_RETRY && results.size() < this->get_peer_nodes().size())
	{
		// create and request message to be published for all peers
		// (we have to do this inside the loop because message objects are flushed on send)
		zmqpp::message request;
		request.push_back("global_state_request");
		request.push_back(this->my_ip);
		request.push_back(this->my_port);
		request.push_back(request_id);
		request.push_back(k);
		// publish request message
		this->zpublisher->send(request);
		debug("(%s) published request k=%s; rid=%ld\n", this->get_local_identity().c_str(),  k.c_str(), request_id);

		// try to get all results of one request directly in this inner loop
		while(results.size() < this->get_peer_nodes().size())
		{
			// fetch message from input queue
			zmqpp::message response;
			this->zresponsepull->receive(response);

			// if we run into timeout, we stop this loop and re-publish the request
			if(response.parts() < 1)
				break;

			if(response.parts() > 6)
			{
				// unpack response message:
				// 0: constant message type
				// 1: sender IP
				std::string sender_ip = response.get(1);
				// 2: sender port
				int sender_port;
				response.get(sender_port, 2);
				// 3: request ID:
				unsigned long response_id;
				response.get(response_id, 3);
				// 4: state item: data
				std::string data = response.get(4);
				// 5: state item: node identifier
				std::string node_identifier = response.get(5);
				// 6: state item: timestamp
				long timestamp;
				response.get(timestamp, 6);

				debug("(%s) received response from %s:%d: k=%s; v=%s; rid=%ld\n", this->get_local_identity().c_str(), sender_ip.c_str(), sender_port, k.c_str(), data.c_str(), response_id);

				// decide if we have a valid response for the current request
				if(response_id != request_id)
				{
					debug("(%s) dropping response from %s:%d: rid=%ld != %ld\n", this->get_local_identity().c_str(), sender_ip.c_str(), sender_port, response_id, request_id);
					continue;
				}

				// generate state item
				StateItem si = StateItem(data, node_identifier, timestamp);

				// decide if we add the response to our global result
				if(this->is_state_item_of_node_in_list(si, results))
				{
					debug("(%s) dropping response from %s:%d: StateItem exists.\n", this->get_local_identity().c_str(), sender_ip.c_str(), sender_port);
					continue;
				}

				// response can be used: add it to our result list
				results.push_back(si);
			}
		} // end inner while
		// next try
		request_try++;
	} // end outer while

	// display a message if we still have not all results
	if(this->get_peer_nodes().size() != results.size() && this->get_peer_nodes().size() > 1)
		debug("get_global response resulsts.size()=%lu != num_peers=%d\n", results.size(), this->get_peer_nodes().size());

	// filter empty results, we don't want them in our reduce functions
	std::list<StateItem> filtered_results;
	for (std::list<StateItem>::const_iterator it = results.begin(), end = results.end(); it != end; ++it)
	{
		if(it->getData() != "ES_NOT_PRESENT")
		{
			filtered_results.push_back(*it);
		}
	}

	// return results
	debug("return results for rid=%ld\n", request_id);
	return filtered_results;
}


/**
 * Starts a thread that subscribes to all peers and subscribes to get_global requests.
 * It is also responsible to answer these requests.
 */
void CommunicationManager::request_subscriber_start()
{
	// start thread
	this->request_subscriber_active = true;
	this->request_subscriber_thread = new std::thread(&CommunicationManager::request_subscriber_thread_func, this);
}

/**
 * Subscriber thread functionality.
 */
void CommunicationManager::request_subscriber_thread_func()
{
	print_call();
	// create one single ZMQ subscriber
	zmqpp::socket zsubscriber (this->zmqctx, zmqpp::socket_type::sub);
	zsubscriber.set(zmqpp::socket_option::subscribe, "global_state_request");
	zsubscriber.set(zmqpp::socket_option::receive_timeout, 1000); // ensure that we check for termination from time to time

	// subscribe to each peer node which is currently known to us
	std::list<std::string> peer_list = this->get_peer_nodes();
	for(std::string s : peer_list)
	{
		zsubscriber.connect("tcp://" + s);
		info("(%s) subscribed to %s\n", this->get_local_identity().c_str(), s.c_str());
	}

	// infinity subscriber loop
	while(this->request_subscriber_active)
	{
		zmqpp::message request;
		zsubscriber.receive(request);
		if(request.parts() > 2)
		{
			// parse request
			std::string sender_ip = request.get(1);
			int sender_port;
			request.get(sender_port, 2);
			unsigned long request_id;
			request.get(request_id, 3);
			std::string key = request.get(4);
			debug("(%s) received request from %s:%d; rid=%ld\n", this->get_local_identity().c_str(), sender_ip.c_str(), sender_port, request_id);

			// create ZMQ push socket for the response if it is not already present
			std::string conn_string = sender_ip + ":" + int_to_string(sender_port + 1000);
			zmqpp::socket* zresponsepush;

			//TODO: Dyn: This map has to be updated dynamically if nodes can join/leave
			if(!this->zresponsepush_map[conn_string])
			{
				// only if not present
				zresponsepush = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::push);
				zresponsepush->connect("tcp://" + conn_string);
				this->zresponsepush_map[conn_string] = zresponsepush;
				info("(%s) created push socket for: %s\n", this->get_local_identity().c_str(), conn_string.c_str());
			}
			zresponsepush = this->zresponsepush_map[conn_string];

			// get local state item
			StateItem* si = this->sm->getItem(key);

			// send response message to requester
			zmqpp::message response;
			response.push_back("global_state_response");
			response.push_back(this->my_ip);
			response.push_back(this->my_port);
			response.push_back(request_id);
			if(si != NULL)
			{	// return state item if present on this node
				response.push_back(si->getData()); // actual data for key
				response.push_back(si->getNodeIdentifier());
				response.push_back(si->getTimestamp());
			}
			else
			{	// return indicator that state item was not found
				response.push_back("ES_NOT_PRESENT");
				response.push_back(this->get_local_identity());
				response.push_back(0);
			}
			zresponsepush->send(response);
		}
	}
}

std::list<std::string> CommunicationManager::get_peer_nodes()
{
	return this->peer_lst;
}

void CommunicationManager::set_peer_nodes(std::list<std::string> peer_lst)
{
	//TODO Dyn: replace this with a real discovery method
	this->peer_lst = peer_lst;
}

std::string CommunicationManager::get_local_identity()
{
	// this is used to identify each estate node
	return this->my_ip + std::string(":") + int_to_string(this->my_port);
	//return to_string(this->my_port);
}

bool CommunicationManager::is_state_item_of_node_in_list(StateItem si, std::list<StateItem> l)
{
	for (std::list<StateItem>::const_iterator it = l.begin(), end = l.end(); it != end; ++it)
	{
		if(it->getNodeIdentifier() == si.getNodeIdentifier())
			return true;
	}
	return false;
}


