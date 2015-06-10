/*
 * estatepp.cpp
 *
 *  Created on: Apr 24, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "estatepp.h"
#include "StateManager.h"
#include "util.h"

StateManager* sm;

void estatepp_init()
{
	sm = new StateManager();
}

void estatepp_close()
{
	delete sm;
}

void testpp()
{
	print_call();
	sm->test();
}

