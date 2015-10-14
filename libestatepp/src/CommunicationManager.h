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
#include "StateItem.h"
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

	/* global request identifier counter: 64bit long, however we'll see overflows here if the system runs long enough */
	unsigned long request_count;

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

	/* zeromq management */
	zmqpp::context zmqctx;

	/* peer management */
	std::list<std::string> peer_lst;

	/* callback pointer, called when global requests are received */
	void (*get_global_callback_func)(const char* key) = NULL;

public:
	CommunicationManager(StateManager*, std::string, int);
	virtual ~CommunicationManager();
	virtual void start();
	virtual std::list<StateItem> request_global_state(std::string);
	virtual std::string get_local_identity();

	/* peer discovery */
	virtual std::list<std::string> get_peer_nodes();
	virtual void set_peer_nodes(std::list<std::string>);

	virtual bool is_state_item_of_node_in_list(StateItem si, std::list<StateItem> l);

	/* setter for get_global_callback */
	virtual void register_get_global_callback(void (*cb_func)(const char* key)) {this->get_global_callback_func = cb_func; }
};

#endif /* COMMUNICATIONMANAGER_H_ */
