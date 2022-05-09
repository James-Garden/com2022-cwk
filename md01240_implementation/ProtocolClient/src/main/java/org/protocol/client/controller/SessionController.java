package org.protocol.client.controller;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;

import org.protocol.client.config.MySessionHandler;
import org.protocol.client.entities.ProtocolMessage;
import org.springframework.messaging.converter.MappingJackson2MessageConverter;
import org.springframework.messaging.simp.stomp.StompFrameHandler;
import org.springframework.messaging.simp.stomp.StompHeaders;
import org.springframework.messaging.simp.stomp.StompSession;
import org.springframework.messaging.simp.stomp.StompSessionHandler;
import org.springframework.util.concurrent.ListenableFuture;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.socket.WebSocketHttpHeaders;
import org.springframework.web.socket.client.WebSocketClient;
import org.springframework.web.socket.client.standard.StandardWebSocketClient;
import org.springframework.web.socket.messaging.WebSocketStompClient;
import org.springframework.web.socket.sockjs.client.SockJsClient;
import org.springframework.web.socket.sockjs.client.Transport;
import org.springframework.web.socket.sockjs.client.WebSocketTransport;

public class SessionController {

	/**
	 * Session instance.
	 */
	private StompSession session;

	public void connect(String url, String username, String password)
			throws InterruptedException, ExecutionException, HttpClientErrorException {
		CountDownLatch latch = new CountDownLatch(1);
		StompSessionHandler sessionHandler = new MySessionHandler(latch);

		List<Transport> transports = new ArrayList<>(1);
		transports.add(new WebSocketTransport(new StandardWebSocketClient()));
		WebSocketClient transport = new SockJsClient(transports);
		WebSocketStompClient stompClient = new WebSocketStompClient(transport);
		stompClient.setMessageConverter(new MappingJackson2MessageConverter());


		String base64Credentials = CredentialController.getBasicAuth(username, password);

		final WebSocketHttpHeaders headers = new WebSocketHttpHeaders();
		headers.add("Authorization", "Basic " + base64Credentials);
		ListenableFuture<StompSession> future = null;
		future = stompClient.connect(url, headers, sessionHandler);

		latch.await();
		session = future.get();
	}
	

	
	public void sendMessage(ProtocolMessage protocolMessage) {
		session.send("/queue/click", protocolMessage);
    }

	public void subscribe(String endPoint, ISubscriber subscriber) {
		if (null == endPoint) {
			throw new NullPointerException("Null passed to subscribe");
		}

		session.subscribe(endPoint, new StompFrameHandler() {

			@Override
			public java.lang.reflect.Type getPayloadType(StompHeaders headers) {
				//subscriber.notifySubscriber();
				return ProtocolMessage.class;
			}

			@Override
			public void handleFrame(StompHeaders headers, Object payload) {
				if(payload instanceof ProtocolMessage) {
					ProtocolMessage pm = (ProtocolMessage)payload;
					subscriber.notifySubscriber(pm);
				}
			}

		});
	}

	/**
	 * Disconnect the session from server.
	 */
	public void disconnect() {
		if (null != session) {
			session.disconnect();
		}
	}

}
