/*
 * CommunicationManager.h
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef COMMUNICATIONMANAGER_H_
#define COMMUNICATIONMANAGER_H_

#include <thread>
#include <chrono>
#include <sstream>
#include <zmqpp/zmqpp.hpp>
#include "util.h"
#include <assert.h>
#include <tr1/unordered_map>

class StateManager;

class CommunicationManager
{
private:
	/* references */
	StateManager* sm;

	/* identification of this node */
	std::string my_ip;
	int my_port;
	virtual std::string get_local_identity();

	/* request publisher */
	zmqpp::socket* zpublisher;

	/* response puller */
	zmqpp::socket* zresponsepull;

	/* response pusher (we have one socket open to each of our peers!) */
	std::tr1::unordered_map<std::string, zmqpp::socket*> zresponsepush_map;

	/* request subscriber thread management */
	std::thread *request_subscriber_thread = NULL;
	virtual void request_subscriber_start();
	virtual void request_subscriber_thread_func();
	bool request_subscriber_active = false;

	/* peer discovery */
	virtual std::list<std::string> get_peer_nodes();

	/* zeromq management */
	zmqpp::context zmqctx;

public:
	CommunicationManager(StateManager*, std::string, int);
	virtual ~CommunicationManager();
	virtual std::list<std::string> request_global_state(std::string);
};

#endif /* COMMUNICATIONMANAGER_H_ */
