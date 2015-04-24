/*
 * backend.c
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <stdio.h>
#include "backends/redis.h"
#include "util.h"
#include "backend.h"

const int ACT_BACKEND = BACKEND_REDIS;

void backend_init()
{
	print_call();
	if (ACT_BACKEND == BACKEND_REDIS)
	{
		redis_init_connection();
	}
}

int backend_set(char *key, char *value)
{
	print_call();
	if (ACT_BACKEND == BACKEND_REDIS)
	{
		return redis_set_string(key, value);
	}
	return -1;
}

int backend_get(char *key, char **value)
{
	print_call();
	if (ACT_BACKEND == BACKEND_REDIS)
	{
		int ret = redis_get_string(key, value);
		if (ret < 0)
			error("Backend get failed\n");
		return ret;
	}
	return -1;
}

void backend_close()
{
	print_call();
	redis_close_connection();
}

