/*
 * StateManager.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <iostream>
#include "StateManager.h"
#include "util.h"

StateManager::StateManager(int local_instance)
{
	this->local_state = new LocalState();
	this->comm = new CommunicationManager(local_instance);

	std::cout << "Created eState StateManager for instance " << local_instance << std::endl;
}

StateManager::~StateManager()
{
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

void StateManager::del(std::string k)
{
	this->local_state->del(k);
}

