/*
 * LocalState.h
 *
 *  Created on: Jun 10, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef LOCALSTATE_H_
#define LOCALSTATE_H_

#include <iostream>
#include <tr1/unordered_map>
#include "StateItem.h"

class LocalState
{
private:
	std::tr1::unordered_map<std::string, StateItem*> data;

public:
	LocalState();
	virtual ~LocalState();
	virtual void set(std::string, StateItem* v);
	virtual StateItem* get(std::string);
	virtual void del(std::string);
	virtual bool exists(std::string);
};

#endif /* LOCALSTATE_H_ */
