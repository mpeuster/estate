/**
 * This program creates a stand alone running estate node using the estatepp lib.
 *
 * It offers ZMQ based IPC to be used by other processes.
 */

#include <iostream>
#include "ZmqServer.h"

using namespace std;

int main() {

	ZmqServer* zs = new ZmqServer();
	zs->start();

	return 0;
}
