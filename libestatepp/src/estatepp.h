/*
 * estatepp.h
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef ESTATEPP_H_
#define ESTATEPP_H_

#ifdef __cplusplus
extern "C"
{
#endif
	/* basic data types */
	struct state_item_struct {
		int timestamp;
		const char* node_identifier;
		const char* data;
	};
	typedef struct state_item_struct state_item_t;

	/* basic initialization API */
	extern void es_init(const char* ip, int port);
	extern void es_init_with_peers(const char* ip, int port, const char* peers);
	extern void es_close(void);
	extern void testpp(void);

	/* our main state management API */
	extern void es_set(const char*,const char*);
	extern const char* es_get(const char*);
	extern void es_del(const char*);

	/**
	 * get global function gets a key and a reduce function pointer with the following
	 * signature:
	 * char* func (char*)
	 *
	 * argument 1: array of strings (all possible results)
	 * argument 2: length = number of items in array
	 * return: string (selected, reduced result)
	 */
	extern const char* es_get_global(const char* k, char* (*reduce)(state_item_t[], int));

#ifdef __cplusplus
}
#endif

#endif /* ESTATEPP_H_ */
