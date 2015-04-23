/*
 * estate.c
 *
 *  Created on: Apr 21, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */


#include <stdio.h>
#include "backend.h"
#include "util.h"


void test(void)
{
    print_call();
    backend_init();

    backend_close();
}
