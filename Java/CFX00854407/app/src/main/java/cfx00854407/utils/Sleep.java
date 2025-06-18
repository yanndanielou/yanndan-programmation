package cfx00854407.utils;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import cfx00854407.applications.ReproduceFuturPaeBehavior;

public class Sleep {
	private static final Logger LOGGER = LogManager.getLogger(ReproduceFuturPaeBehavior.class);

	public static void waitSafe(long milliseconds) {
		try {
			Thread.sleep(cfx00854407.constants.Constants.MESSAGES_FREQUENCY);
		} catch (InterruptedException e) {
			e.printStackTrace();
			LOGGER.error(()->"Thread.sleep throws exception:" + e.getMessage());
		}
	}
	
}
