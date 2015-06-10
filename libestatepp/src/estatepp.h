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

	extern void estatepp_init(void);
	extern void estatepp_close(void);
	extern void testpp(void);

	/* our main state management API */
	extern void set(const char*,const char*);
	extern const char* get(const char*);
	extern void del(const char*);
	extern char* get_global(const char*, char*(*reduce)(char*)); // TODO: reduce function needs a list of strings (linked list of char*, create a corresponding strunct in the lib?)

#ifdef __cplusplus
}
#endif

#endif /* ESTATEPP_H_ */
