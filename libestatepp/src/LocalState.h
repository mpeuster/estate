/*
 * LocalState.h
 *
 *  Created on: Jun 10, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef LOCALSTATE_H_
#define LOCALSTATE_H_

#include <iostream>

class LocalState
{
public:
	LocalState();
	virtual ~LocalState();
	virtual void set(std::string, std::string);
	virtual std::string get(std::string);
	virtual void del(std::string);
};

#endif /* LOCALSTATE_H_ */
