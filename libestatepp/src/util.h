/*
 * util.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <stdio.h>
#include <iostream>

#ifndef UTIL_H_
#define UTIL_H_

#define PRINT_CALLS 0
#define print_call(...) do { if (PRINT_CALLS) fprintf(stdout, "CALL: %s:%d:%s()\n", __FILE__, __LINE__, __func__); } while (0)

#define PRINT_DEBUG 0
#define debug(fmt, args...) do { if (PRINT_DEBUG) fprintf(stdout, "\e[34mDEBUG: %s:%d:%s():\e[0m" fmt, __FILE__, __LINE__, __func__, ##args); } while (0)

#define PRINT_INFO 1
#define info(fmt, args...) do { if (PRINT_INFO) fprintf(stdout, "\e[32mINFO:\e[0m" fmt, ##args); } while (0)

#define PRINT_WARN 1
#define warn(fmt, args...) do { if (PRINT_WARN) fprintf(stderr, "\e[33mWARNING: %s:%d:%s():\e[0m" fmt, __FILE__, __LINE__, __func__, ##args); } while (0)

#define PRINT_ERROR 1
#define error(fmt, args...) do { if (PRINT_ERROR) fprintf(stderr, "\e[31mERROR: %s:%d:%s():\e[0m" fmt, __FILE__, __LINE__, __func__, ##args); } while (0)

std::string to_string(int);

#endif /* UTIL_H_ */
