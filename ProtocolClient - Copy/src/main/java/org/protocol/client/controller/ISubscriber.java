package org.protocol.client.controller;

import org.protocol.client.entities.ProtocolMessage;

public interface ISubscriber {

	/**
	 * When a click is made all subscribers will be notified to this method.
	 */
	public void notifySubscriber(ProtocolMessage protocolMessage);

}
