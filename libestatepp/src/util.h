/*
 * util.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include <stdio.h>

#ifndef UTIL_H_
#define UTIL_H_

#define PRINT_CALLS 1
#define print_call(...) do { if (PRINT_CALLS) fprintf(stdout, "CALL: %s:%d:%s()\n", __FILE__, __LINE__, __func__); } while (0)

#define PRINT_DEBUG 1
#define debug(fmt, args...) do { if (PRINT_DEBUG) fprintf(stdout, "DEBUG: %s:%d:%s(): " fmt, __FILE__, __LINE__, __func__, ##args); } while (0)

#define PRINT_INFO 1
#define info(fmt, args...) do { if (PRINT_INFO) fprintf(stdout, "INFO: " fmt, ##args); } while (0)

#define PRINT_ERROR 1
#define error(fmt, args...) do { if (PRINT_ERROR) fprintf(stderr, "ERROR: %s:%d:%s(): " fmt, __FILE__, __LINE__, __func__, ##args); } while (0)

#endif /* UTIL_H_ */
