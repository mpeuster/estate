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

//TODO remove eclipse error for state_item_t
char* reduce_test(state_item_t d[], int length)
{
	printf("reduce input size: %d\n", length);
	int i = 0;
	for(i; i < length; i++)
		printf("reduce input[%d]: %s\n", i, d[i].data);
	return "reduce_result";
}

int main(void) {
	es_init("127.0.0.1", 9000);
	//testpp();

	es_set("k1", "value1");
	const char* result = es_get("k1");
	printf("GET k1 result: %s\n", result);

	usleep(1000 * 1000 * 1);
	es_get_global("k1", reduce_test);
	usleep(1000 * 1000 * 1);

	es_del("k1");

	es_close();
	return EXIT_SUCCESS;
}
