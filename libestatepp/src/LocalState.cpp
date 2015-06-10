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
	// TODO Auto-generated constructor stub

}

LocalState::~LocalState()
{
	// TODO Auto-generated destructor stub
}

void LocalState::set(std::string k, std::string v)
{
	print_call();
	std::cout << "k:" << k << " v:" << v << std::endl;
}

std::string LocalState::get(std::string)
{
	print_call();
	return "none";
}

void LocalState::del(std::string)
{
	print_call();

}
