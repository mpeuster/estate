/*
 * estate.c
 *
 *  Created on: Apr 21, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */


#include <stdio.h>
#include "backend.h"
#include "util.h"
#include "estate.h"


void estate_init()
{
	print_call();
	// init global memory store
	backend_init();
	//TODO return a state struct
}

void estate_close()
{
	print_call();
	// tear down global memory store
	backend_close();
}

void test(void)
{
    print_call();
    if(backend_set("key1", "this is value number 1"))
    	debug("SET OK\n");

    char *result = NULL;
    int len = backend_get("key1", &result);

    info("Received len: %d\n", len);
    info("Received string: %s\n", result);
}
