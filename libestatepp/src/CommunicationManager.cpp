/*
 * CommunicationManager.cpp
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "CommunicationManager.h"
#include "StateManager.h"


CommunicationManager::CommunicationManager(StateManager* sm, std::string ip, int port)
{
	// initialization
	this->sm = sm;
	this->my_ip = ip;
	this->my_port = port;

	// create publisher
	this->zpublisher = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::pub);
	this->zpublisher->bind("tcp://*:" + to_string(this->my_port));

	// pull socket to receive the request responses (on port = (orig_port + 1000)
	this->zresponsepull = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::pull);
	this->zresponsepull->bind("tcp://*:" + to_string(this->my_port + 1000));
	this->zresponsepull->set(zmqpp::socket_option::receive_timeout, 5000);

	// start subscriber thread
	this->request_subscriber_start();
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


/**
 * Request the global state by sending a state request to all peer nodes.
 * This is done by publishing a request to the zpublisher.
 */
std::list<StateItem> CommunicationManager::request_global_state(std::string k)
{
	// create and send request to all peers
	zmqpp::message request;
	request.push_back("global_state_request");
	request.push_back(this->my_ip);
	request.push_back(this->my_port);
	request.push_back(k);
	this->zpublisher->send(request);

	// prepare results structure
	std::list<StateItem> results;

	// receive results (we always expect to get results from all peers)
	uint num_peers = this->get_peer_nodes().size();
	for(uint i = 0; i < num_peers; i++)
	{
		zmqpp::message response;
		this->zresponsepull->receive(response);
		if(response.parts() > 2)
		{
			// unpack response message
			std::string sender_ip = response.get(1);
			int sender_port;
			response.get(sender_port, 2);
			// actual state item data
			std::string data = response.get(3);
			std::string node_identifier = response.get(4);
			int timestamp;
			response.get(timestamp, 5);
			// add response to results
			results.push_back(StateItem(data, node_identifier, timestamp));

			debug("(%s) received response from %s:%d\n", this->get_local_identity().c_str(), sender_ip.c_str(), sender_port);
		}
		// if we run in a timeout, we skip further tries to receive more responses
		if(response.parts() < 1)
			break;
	}

	// if we have more than one peer, we will check if we have all results (remove this later, but helpful to keep track during development)
	if(num_peers != results.size() && results.size() != 1)
		error("resulsts.size()=%d != num_peers=%d\n", results.size(), num_peers);

	return results;
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
			std::string key = request.get(3);
			debug("(%s) received request from %s:%d\n", this->get_local_identity().c_str(), sender_ip.c_str(), sender_port);

			// create ZMQ push socket for the response if it is not already present
			std::string conn_string = sender_ip + ":" + to_string(sender_port + 1000);
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
			if(si != NULL)
			{
				// send response message to requester
				zmqpp::message response;
				response.push_back("global_state_response");
				response.push_back(this->my_ip);
				response.push_back(this->my_port);
				response.push_back(si->getData()); // actual data for key
				response.push_back(si->getNodeIdentifier());
				response.push_back(si->getTimestamp());
				zresponsepush->send(response);
			}
		}
	}
}

std::list<std::string> CommunicationManager::get_peer_nodes()
{
	//TODO Dyn: replace this with a real discovery method
	std::list<std::string> lst;
	lst.push_front("127.0.0.1:9000");
	lst.push_front("127.0.0.1:9001");
	lst.push_front("127.0.0.1:9002");
	lst.push_front("127.0.0.1:9003");
	lst.push_front("127.0.0.1:9004");
	lst.push_front("127.0.0.1:9005");
	return lst;
}

std::string CommunicationManager::get_local_identity()
{
	//return this->my_ip + std::string(":") + to_string(this->my_port);
	return to_string(this->my_port);
}


