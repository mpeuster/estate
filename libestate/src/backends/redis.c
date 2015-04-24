/*
 * redis.c
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <hiredis.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../util.h"

#include "redis.h"

/* global redis context */
redisContext *redis_context;

void redis_init_connection()
{
	redis_context = redisConnect(CONFIG_REDIS_HOST, CONFIG_REDIS_PORT);
	if (redis_context != NULL && redis_context->err)
	{
		error("Redis connection error: %s\n", redis_context->errstr);
		exit(1);
	}
	else
	{
		info("Redis connection established\n");
	}
}

void redis_close_connection()
{
	info("Redis connection closed\n");
	redisFree(redis_context);
}

int redis_set_string(char* key, char* value)
{
	//TODO we may need to use binary save strings

	int ret;

	// perform redis request
	redisReply *reply = redisCommand(redis_context, "SET %s %s", key, value);

	if (reply->type != REDIS_REPLY_ERROR)
	{
		debug("k:%s ... %s\n", key, reply->str);
		ret = 1;
	}
	else
	{
		error("%s\n", reply->str);
		ret = -1;
	}
	freeReplyObject(reply);
	return ret;
}

int redis_get_string(char *key, char **value)
{
	int ret;

	// perform redis request
	redisReply *reply = redisCommand(redis_context, "GET %s", key);

	if (reply->type == REDIS_REPLY_STRING)
	{
		debug("k:%s\n", key);
		//TODO copy reply string into local data structure
		ret = reply->len;
		*value = malloc(reply->len * sizeof(char));
		strcpy(*value, reply->str);
	}
	else
	{
		error("%s\n", reply->str);
		ret = -1;
	}
	freeReplyObject(reply);
	return ret;
}
