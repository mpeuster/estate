/*
 * backend.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef BACKEND_H_
#define BACKEND_H_

#define BACKEND_REDIS 1

void backend_init(void);
void backend_close(void);

int backend_set(char *key, char *value);
int backend_get(char *key, char **value);

#endif /* BACKEND_H_ */
