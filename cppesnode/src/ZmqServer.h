/*
 * ZmqServer.h
 *
 *  Created on: Aug 13, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef ZMQSERVER_H_
#define ZMQSERVER_H_

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


public:
	ZmqServer();
	virtual ~ZmqServer();
	virtual void start();
};

} /* namespace std */

#endif /* ZMQSERVER_H_ */
