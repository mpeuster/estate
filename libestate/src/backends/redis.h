/*
 * redis.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef BACKENDS_REDIS_H_
#define BACKENDS_REDIS_H_

#define CONFIG_REDIS_HOST "127.0.0.1"
#define CONFIG_REDIS_PORT 6379

void redis_init_connection(void);
void redis_close_connection(void);
int redis_set_string(char* key, char* value);
int redis_get_string(char* key, char** value);

#endif /* BACKENDS_REDIS_H_ */
