/*
 * StateManager.h
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef STATEMANAGER_H_
#define STATEMANAGER_H_

#include <iostream>
#include "LocalState.h"
#include "CommunicationManager.h"

class StateManager
{
private:
	LocalState* local_state;
	CommunicationManager* comm;

public:
	StateManager();
	virtual ~StateManager();
	virtual void test();
	virtual void set(std::string, std::string);
	virtual std::string get(std::string);
	virtual void del(std::string);
};

#endif /* STATEMANAGER_H_ */
