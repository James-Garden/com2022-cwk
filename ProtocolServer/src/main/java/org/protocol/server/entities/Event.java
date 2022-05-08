package org.protocol.server.entities;

public class Event {
	
	private String host;
	
	public Event() {

	}

	public Event(String host) {
		super();
		this.host = host;
	}

	public String getHost() {
		return host;
	}

	public void setHost(String host) {
		this.host = host;
	}
}


