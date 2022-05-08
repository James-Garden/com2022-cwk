package org.protocol.client.controller;

import java.util.Base64;

public class CredentialController {

	/**
	 * Constructs and returns the basic authentication string.
	 * 
	 * @param username
	 *            The username.
	 * @param password
	 *            The password.
	 * @return The encoded authentication string.
	 */
	public static String getBasicAuth(String username, String password) {
		if (null == username || null == password) {
			throw new NullPointerException("Null passed to getBasicAuth");
		}
		String plainCredentials = username + ":" + password;
		return Base64.getEncoder().encodeToString(plainCredentials.getBytes());
	}

}
