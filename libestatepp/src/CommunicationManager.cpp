/*
 * CommunicationManager.cpp
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "CommunicationManager.h"


CommunicationManager::CommunicationManager(int instance)
{
	// initialization
	this->local_instance = instance;

	// start subscriber thread
	this->request_subscriber_start();

	this->request_global_state();

}

CommunicationManager::~CommunicationManager()
{
	// stop and delete subscriber thread
	this->request_subscriber_active = false;
	this->request_subscriber_thread->join();
	delete this->request_subscriber_thread;
}

void CommunicationManager::request_global_state()
{
	//TODO replace this by real functionality, esp.: call it only from one node in the network (see manual node in example.py)
	/* test code to publish requests */
	zmqpp::socket zpublisher (this->zmqctx, zmqpp::socket_type::pub);
	zpublisher.bind("tcp://*:" + to_string(9000 + this->local_instance));

	for(int i = 0; i < 20; i++)
	{
		zmqpp::message request;
		request << "global_state_request:test";
		zpublisher.send(request);
		std::this_thread::sleep_for(std::chrono::milliseconds(300));
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
	std::cout << "normal thread operation... " << std::endl;
}

/**
 * Subscriber thread functionality.
 */
void CommunicationManager::request_subscriber_thread_func()
{
	//TODO Support n-1 subscriptions! One connect command for each, but only one zsubscriber!
	zmqpp::socket zsubscriber (this->zmqctx, zmqpp::socket_type::sub);
	zsubscriber.connect("tcp://127.0.0.1:" + to_string(9000 + this->local_instance));
	zsubscriber.set(zmqpp::socket_option::subscribe, "global_state_request");
	zsubscriber.set(zmqpp::socket_option::receive_timeout, 1000); // ensure that we check for termination from time to time

	while(this->request_subscriber_active)
	{
		std::cout << "I am the subscriber Thread!" << std::endl;

		zmqpp::message response;
		zsubscriber.receive(response);
		if(response.parts() > 0)
		{
			std::cout << "Received: " << response.get(0) << std::endl;
		}
	}
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
