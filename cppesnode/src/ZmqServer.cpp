/*
 * ZmqServer.cpp
 *
 *  Created on: Aug 13, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "ZmqServer.h"

namespace std
{

char* reduce_latest(state_item_t* d, int length)
{
	// maximum timestamp search
	int i = 0;
	const char* latest;
	unsigned long max_timestamp = 0;
	for(i=0; i < length; i++)
	{
		//printf("reduce(latest) input: n_id=%s ts=%lu value=%s\n", d[i].node_identifier, d[i].timestamp,  d[i].data);
		if(d[i].timestamp >= max_timestamp)
		{
			max_timestamp = d[i].timestamp;
			latest = d[i].data;
		}
	}
	if(max_timestamp >= 0)
		return (char*)latest;
	return (char*)"ES_REDUCE_ERROR";
}

char* reduce_sum(state_item_t* d, int length)
{
	// sum up all item values (treated as double)
	double sum = 0;
	int i;
	for(i = 0; i < length; i++)
	{
		//printf("reduce input(sum): n_id=%s ts=%lu value=%s\n", d[i].node_identifier, d[i].timestamp,  d[i].data);
		sum += string_to_double(d[i].data);
	}
	return (char*)double_to_string(sum).c_str();
}

char* reduce_avg(state_item_t* d, int length)
{
	// avg of all item values (treated as double)
	double sum = 0;
	int i = 0;
	for(i=0; i < length; i++)
	{
		//printf("reduce(avg) input: n_id=%s ts=%lu value=%s\n", d[i].node_identifier, d[i].timestamp,  d[i].data);
		sum += string_to_double(d[i].data);
	}
	return (char*)double_to_string(sum/(double)length).c_str();
}

ZmqServer::ZmqServer()
{
	this->local_api_port = 8800;
	this->estate_node_address = "127.0.0.1";
	this->estate_node_port = 9000;
	this->recv_socket = NULL;
	this->peers = "";

	this->init();
}

ZmqServer::ZmqServer(int local_api_port, string estate_node_address, int estate_node_port)
{
	this->local_api_port = local_api_port;
	this->estate_node_address = estate_node_address;
	this->estate_node_port = estate_node_port;
	this->recv_socket = NULL;
	this->peers = "";

	this->init();
}

ZmqServer::~ZmqServer()
{
	if(this->recv_socket)
	{
		this->recv_socket->close();
		delete this->recv_socket;
	}
}

void ZmqServer::init()
{
	// init zmq
	cout << "creating estate node with address: " << this->estate_node_address << ":" << this->estate_node_port << endl;
	this->recv_socket = new zmqpp::socket(this->zmqctx, zmqpp::socket_type::rep);
	//this->recv_socket->bind("tcp://*:" + int_to_string(this->local_api_port));
	this->recv_socket->bind("ipc:///tmp/estatezmq:" + int_to_string(this->local_api_port));
}

void ZmqServer::start()
{
	// init estate
	if(this->peers.size() < 1)
		es_init(this->estate_node_address.c_str(), this->estate_node_port);
	else
		es_init_with_peers(this->estate_node_address.c_str(), this->estate_node_port, this->peers.c_str());

	cout << "ZMQ API server listening to port: " << this->local_api_port  << endl;
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
			//cout << "received: " << request_msg.get(0) << " " << request_msg.get(1) << endl;

			if(request_msg.get(0) == "SET")
			{
				//--- SET command
				es_set(request_msg.get(1).c_str(), request_msg.get(2).c_str());
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
				else if(request_msg.get(2) == "SUM")
				{
					const char* data = es_get_global(request_msg.get(1).c_str(), reduce_sum);
					response_msg.push_back("OK");
					response_msg.push_back(data);
				}
				else if(request_msg.get(2) == "AVG")
				{
					const char* data = es_get_global(request_msg.get(1).c_str(), reduce_avg);
					response_msg.push_back("OK");
					response_msg.push_back(data);
				}
				else
				{
					response_msg.push_back("ERROR");
					response_msg.push_back("reduce function not implemented");
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
		//cout << "sending: " << response_msg.get(0) << endl;
		this->recv_socket->send(response_msg);
	}
}

void ZmqServer::set_peer_list(string peers)
{
	this->peers = peers;
	cout << "setting peers: " << peers << endl;
}

/* Helper */
string int_to_string(int i)
{
	stringstream s;
	s << i;
	return s.str();
}

string double_to_string(double d)
{
	stringstream s;
	s << d;
	return s.str();
}

double string_to_double(string s)
{
	return atof(s.c_str());
}

} /* namespace std */
