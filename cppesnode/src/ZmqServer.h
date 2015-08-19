/*
 * ZmqServer.h
 *
 *  Created on: Aug 13, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef ZMQSERVER_H_
#define ZMQSERVER_H_

#include <iostream>
#include <string>
#include <sstream>
#include <stdlib.h>
#include <zmqpp/zmqpp.hpp>
#include <estatepp.h>

namespace std
{

class ZmqServer
{
private:
	/* zeromq management */
	zmqpp::context zmqctx;
	zmqpp::socket* recv_socket;

	/* local configuration */
	int local_api_port;
	string estate_node_address;
	int estate_node_port;
	string peers;

	virtual void init();

public:
	ZmqServer();
	ZmqServer(int local_api_port, string estate_node_address, int estate_node_port);
	virtual ~ZmqServer();
	virtual void start();
	virtual void set_peer_list(string);
};

/* Helper */
string int_to_string(int );
string double_to_string(double);
double string_to_double(string);

} /* namespace std */

#endif /* ZMQSERVER_H_ */
