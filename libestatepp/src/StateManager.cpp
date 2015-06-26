/*
 * StateManager.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <iostream>
#include "StateManager.h"
#include "util.h"

StateManager::StateManager(std::string ip, int port)
{
	this->local_state = new LocalState();
	this->comm = new CommunicationManager(this, ip, port);

	std::cout << "Created eState StateManager for instance: " << ip << ":" << port << std::endl;
}

StateManager::~StateManager()
{
	delete this->local_state;
	delete this->comm;
	std::cout << "Destroyed eState StateManager." << std::endl;
}

void StateManager::test()
{
	print_call();
}

void StateManager::set(std::string k, std::string v)
{
	this->local_state->set(k, v);
}

std::string StateManager::get(std::string k)
{
	return this->local_state->get(k);
}

std::string StateManager::get_global(std::string k)
{
	this->comm->request_global_state(k);
	return "ES_NONE";
}

void StateManager::del(std::string k)
{
	this->local_state->del(k);
}

