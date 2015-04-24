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
#include <estate.h>

int main(void) {
	//puts("running testclient");
	estate_init();
	test();
	estate_close();
	return EXIT_SUCCESS;
}
