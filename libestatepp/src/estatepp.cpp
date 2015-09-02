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

	// start node
	sm->start();
}

void es_init_with_peers(const char* ip, int port, const char* peers)
{
	std::string str_ip(ip);
	sm = new StateManager(str_ip, port);
	// set peers
	std::string str_peers(peers);
	sm->set_peers(str_peers);

	// start node
	sm->start();
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

const char* es_get_global(const char* k, char* (*reduce)(state_item_t*, int))
{
	print_call();
	assert(sm != NULL);
	assert(k != NULL);

	// get list state items from all nodes
	std::string str_k(k);
	state_item_t* data_buffer; // array of state_item_t pointers (allocated in sm->get_global)
	int size = sm->get_global(str_k, data_buffer);

	// if we get an empty array, we'll abort before entering the reduce function
	if(size < 1)
		return "ES_NONE";

	// run custom reduce function on returned data
	info("calling reduce function\n");
	char* res = reduce(data_buffer, size);
	info("reduce result: %s\n", res);
	free(data_buffer);

	// return reduced
	return res;
}

void es_del(const char* k)
{
	//print_call();
	assert(sm != NULL);
	assert(k != NULL);

	std::string str_k(k);
	sm->del(str_k);
}

