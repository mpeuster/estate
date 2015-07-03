/*
 * estatepp.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <iostream>
#include <stdlib.h>
#include <assert.h>
#include "estatepp.h"
#include "StateManager.h"
#include "util.h"

StateManager* sm;

void es_init(const char* ip, int port)
{
	std::string str_ip(ip);
	sm = new StateManager(str_ip, port);
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
	assert(sm != NULL);
	assert(k != NULL);
	assert(v != NULL);

	std::string str_k(k);
	std::string str_v(v);
	sm->set(str_k, str_v);
}

const char* es_get(const char* k)
{
	//print_call();
	assert(sm != NULL);
	assert(k != NULL);

	std::string str_k(k);
	return sm->get(str_k).c_str();
}

const char* es_get_global(const char* k, char* (*reduce)(state_item_t[], int))
{
	print_call();
	assert(sm != NULL);
	assert(k != NULL);

	state_item_t d1, d2, d3;
	d1.data = "value1.1"; d1.timestamp = 1;
	d2.data = "value1.2"; d2.timestamp = 23;
	d3.data = "vlaue1.3"; d3.timestamp = 42;
	state_item_t data[3];
	data[0] = d1;
	data[1] = d2;
	data[2] = d3;

	info("calling reduce function\n");
	char* res = reduce(data, sizeof(data) / sizeof(state_item_t));
	info("reduce result: %s\n", res);

	std::string str_k(k);
	return sm->get_global(str_k).c_str();
}

void es_del(const char* k)
{
	//print_call();
	assert(sm != NULL);
	assert(k != NULL);

	std::string str_k(k);
	sm->del(str_k);
}

