package org.protocol.server.entities;

import java.util.HashMap;

public class ServerStorage {
	
	private static Event event;

	private static HashMap<String, Boolean> responses = new HashMap<>();

	public static Event getEvent() {
		return event;
	}

	public static void setEvent(Event event) {
		ServerStorage.event = event;
	}

	public static HashMap<String, Boolean> getResponses() {
		return responses;
	}

	public static void setResponses(HashMap<String, Boolean> responses) {
		ServerStorage.responses = responses;
	}
}
