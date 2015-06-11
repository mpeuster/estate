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
	std::cout << "k:" << k << " v:" << v << std::endl;
}

std::string LocalState::get(std::string k)
{
	std::cout << this->data[k] << std::endl;
	return this->data[k];
}

void LocalState::del(std::string k)
{

}
