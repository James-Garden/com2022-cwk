/**
 * 
 */
package org.protocol.client.view;

import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.Date;

import javax.swing.DefaultListModel;
import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JScrollPane;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;

import org.protocol.client.controller.ISubscriber;
import org.protocol.client.controller.SessionController;
import org.protocol.client.entities.ProtocolMessage;

import javax.swing.JButton;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import javax.swing.LayoutStyle.ComponentPlacement;

/**
 * @author Panerass
 *
 */
public class MainFrame extends javax.swing.JFrame implements ISubscriber {

	private static final long serialVersionUID = 1L;

	/**
	 * The label for connection representation.
	 */
	private JLabel connectLabel;

	/**
	 * The model of the logging list.
	 */
	private DefaultListModel<String> logModel;
	
	private JList<String> logList;

	/**
	 * Session controller instance.
	 */
	private SessionController sessionController;

	/**
	 * Creates new form DemoFrame
	 * 
	 * @throws InterruptedException
	 */
	public MainFrame() {
		initComponents();

		this.addWindowListener(new WindowAdapter() {
			@Override
			public void windowOpened(WindowEvent we) {
				new Thread(new Runnable() {
					public void run() {
						String text = "Couldn't connect";
						boolean connected = true;
						sessionController = new SessionController();
						try {
							sessionController.connect("ws://localhost:8080/server/click", "markos", "doufos");
						} catch (Exception ex) {
							connected = false;
							text = ex.getMessage();
							System.out.println("catch(Exception)");
						}

						if (connected) {
							text = "Connected";
							sessionController.subscribe("/topic/click", MainFrame.this);
							sessionController.subscribe("/user/queue/reply", MainFrame.this);
						}
						updateGUI(text);

					}
				}).start();
			}
		});

		this.addWindowListener(new java.awt.event.WindowAdapter() {
			public void windowClosing(WindowEvent winEvt) {
				sessionController.disconnect();
				System.exit(0);
			}
		});

	}

	/**
	 * This method is called from within the constructor to initialize the form.
	 */
	private void initComponents() {
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		setTitle("Spring Boot - GUI Application");

		setSize(405, 271);

		connectLabel = new JLabel("Trying to connect");
		connectLabel.setHorizontalAlignment(SwingConstants.CENTER);

		JScrollPane scrollPane = new JScrollPane();
		
		JButton btnGoOut = new JButton("Go out!");
		btnGoOut.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				sessionController.sendMessage(new ProtocolMessage("P_GO_OUT", null));
			}
		});
		
		JButton btnNewButton = new JButton("Yes");
		btnNewButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				sessionController.sendMessage(new ProtocolMessage("P_YES", null));
			}
		});
		
		JButton btnNo = new JButton("No");
		btnNo.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				sessionController.sendMessage(new ProtocolMessage("P_NO", null));
			}
		});
		GroupLayout groupLayout = new GroupLayout(getContentPane());
		groupLayout.setHorizontalGroup(
			groupLayout.createParallelGroup(Alignment.LEADING)
				.addGroup(groupLayout.createSequentialGroup()
					.addGap(89)
					.addComponent(connectLabel, GroupLayout.DEFAULT_SIZE, 209, Short.MAX_VALUE)
					.addGap(93))
				.addGroup(groupLayout.createSequentialGroup()
					.addContainerGap()
					.addComponent(scrollPane, GroupLayout.DEFAULT_SIZE, 371, Short.MAX_VALUE)
					.addContainerGap())
				.addGroup(groupLayout.createSequentialGroup()
					.addContainerGap()
					.addComponent(btnGoOut)
					.addPreferredGap(ComponentPlacement.RELATED, 169, Short.MAX_VALUE)
					.addComponent(btnNewButton)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(btnNo)
					.addContainerGap())
		);
		groupLayout.setVerticalGroup(
			groupLayout.createParallelGroup(Alignment.LEADING)
				.addGroup(groupLayout.createSequentialGroup()
					.addContainerGap()
					.addComponent(connectLabel)
					.addGap(28)
					.addComponent(scrollPane, GroupLayout.PREFERRED_SIZE, 105, GroupLayout.PREFERRED_SIZE)
					.addGap(40)
					.addGroup(groupLayout.createParallelGroup(Alignment.BASELINE)
						.addComponent(btnGoOut)
						.addComponent(btnNewButton)
						.addComponent(btnNo))
					.addContainerGap())
		);
		logModel = new DefaultListModel<>();
		logList = new JList<String>(logModel);
		scrollPane.setViewportView(logList);
		getContentPane().setLayout(groupLayout);
	}

	/**
	 * Updates connectLabel from main thread.
	 * 
	 * @param test
	 */
	public void updateGUI(final String test) {
		if (!SwingUtilities.isEventDispatchThread()) {
			SwingUtilities.invokeLater(new Runnable() {
				@Override
				public void run() {
					connectLabel.setText(test);
				}
			});
			return;
		}
		connectLabel.setText(test);
	}

	/**
	 * Adds new rows to the log list.
	 * 
	 * @param text
	 */
	public void updateLogList(String text) {
		logModel.addElement(text);
		logList.ensureIndexIsVisible(logModel.getSize());
	}

	@Override
	public void notifySubscriber(ProtocolMessage protocolMessage) {
		updateLogList(protocolMessage.getText());

	}
}