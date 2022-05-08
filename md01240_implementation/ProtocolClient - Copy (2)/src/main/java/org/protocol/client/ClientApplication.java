package org.protocol.client;

import org.protocol.client.view.MainFrame;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class ClientApplication {

	/**
	 * Creates Spring application without web modules and not headless.
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		new SpringApplicationBuilder(ClientApplication.class).headless(false).web(false).run(args);
	}

	/**
	 * MainFrame bean.
	 * 
	 * @return
	 */
	@Bean
	public MainFrame frame() {
		return new MainFrame();
	}
}
