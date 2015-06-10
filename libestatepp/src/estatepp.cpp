/*
 * estatepp.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "estatepp.h"
#include "StateManager.h"
#include "util.h"

StateManager* sm;

void estatepp_init()
{
	sm = new StateManager();
}

void estatepp_close()
{
	delete sm;
}

void testpp()
{
	print_call();
	sm->test();
}

void set(const char* k, const char* v)
{
	print_call();
	std::string str_k(k);
	std::string str_v(v);
	sm->set(str_k, str_v);
}

const char* get(const char* k)
{
	print_call();
	std::string str_k(k);
	return sm->get(str_k).c_str();
}

void del(const char* k)
{
	print_call();
	std::string str_k(k);
	sm->del(str_k);
}

