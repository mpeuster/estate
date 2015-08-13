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
#include "StateItem.h"
#include "estatepp.h"

class StateManager
{
private:
	LocalState* local_state;
	CommunicationManager* comm;

public:
	StateManager(std::string ip, int port);
	virtual ~StateManager();
	virtual void set(std::string, std::string);
	virtual std::string get(std::string);
	virtual StateItem* getItem(std::string);
	virtual int get_global(std::string, state_item_t* &result_array);
	virtual void del(std::string);
	virtual void set_peers(std::string);
	virtual void start();
};

#endif /* STATEMANAGER_H_ */
