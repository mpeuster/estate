/*
 * redis.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef BACKENDS_REDIS_H_
#define BACKENDS_REDIS_H_

void redis_init_connection(void);
void redis_close_connection(void);
void redis_set_string(char* key, char* value);

#endif /* BACKENDS_REDIS_H_ */
