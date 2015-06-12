/*
 ============================================================================
 Name        : testclient.c
 Author      : Manuel Peuster (manuel.peuster@uni-paderborn.de)
 Version     :
 Copyright   : (c) 2015 by Manuel Peuster
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <estatepp.h>
#include <time.h>

int main(void) {
	es_init("127.0.0.1", 9000);
	//testpp();

	es_set("k1", "value1");
	const char* result = es_get("k1");
	printf("received from get: %s\n", result);

	usleep(1000 * 1000 * 2);
	es_get_global("k1");
	usleep(1000 * 1000 * 2);

	es_del("k1");

	es_close();
	return EXIT_SUCCESS;
}
