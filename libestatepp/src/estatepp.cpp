/*
 * estatepp.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <iostream>
#include <stdlib.h>
#include "estatepp.h"
#include "StateManager.h"
#include "util.h"

StateManager* sm;

void es_init()
{
	sm = new StateManager();
}

void es_close()
{
	delete sm;
}

void testpp()
{
	print_call();
	//sm->test();
}

void es_set(const char* k, const char* v)
{
	//print_call();
	if(sm == NULL)
	{
		error("es_init() never called!\n");
		exit(1);
	}
	if(k == NULL || v == NULL)
	{
		error("NULL is not a valid key nor a valid value!\n");
		return;
	}
	std::string str_k(k);
	std::string str_v(v);
	sm->set(str_k, str_v);
}

const char* es_get(const char* k)
{
	//print_call();
	if(sm == NULL)
	{
		error("es_init() never called!\n");
		exit(1);
	}
	if(k == NULL)
	{
		error("NULL is not a valid key!\n");
		return "ES_NONE";
	}
	std::string str_k(k);
	return sm->get(str_k).c_str();
}

void es_del(const char* k)
{
	//print_call();
	if(sm == NULL)
	{
		error("es_init() never called!\n");
		exit(1);
	}
	if(k == NULL)
	{
		error("NULL is not a valid key!\n");
		return;
	}
	std::string str_k(k);
	sm->del(str_k);
}

