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
#include <string.h>

char* reduce_test(state_item_t d[], int length)
{
	printf("reduce input size: %d\n", length);
	int i = 0;
	for(i; i < length; i++)
		printf("reduce input[%d]: %s\n", i, d[i].data);
	return "reduce_result";
}

void client_a()
{
	es_init("127.0.0.1", 9000);

	es_set("k1", "value1.a");

	//const char* result = es_get("k1");
	//printf("GET k1 result: %s\n", result);

	usleep(1000 * 1000 * 10);
	//es_get_global("k1", reduce_test);
	usleep(1000 * 1000 * 1);

	//es_del("k1");

	es_close();
}

void client_b()
{
	es_init("127.0.0.1", 9001);

		es_set("k1", "value1.b");

		//const char* result = es_get("k1");
		//printf("GET k1 result: %s\n", result);

		usleep(1000 * 1000 * 10);
		//es_get_global("k1", reduce_test);
		usleep(1000 * 1000 * 1);

		//es_del("k1");

		es_close();
}

void client_c()
{
	es_init("127.0.0.1", 9002);

		es_set("k1", "value1.c");

		//const char* result = es_get("k1");
		//printf("GET k1 result: %s\n", result);

		usleep(1000 * 1000 * 10);
		//es_get_global("k1", reduce_test);
		usleep(1000 * 1000 * 1);

		//es_del("k1");

		es_close();
}

void client_d()
{
	es_init("127.0.0.1", 9003);

	es_set("k1", "value1.d");

	usleep(1000 * 1000 * 2);

	es_get_global("k1", reduce_test);

	usleep(1000 * 1000 * 1);

	es_del("k1");

	es_close();
}


int main(int argc, char *argv[]) {
	if (strcmp("A", argv[1]) == 0)
	{
		client_a();
	}
	else if (strcmp("B", argv[1]) == 0)
	{
		client_b();
	}
	else if (strcmp("C", argv[1]) == 0)
	{
		client_c();
	}
	else
	{
		client_d();
	}


	return EXIT_SUCCESS;
}
