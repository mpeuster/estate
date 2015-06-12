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
#include <zmqpp/zmqpp.hpp>
#include "util.h"

class CommunicationManager
{
private:
	/* used to specify different communication ports when multiple nodes are executed on one machine */
	/* default is 0 */
	int local_instance;

	/* request publisher */
	zmqpp::socket* zpublisher;

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
	CommunicationManager(int);
	virtual ~CommunicationManager();
	virtual void request_global_state();
};

#endif /* COMMUNICATIONMANAGER_H_ */
