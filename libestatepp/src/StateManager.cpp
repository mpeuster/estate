/*
 * StateManager.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <iostream>
#include <sstream>
#include "StateManager.h"
#include "util.h"

StateManager::StateManager(std::string ip, int port)
{
	this->local_state = new LocalState();
	this->comm = new CommunicationManager(this, ip, port);

	// always add this node as peer, if no other peers are specified
	std::stringstream local_address;
	local_address << ip << ":" << port;
	this->set_peers(local_address.str());
}

StateManager::~StateManager()
{
	delete this->local_state;
	delete this->comm;
}

void StateManager::start()
{
	if(this->comm)
		this->comm->start();
}

void StateManager::set(std::string k, std::string v)
{
	StateItem* si;
	if(this->local_state->exists(k))
	{
		// state item already exists: update it
		si = this->local_state->get(k);
		si->setData(v);
		si->setTimestamp(si->getTimestamp() + 1); // currently simple local versions
	}
	else
	{
		// new state item object needed
		si = new StateItem(v, this->comm->get_local_identity(), 0);
	}

	// make sure reference to state item is stored
	this->local_state->set(k, si);
}

std::string StateManager::get(std::string k)
{
	if(this->local_state->exists(k) && this->local_state->get(k) != NULL)
		return this->local_state->get(k)->getData();
	return "ES_NONE";
}

StateItem* StateManager::getItem(std::string k)
{
	if(this->local_state->exists(k) && this->local_state->get(k) != NULL)
		return this->local_state->get(k);
	return NULL;
}


/**
 * Collects all state items from other nodes and collects them in an
 * array of type "state_item_t".
 *
 * Arguments:
 * 	- k = key for item
 * 	- result_array = array pointer to store results in
 * Return: number of elements in result array
 */
int StateManager::get_global(std::string k, state_item_t* &result_array)
{
	std::list<StateItem> result_list = this->comm->request_global_state(k);

	// allocate memory for the result array
	int length = result_list.size();
	result_array = (state_item_t*)malloc(length * sizeof(state_item_t));
	debug("malloc size: %d\n", length);

	// fill the result array with data
	int i = 0;
	for (std::list<StateItem>::const_iterator it = result_list.begin(), end = result_list.end(); it != end; ++it)
	{
	    result_array[i].timestamp = it->getTimestamp();
	    result_array[i].node_identifier = it->getNodeIdentifier().c_str();
	    result_array[i].data = it->getData().c_str();
	    i++;
	}

	//static state_item_t result_array[result_list.size()];
	return length;
}

void StateManager::del(std::string k)
{
	this->local_state->del(k);
}

void StateManager::set_peers(std::string peer_str)
{
	// parse string an build peer list
	std::list<std::string> peer_lst;
	std::stringstream peers_stream(peer_str);
	while(peers_stream.good())
	{
		std::string tmp;
		peers_stream >> tmp;
		if(tmp.size() > 0)
			peer_lst.push_back(tmp);
	}
	// push peer list to comunication manager
	this->comm->set_peer_nodes(peer_lst);
}

