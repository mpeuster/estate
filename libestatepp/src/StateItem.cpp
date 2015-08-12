/*
 * StateItem.cpp
 *
 *  Created on: Aug 12, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#include "StateItem.h"



StateItem::StateItem(std::string data, std::string node_identifier, int timestamp)
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

