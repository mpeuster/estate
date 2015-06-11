/*
 * StateManager.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <iostream>
#include "StateManager.h"
#include "util.h"

StateManager::StateManager()
{
	std::cout << "Created eState StateManager" << std::endl;
	this->local_state = new LocalState();
	this->comm = new CommunicationManager();
}

StateManager::~StateManager()
{
	// TODO Auto-generated destructor stub
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

void StateManager::del(std::string k)
{
	this->local_state->del(k);
}

