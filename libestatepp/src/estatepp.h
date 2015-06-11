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

	extern void es_init(void);
	extern void es_close(void);
	extern void testpp(void);

	/* our main state management API */
	extern void es_set(const char*,const char*);
	extern const char* es_get(const char*);
	extern void es_del(const char*);
	extern char* es_get_global(const char*, char*(*reduce)(char*)); // TODO: reduce function needs a list of strings (linked list of char*, create a corresponding strunct in the lib?)

#ifdef __cplusplus
}
#endif

#endif /* ESTATEPP_H_ */
