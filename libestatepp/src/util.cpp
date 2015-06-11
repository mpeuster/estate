/*
 * util.c
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */


#include "util.h"
#include <sstream>


std::string to_string(int i)
{
	std::stringstream s;
	s << i;
	return s.str();
}



