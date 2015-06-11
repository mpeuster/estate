/*
 * LocalState.cpp
 *
 *  Created on: Jun 10, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "LocalState.h"
#include "util.h"

LocalState::LocalState()
{
}

LocalState::~LocalState()
{
}

void LocalState::set(std::string k, std::string v)
{
	this->data[k] = v;
	debug("SET %s to %s\n", k.c_str(), v.c_str());
}

std::string LocalState::get(std::string k)
{
	debug("GET %s\n", k.c_str());
	if (this->exists(k))
		return this->data[k];
	return "ES_NONE"; // our reserves symbol if a key not exists
}

void LocalState::del(std::string k)
{
	this->data.erase(k);
	debug("DEL %s\n", k.c_str());
}


bool LocalState::exists(std::string k)
{
	std::tr1::unordered_map<std::string, std::string>::const_iterator search = this->data.find(k);
	return (search != this->data.end());
}
