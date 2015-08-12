/*
 * StateItem.h
 *
 *  Created on: Aug 12, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef STATEITEM_H_
#define STATEITEM_H_

#include <iostream>

class StateItem
{
private:
	int timestamp;
	std::string node_identifier;
	std::string data;

public:
	StateItem(std::string data, std::string node_identfier, int timestamp);
	virtual ~StateItem();

	std::string toString();

	const std::string& getData() const
	{
		return data;
	}

	void setData(const std::string& data)
	{
		this->data = data;
	}

	const std::string& getNodeIdentifier() const
	{
		return node_identifier;
	}

	void setNodeIdentifier(const std::string& nodeIdentifier)
	{
		node_identifier = nodeIdentifier;
	}

	int getTimestamp() const
	{
		return timestamp;
	}

	void setTimestamp(int timestamp)
	{
		this->timestamp = timestamp;
	}
};



#endif /* STATEITEM_H_ */
