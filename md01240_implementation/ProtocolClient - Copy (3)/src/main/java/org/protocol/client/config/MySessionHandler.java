package org.protocol.client.config;

import java.util.concurrent.CountDownLatch;

import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompHeaders;
import org.springframework.messaging.simp.stomp.StompSession;
import org.springframework.messaging.simp.stomp.StompSessionHandlerAdapter;

public class MySessionHandler extends StompSessionHandlerAdapter {

	/**
	 * Is used to wait for the connection to be made or fail. We need this
	 * because connection is asynchronous.
	 */
	private final CountDownLatch latch;

	public MySessionHandler(final CountDownLatch latch) {
		this.latch = latch;
	}

	/**
	 * When client connected release the thread which waiting.
	 */
	@Override
	public void afterConnected(StompSession session, StompHeaders connectedHeaders) {
		try {
			System.out.println("afterConnected");
		} finally {
			latch.countDown();
		}
	}

	@Override
	public void handleException(StompSession session, StompCommand command, StompHeaders headers, byte[] payload,
			Throwable exception) {
	}

	/**
	 * When client has authentication problems release the thread which waiting.
	 */
	@Override
	public void handleTransportError(StompSession session, Throwable exception) {
		try {
			System.out.println("handleTransportError");
		} finally {
			latch.countDown();
		}
	}
}