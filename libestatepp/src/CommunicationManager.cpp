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

	// start subscriber thread
	this->request_subscriber_start();
}

CommunicationManager::~CommunicationManager()
{
	// delete objects
	delete this->zpublisher;
	// stop and delete subscriber thread
	this->request_subscriber_active = false;
	this->request_subscriber_thread->join();
	delete this->request_subscriber_thread;
}


/**
 * Request the global state by sending a state request to all peer nodes.
 * This is done by publishing a request to the zpublisher.
 */
void CommunicationManager::request_global_state(std::string k)
{

	//FIXME ugly string conversation (use json as message format)
	zmqpp::message request;
	std::stringstream msg;
	msg << "global_state_request##sender#" << this->get_local_identity() << "##key#" << k;
	request << msg.str();
	this->zpublisher->send(request);
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
	/* create one single ZMQ subscriber */
	zmqpp::socket zsubscriber (this->zmqctx, zmqpp::socket_type::sub);
	zsubscriber.set(zmqpp::socket_option::subscribe, "global_state_request");
	zsubscriber.set(zmqpp::socket_option::receive_timeout, 1000); // ensure that we check for termination from time to time

	/* subscribe to each peer node which is currently known to us */
	std::list<std::string> peer_list = this->get_peer_nodes();
	for(std::string s : peer_list)
	{
		zsubscriber.connect("tcp://" + s);
		std::cout << "(" << this->get_local_identity() << ")" << " Subscribed to: " << s << std::endl;
	}

	/* infinity subscriber loop */
	while(this->request_subscriber_active)
	{
		//std::cout << "(" << this->local_instance << ")" << " Subscriber thread wakeup." << std::endl;
		zmqpp::message response;
		zsubscriber.receive(response);
		if(response.parts() > 0)
		{
			std::cout << "(" << this->get_local_identity() << ")" << " Received: " << response.get(0) << std::endl;
			//TODO respond to request. Queue it? Is queing not already presend thorugh ZMQ? -> just answer?
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




/**
 * ZMQ Example:
 * 	this->local_instance = instance;
	// initialize the 0MQ context
	zmqpp::context context;

	// create and bind a server socket
	zmqpp::socket server (context, zmqpp::socket_type::push);
	server.bind("tcp://*:" + to_string(9000 + instance));

	// create and connect a client socket
	zmqpp::socket client (context, zmqpp::socket_type::pull);
	client.connect("tcp://127.0.0.1:" + to_string(9000 + instance));

	// Send a single message from server to client
	zmqpp::message request;
	request << "Hello";
	server.send(request);

	zmqpp::message response;
	client.receive(response);

	assert("Hello" == response.get(0));
	std::cout << "ZMQ test OK" << std::endl;
 */
