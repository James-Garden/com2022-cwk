package org.protocol.server.entities;

public class ProtocolMessage
{
	private String protocolId;
    private String text;

    public ProtocolMessage() {}
    
    

	public ProtocolMessage(String protocolId, String text) {
		super();
		this.protocolId = protocolId;
		this.text = text;
	}



	public String getProtocolId() {
		return protocolId;
	}

	public void setProtocolId(String protocolId) {
		this.protocolId = protocolId;
	}

	public String getText() {
		return text;
	}

	public void setText(String text) {
		this.text = text;
	}

    
}