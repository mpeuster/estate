/*
 * CommunicationManager.h
 *
 *  Created on: Jun 11, 2015
 *      Author: Manuel Peuster (manuel.peuster@uni-paderborn.de)
 */

#ifndef COMMUNICATIONMANAGER_H_
#define COMMUNICATIONMANAGER_H_

class CommunicationManager
{
private:
	/* used to specify different communication ports when multiple nodes are executed on one machine */
	/* default is 0 */
	int local_instance;

public:
	CommunicationManager(int);
	virtual ~CommunicationManager();
};

#endif /* COMMUNICATIONMANAGER_H_ */
