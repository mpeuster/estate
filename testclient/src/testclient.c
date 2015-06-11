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

int main(void) {
	estatepp_init();
	//testpp();

	es_set("k1", "value1");
	const char* result = es_get("k1");
	printf("received: %s\n", result);
	es_del("k1");

	estatepp_close();
	return EXIT_SUCCESS;
}
