/*
 * CommunicationManager.cpp
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "CommunicationManager.h"
#include <zmqpp/zmqpp.hpp>

CommunicationManager::CommunicationManager()
{
	// initialize the 0MQ context
	zmqpp::context context;

	// create and bind a server socket
	zmqpp::socket server (context, zmqpp::socket_type::push);
	server.bind("tcp://*:9000");

	// create and connect a client socket
	zmqpp::socket client (context, zmqpp::socket_type::pull);
	client.connect("tcp://127.0.0.1:9000");

	// Send a single message from server to client
	zmqpp::message request;
	request << "Hello";
	server.send(request);

	zmqpp::message response;
	client.receive(response);

	assert("Hello" == response.get(0));
	std::cout << "Grasslands test OK" << std::endl;

}

CommunicationManager::~CommunicationManager()
{
}

