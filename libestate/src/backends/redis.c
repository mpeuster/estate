/*
 * redis.c
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <hiredis.h>
#include <stdio.h>
#include <stdlib.h>
#include "../util.h"

/* global redis context */
redisContext *redis_context;

void redis_init_connection()
{
	redis_context = redisConnect("127.0.0.1", 6379);
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
	free(redis_context);
}

void redis_set_string(char* key, char* value)
{

	redisReply *reply = redisCommand(redis_context, "SET %s %s", key, value);
	if(reply->type != REDIS_REPLY_ERROR)
		debug("k:%s %s\n", key, reply->str);
	else
		error("%s\n", reply->str);
	freeReplyObject(reply);
}
