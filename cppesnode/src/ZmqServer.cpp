/*
 * ZmqServer.cpp
 *
 *  Created on: Aug 13, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "ZmqServer.h"

namespace std
{

char* reduce_latest(state_item_t d[], int length)
{
	// TODO implement real reduce latest functionality
	printf("reduce input size: %d\n", length);
	int i = 0;
	for(i=0; i < length; i++)
	{
		printf("reduce input[%d]: %s\n", i, d[i].data);
	}
	return "reduce_result";
}

ZmqServer::ZmqServer()
{
	// init estate
	es_init("127.0.0.1", 9000);

	// init zmq
	this->recv_socket = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::rep);
	this->recv_socket->bind("tcp://*:8800");
}

ZmqServer::~ZmqServer()
{
	if(this->recv_socket)
	{
		this->recv_socket->close();
		delete this->recv_socket;
	}
}

void ZmqServer::start()
{
	cout << "running ZMQ server ..." << endl;
	while (true)
	{
		// prepare messages
		zmqpp::message response_msg;
		zmqpp::message request_msg;
		// receive requests
		this->recv_socket->receive(request_msg);
		// work on request
		if(request_msg.parts() > 1)
		{
			cout << "received: " << request_msg.get(0) << " " << request_msg.get(1) << endl;
			// TODO call libestate

			if(request_msg.get(0) == "SET")
			{
				//--- SET command
				es_set(request_msg.get(1).c_str(), request_msg.get(2).c_str());
				//cout << "SET VALUE: " << request_msg.get(2) << endl;
				response_msg.push_back("OK");
			}
			else if(request_msg.get(0) == "GET")
			{
				//--- GET command
				const char* data = es_get(request_msg.get(1).c_str());
				response_msg.push_back("OK");
				response_msg.push_back(data);
			}
			else if(request_msg.get(0) == "DEL")
			{
				//--- DEL command
				es_del(request_msg.get(1).c_str());
				response_msg.push_back("OK");
			}
			else if(request_msg.get(0) == "GET_GLOBAL")
			{
				//--- GET_GLOBAL command
				if(request_msg.get(2) == "LATEST")
				{
					const char* data = es_get_global(request_msg.get(1).c_str(), reduce_latest);
					response_msg.push_back("OK");
					response_msg.push_back(data);
				}
				else
				{
					response_msg.push_back("ERROR");
					response_msg.push_back("reduce function not implemented");
					//TODO add avg, sum reduce functions
				}
			}
			else
			{
				response_msg.push_back("ERROR");
				response_msg.push_back("unknown command");
			}
		}
		else
		{
			response_msg.push_back("ERROR");
			response_msg.push_back("missing message parts");
		}
		// send reply
		cout << "sending: " << response_msg.get(0) << endl;
		this->recv_socket->send(response_msg);
	}
}

} /* namespace std */
