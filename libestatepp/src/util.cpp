/*
 * util.c
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */


#include "util.h"
#include <sstream>


std::string int_to_string(int i)
{
	std::stringstream s;
	s << i;
	return s.str();
}


std::string double_to_string(double d)
{
	std::stringstream s;
	s << d;
	return s.str();
}

double string_to_double(std::string s)
{
	return atof(s.c_str());
}

