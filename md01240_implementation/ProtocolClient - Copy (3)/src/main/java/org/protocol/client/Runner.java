package org.protocol.client;

import org.protocol.client.view.MainFrame;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 *
 */
@Component
public class Runner implements CommandLineRunner {

	/**
	 * Pull in the JFrame to be displayed.
	 */
	@Autowired
	private MainFrame frame;

	/**
	 * Display the form using the AWT EventQueue
	 */
	@Override
	public void run(String... args) throws Exception {
		java.awt.EventQueue.invokeLater(new Runnable() {
			@Override
			public void run() {
				frame.setVisible(true);
			}
		});
	}

}