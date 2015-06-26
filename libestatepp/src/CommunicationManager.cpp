/*
 * CommunicationManager.cpp
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "CommunicationManager.h"


CommunicationManager::CommunicationManager(std::string ip, int port)
{
	// initialization
	this->my_ip = ip;
	this->my_port = port;

	// create publisher
	this->zpublisher = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::pub);
	this->zpublisher->bind("tcp://*:" + to_string(this->my_port));

	// pull socket to receive the request responses (on port = (orig_port + 1000)
	this->zresponsepull = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::pull);
	this->zresponsepull->bind("tcp://*:" + to_string(this->my_port + 1000));
	this->zresponsepull->set(zmqpp::socket_option::receive_timeout, 1000);

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
	// delete objects
	delete this->zpublisher;
	delete this->zresponsepull;
}


/**
 * Request the global state by sending a state request to all peer nodes.
 * This is done by publishing a request to the zpublisher.
 */
void CommunicationManager::request_global_state(std::string k)
{
	// create request
	zmqpp::message request;
	request.push_back("global_state_request");
	request.push_back(this->my_ip);
	request.push_back(this->my_port);
	request.push_back(k);
	this->zpublisher->send(request);

	// TODO we need to ensure that we receive n results here .. print error if it is not the case.
	// TODO how to process the results?
	// receive results
	int num_peers = this->get_peer_nodes().size();
	// we always expect to get results from all peers
	for(int i = 0; i < num_peers; i++)
	{
		zmqpp::message response;
		this->zresponsepull->receive(response);
		if(response.parts() > 2)
		{
			std::string sender_ip = response.get(1);
			int sender_port;
			response.get(sender_port, 2);
			std::cout << "(" << this->get_local_identity() << ")" << " Received response: " << response.get(0) << " from " << sender_ip << ":" << to_string(sender_port) << std::endl;
		}
		// if we run in a timeout, we skip further tries to receive more responses
		if(response.parts() < 1)
			break;
	}
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
		std::cout << "(" << this->get_local_identity() << ")" << " Subscribed to: " << s << std::endl;
	}

	// infinity subscriber loop
	while(this->request_subscriber_active)
	{
		//std::cout << "(" << this->local_instance << ")" << " Subscriber thread wakeup." << std::endl;
		zmqpp::message request;
		zsubscriber.receive(request);
		if(request.parts() > 2)
		{
			std::string sender_ip = request.get(1);
			int sender_port;
			request.get(sender_port, 2);
			std::cout << "(" << this->get_local_identity() << ")" << " Received: " << request.get(0) << " from " << sender_ip << ":" << to_string(sender_port) << std::endl;
			//TODO respond to request. Queue it? Is queing not already presend thorugh ZMQ? -> just answer?

			// create ZMQ push socket to send responses to requester
			//FIXME this is inefficient! create on push socket for each peer, and keep it in a public list (or a peer object?)
			zmqpp::socket zresponsepush (this->zmqctx, zmqpp::socket_type::push);
			zresponsepush.connect("tcp://" + sender_ip + ":" + to_string(sender_port + 1000));
			zmqpp::message response;
			response.push_back("global_state_response");
			response.push_back(this->my_ip);
			response.push_back(this->my_port);
			response.push_back("DUMMY_CONTENT");
			zresponsepush.send(response);
			zresponsepush.close();
		}
	}
}

std::list<std::string> CommunicationManager::get_peer_nodes()
{
	//TODO fake discovery: replace this with a real discovery method
	std::list<std::string> lst;
	lst.push_front("127.0.0.1:9000");
	lst.push_front("127.0.0.1:9001");
	lst.push_front("127.0.0.1:9002");
	lst.push_front("127.0.0.1:9003");
	lst.push_front("127.0.0.1:9004");
	lst.push_front("127.0.0.1:9005");
	//TODO discovery list currently includes the local node! not sure if this may be helpful or a problem?
	return lst;
}

std::string CommunicationManager::get_local_identity()
{

	return this->my_ip + std::string(":") + to_string(this->my_port);
}


