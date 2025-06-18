package cfx00854407.applications;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import cfx00854407.network.Sender;

public class ReproduceRl2b71PaeBehavior {
	private static final Logger LOGGER = LogManager.getLogger(ReproduceRl2b71PaeBehavior.class);


	
	public static void main(String[] args) {
		LOGGER.info(()->"Beginning of application");

		short counter_value = 10;
		Sender sender = new Sender();

		while (counter_value > 5) {
			for (int i = 0; i < 10; i++) {
				cfx00854407.utils.Sleep.waitSafe(cfx00854407.constants.Constants.MESSAGES_FREQUENCY);	
				sender.sendPaeAffcarMessage(cfx00854407.constants.Constants.DISPLAY_COLOR_NOT_BLOCKED, counter_value);
			}
			counter_value--;
		}
		for (int i = 0; i < 100; i++) {
			cfx00854407.utils.Sleep.waitSafe(cfx00854407.constants.Constants.MESSAGES_FREQUENCY);	
			sender.sendPaeAffcarMessage(cfx00854407.constants.Constants.DISPLAY_COLOR_BLOCKED, counter_value);
		}
		LOGGER.info(()->"End of application");

	}
}
