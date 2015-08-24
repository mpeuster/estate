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
	unsigned long timestamp;
	std::string node_identifier;
	std::string data;

public:
	StateItem(std::string data, std::string node_identfier, unsigned long timestamp);
	virtual ~StateItem();

	std::string toString();

	void updateTimestamp();

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

	long getTimestamp() const
	{
		return timestamp;
	}

	void setTimestamp(long timestamp)
	{
		this->timestamp = timestamp;
	}
};



#endif /* STATEITEM_H_ */
