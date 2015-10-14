/*
 * estatepp.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <iostream>
#include <stdlib.h>
#include <assert.h>
#include <algorithm>
#include "estatepp.h"
#include "StateManager.h"
#include "util.h"

StateManager* sm;

// function prototypes for helper reuce functions
char* reduce_latest(state_item_t* d, int length);
char* reduce_sum(state_item_t* d, int length);
char* reduce_avg(state_item_t* d, int length);


void es_init(const char* ip, int port)
{
	std::string str_ip(ip);
	sm = new StateManager(str_ip, port);

	// start node
	sm->start();
}

void es_init_with_peers(const char* ip, int port, const char* peers)
{
	print_call();
	std::string str_ip(ip);
	sm = new StateManager(str_ip, port);
	// set peers
	std::string str_peers(peers);
	std::replace( str_peers.begin(), str_peers.end(), ';', ' '); // allow also ';' as separator
	sm->set_peers(str_peers);

	// start node
	sm->start();
}

void es_close()
{
	print_call();
	delete sm;
}

char* test;
const char* testpp()
{
	print_call();
	test = (char*)malloc(sizeof(char) * 5);
	strcpy(test, "abcd\0");
	printf("%s\n", test);
	return test;
	//sm->test();
}

void es_set(const char* k, const char* v)
{
	print_call();
	assert(sm != NULL);
	assert(k != NULL);
	assert(v != NULL);

	std::string str_k(k);
	std::string str_v(v);
	sm->set(str_k, str_v);
}

const char* es_get(const char* k)
{
	print_call();
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
	debug("calling reduce function\n");
	const char* res = reduce(data_buffer, size);
	free(data_buffer);
	debug("reduce result: %s\n", res);
	// return reduced
	return res;
}

/**
 * Work like normal get global method but uses internally predefined reduce functions.
 * Helps for interfacing with, e.g., Python code.
 * reduce_id:	0 = latest
 * 				1 = sum
 * 				2 = avg
 */
const char* es_get_global_predefined_reduce(const char* k, int reduce_id)
{
	print_call();
	if(reduce_id == 1)
		return es_get_global(k, reduce_sum);
	if(reduce_id == 2)
		return es_get_global(k, reduce_avg);
	return es_get_global(k, reduce_latest);
}

void es_del(const char* k)
{
	//print_call();
	assert(sm != NULL);
	assert(k != NULL);

	std::string str_k(k);
	sm->del(str_k);
}


//-----------------------------------------------------------------------------------------------------
// locally implemented defaul reduce functions (for easier interfacing to the lib from e.g. Python
//------------------------------------------------------------------------------------------------------
char* reduce_latest(state_item_t* d, int length)
{
	// maximum timestamp search
	int i = 0;
	const char* latest;
	unsigned long max_timestamp = 0;
	for(i=0; i < length; i++)
	{
		//printf("reduce(latest) input: n_id=%s ts=%lu value=%s\n", d[i].node_identifier, d[i].timestamp,  d[i].data);
		if(d[i].timestamp >= max_timestamp)
		{
			max_timestamp = d[i].timestamp;
			latest = d[i].data;
		}
	}
	if(max_timestamp >= 0)
		return (char*)latest;
	return (char*)"ES_REDUCE_ERROR";
}


char* reduce_sum(state_item_t* d, int length)
{
	// sum up all item values (treated as double)
	double sum = 0;
	int i;
	for(i = 0; i < length; i++)
	{
		//printf("reduce input(sum): n_id=%s ts=%lu value=%s\n", d[i].node_identifier, d[i].timestamp,  d[i].data);
		sum += string_to_double(d[i].data);
	}
	return (char*)double_to_string(sum).c_str();
}

char* reduce_avg(state_item_t* d, int length)
{
	// avg of all item values (treated as double)
	double sum = 0;
	int i = 0;
	for(i=0; i < length; i++)
	{
		//printf("reduce(avg) input: n_id=%s ts=%lu value=%s\n", d[i].node_identifier, d[i].timestamp,  d[i].data);
		sum += string_to_double(d[i].data);
	}
	return (char*)double_to_string(sum/(double)length).c_str();
}


