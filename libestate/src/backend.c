/*
 * backend.c
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <stdio.h>
#include "backends/redis.h"
#include "util.h"

void backend_init()
{
	print_call();

	redis_init_connection();
	redis_set_string("key1", "vlaue1 is a cool value");
}

void backend_close()
{
	print_call();
	redis_close_connection();
}

