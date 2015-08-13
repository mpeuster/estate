/**
 * This program creates a stand alone running estate node using the estatepp lib.
 *
 * It offers ZMQ based IPC to be used by other processes.
 */

#include <iostream>
#include <sstream>
#include <stdlib.h>
#include "ZmqServer.h"

using namespace std;

int main(int argc, char* argv[]) {

	ZmqServer* zs = NULL;

	if(argc < 2)
	{
		// single node with default ports
		zs = new ZmqServer(8800, "127.0.0.1", 9000);
	}
	else
	{
		if(strcmp(argv[1], "help") == 0)
		{
			// display help
			cout << "Help: cppesnode [local_api_port] [local_estate_ip] [port] [peer1_ip] [port] ... [peerN_ip] [port]" << endl;
			exit(0);
		}
		else
		{
			// parse arguments
			int local_api_port = atoi(argv[1]);
			string local_enode_address = argv[2];
			int local_enode_port = atoi(argv[3]);

			// build peer string
			stringstream peers;
			for(int i = 2; i < argc; i+=2)
			{
				peers << argv[i] << ":" << argv[i+1] << " ";
			}
			// configure server with arguments
			zs = new ZmqServer(local_api_port, local_enode_address, local_enode_port);
			zs->set_peer_list(peers.str());
		}
	}

	// run node
	if(zs)
		zs->start();
	return 0;
}
