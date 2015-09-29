/*
 * StateItem.cpp
 *
 *  Created on: Aug 12, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "StateItem.h"
#include <chrono>
#include "util.h"

// select used timestamp mechanism
// 0 = local logical time (tstamp++ on each local set)
// 1 = real time (tstamp = systemtime in msec)
#define TIMESTAMPTYPE 1


StateItem::StateItem(std::string data, std::string node_identifier, unsigned long timestamp)
{
	this->timestamp = timestamp;
	this->node_identifier = node_identifier;
	this->data = data;
}

StateItem::~StateItem()
{
}

std::string StateItem::toString()
{
	return "StateItem@" + this->node_identifier + "(value=" + this->data + ")";
}

void StateItem::updateTimestamp()
{
	if(TIMESTAMPTYPE == 0)
	{
		this->setTimestamp(this->getTimestamp() + 1); // local logical time
	}
	else if(TIMESTAMPTYPE == 1)
	{
		this->setTimestamp(
				(long)std::chrono::duration_cast<std::chrono::milliseconds>(
						std::chrono::system_clock::now().time_since_epoch()
						).count()); // local system clock
	}
	//debug("TIMESTAMP: StateItem@%s = %ld\n", this->node_identifier.c_str(), this->getTimestamp());
}

