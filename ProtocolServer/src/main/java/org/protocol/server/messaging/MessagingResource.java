package org.protocol.server.messaging;

import java.security.Principal;
import java.util.HashMap;
import java.util.stream.Collectors;

import org.protocol.server.entities.ProtocolMessage;
import org.protocol.server.entities.Event;
import org.protocol.server.entities.ServerStorage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.messaging.simp.user.SimpUserRegistry;
import org.springframework.stereotype.Controller;

/**
 *
 */
@Controller
public class MessagingResource {

	/**
	 * Messaging template to forward the request.
	 */
	@Autowired private SimpMessagingTemplate template;
	
	@Autowired private SimpUserRegistry simpUserRegistry;
	

	@Autowired
	public MessagingResource(SimpMessagingTemplate template) {
		this.template = template;
	}

	@MessageMapping("/click")
	//@SendTo("/topic/click")
	public void send(ProtocolMessage protocolMessage, Principal principal)
			throws Exception {
		if(null == ServerStorage.getEvent()) {
			if(protocolMessage.getProtocolId().equals("P_GO_OUT")) {
				template.convertAndSendToUser(principal.getName(), "/queue/reply", new ProtocolMessage("P_OK", "Your invitation has been sent!"));
				ServerStorage.setEvent(new Event(principal.getName()));
				simpUserRegistry.getUsers().stream()
						.filter(x -> !x.getName().equals(principal.getName()))
						.collect(Collectors.toList())
						.forEach(y -> {
							template.convertAndSendToUser(y.getName(), "/queue/reply", new ProtocolMessage("P_INVITE", principal.getName() + " would like to go out this Saturday, are you available?"));
						});
			}
			if(protocolMessage.getProtocolId().equals("P_YES") || protocolMessage.getProtocolId().equals("P_NO")) {
				template.convertAndSendToUser(principal.getName(), "/queue/reply", new ProtocolMessage("P_NO_EVENT", "No event is schedule to respond to!"));
			}
		} else {
			if(protocolMessage.getProtocolId().equals("P_GO_OUT")) {
				template.convertAndSendToUser(principal.getName(), "/queue/reply", new ProtocolMessage("P_EVENT_EXISTS", "There's an ongoing event invitation, you cannot initiate a new one"));
			}
			if(protocolMessage.getProtocolId().equals("P_YES") || protocolMessage.getProtocolId().equals("P_NO")) {
				if(ServerStorage.getEvent().getHost().equals(principal.getName())) {
					template.convertAndSendToUser(principal.getName(), "/queue/reply", new ProtocolMessage("P_YOUR_EVENT", "You can not respond to your own event!"));
				} else {
					ServerStorage.getResponses().put(principal.getName(), protocolMessage.getProtocolId().contains("YES"));
					template.convertAndSendToUser(principal.getName(), "/queue/reply", new ProtocolMessage("P_OK", "Your response has been filed"));
				}
			}
			if(simpUserRegistry.getUserCount() -1 == ServerStorage.getResponses().size()) {
				StringBuilder stb = new StringBuilder();
				stb.append("Event is closed, ");
				ServerStorage.getResponses().forEach((key, value) -> stb.append(key + " " + (value ? " will come " : "will not come ")));
				ServerStorage.setEvent(null);
				ServerStorage.setResponses(new HashMap<>());
				template.convertAndSend("/topic/click", new ProtocolMessage("P_EVENT_END", stb.toString()));
			}
		}
	}
}
