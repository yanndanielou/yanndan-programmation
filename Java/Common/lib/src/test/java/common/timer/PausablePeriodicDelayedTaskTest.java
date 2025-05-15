package common.timer;

import common.exceptions.BadLogicException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class PausablePeriodicDelayedTaskTest {
	static final Logger LOGGER = LogManager.getLogger(PausablePeriodicDelayedTaskTest.class);

	private final static int DELAY_200_MILLISECOND = 200 * TimeConstants.ONE_MILLISECOND;

	protected PausablePeriodicDelayedTaskForTests timerTaskForTests;

	private static void sleepThread(int milliseconds) {
		try {
			Thread.sleep(milliseconds);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}

	private static void sleepThread(double milliseconds) {
		sleepThread((int) milliseconds);
	}

	class PausablePeriodicDelayedTaskForTests extends PausablePeriodicDelayedTask {

		int numberOfTimerRuns = 0;

		public PausablePeriodicDelayedTaskForTests(long delay) {
			super(delay);
		}

		@Override
		public void run() {
			numberOfTimerRuns++;
			LOGGER.info(() -> " run, counter:" + numberOfTimerRuns);
		}

		public int getNumberOfTimerRuns() {
			return numberOfTimerRuns;
		}
	}

	@Nested
	public class TwoHundredsMillisecondsSecondTimer {

		private int taskDelay = DELAY_200_MILLISECOND;

		@BeforeEach
		public void before() {
			LOGGER.info(() -> "before OneSecondTimer");
			timerTaskForTests = new PausablePeriodicDelayedTaskForTests(taskDelay);
		}

		/*@AfterEach
		public void after() {
			if(timerTaskForTests != null && !timerTaskForTests.isCancelled()) {
				timerTaskForTests.cancel();
			}
		}
		*/
		@Test
		public void runAfterFirstDelay() {
			sleepThread(taskDelay * 0.1);
			assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

			sleepThread(taskDelay * 1.1);
			assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);
		}

		@Test
		public void runPeriodicallyAfterEachDelay() {
			sleepThread(taskDelay * 0.5);
			assertEquals(0, timerTaskForTests.getNumberOfTimerRuns());
			sleepThread(taskDelay * 0.6);
			assertEquals(1, timerTaskForTests.getNumberOfTimerRuns());

			sleepThread(taskDelay * 0.5);
			assertEquals(1, timerTaskForTests.getNumberOfTimerRuns());
			sleepThread(taskDelay * 0.6);
			assertEquals(2, timerTaskForTests.getNumberOfTimerRuns());

			sleepThread(taskDelay * 0.5);
			assertEquals(2, timerTaskForTests.getNumberOfTimerRuns());
			sleepThread(taskDelay * 0.6);
			assertEquals(3, timerTaskForTests.getNumberOfTimerRuns());

			sleepThread(taskDelay * 0.5);
			assertEquals(3, timerTaskForTests.getNumberOfTimerRuns());
			sleepThread(taskDelay * 0.6);
			assertEquals(4, timerTaskForTests.getNumberOfTimerRuns());
		}

		@Nested
		public class BeforeFirstRun {

			@Test
			public void doesNotRunDuringPause() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);
			}

			@Test
			public void runAgainAfterResume() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);
			}

			@Test
			public void doesNotRunIfCancel() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.cancel();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);
			}

			@Test
			public void cannotBeResumedIfCancel() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.cancel();
				sleepThread(taskDelay * 1.1);

				assertThrows(BadLogicException.class, () -> timerTaskForTests.resume());
			}

			@Test
			public void cannotBePausedIfCancel() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.cancel();
				sleepThread(taskDelay * 0.1);

				assertThrows(BadLogicException.class, () -> timerTaskForTests.pause());
			}

			@Test
			public void cannotBePausedIfAlreadyPaused() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);

				assertThrows(BadLogicException.class, () -> timerTaskForTests.pause());
			}

			@Test
			public void cannotResumeIfNotPaused() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				assertThrows(BadLogicException.class, () -> timerTaskForTests.resume());
			}

			@Test
			public void canPauseAndResumeSeveralTimesAndRunAfterGoodDelay() {

				int cumulatedTimeOutsideOfPause = 0;

				@SuppressWarnings("unused")
				int cumulatedTimeDuringPause = 0;

				for (int i = 0; i < 9; i++) {

					timerTaskForTests.pause();
					sleepThread(taskDelay * 0.5);
					cumulatedTimeDuringPause += 100;
					assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

					timerTaskForTests.resume();
					sleepThread(taskDelay * 0.1);
					cumulatedTimeOutsideOfPause += 100;
					System.out.println("Cumulated waited outside of pause: " + cumulatedTimeOutsideOfPause);
					assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);
				}

				sleepThread(taskDelay * 0.1);
				cumulatedTimeOutsideOfPause += 100;
				System.out.println("Cumulated waited outside of pause: " + cumulatedTimeOutsideOfPause);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);
			}

			@Test
			public void canPauseAndResumeSeveralTimesWithoutCrash() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 0);

			}
		}

		@Nested
		public class BetweenFirstAndSecondRun {

			@BeforeEach
			public void before() {
				System.out.println("before BetweenFirstAndSecondRun");
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);
			}

			@Test
			public void doesNotRunDuringPause() {

				timerTaskForTests.pause();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);
			}

			@Test
			public void runAgainAfterResume() {

				timerTaskForTests.pause();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 2);
			}

			@Test
			public void doesNotRunIfCancel() {

				timerTaskForTests.cancel();
				sleepThread(taskDelay * 1.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);
			}

			@Test
			public void cannotBeResumedIfCancel() {

				timerTaskForTests.cancel();
				sleepThread(taskDelay * 1.1);

				assertThrows(BadLogicException.class, () -> timerTaskForTests.resume());
			}

			@Test
			public void cannotBePausedIfCancel() {

				timerTaskForTests.cancel();
				sleepThread(taskDelay * 0.1);

				assertThrows(BadLogicException.class, () -> timerTaskForTests.pause());
			}

			@Test
			public void cannotBePausedIfAlreadyPaused() {

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);

				assertThrows(BadLogicException.class, () -> timerTaskForTests.pause());
			}

			@Test
			public void cannotResumeIfNotPaused() {

				assertThrows(BadLogicException.class, () -> timerTaskForTests.resume());
			}

			@Test
			public void canPauseAndResumeRunAfterGoodDelay() {
				sleepThread(taskDelay * 0.5);
				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.5);
				timerTaskForTests.resume();
				assertEquals(1, timerTaskForTests.getNumberOfTimerRuns());
				sleepThread(taskDelay * 1);
				assertEquals(2, timerTaskForTests.getNumberOfTimerRuns());
				sleepThread(taskDelay * 1);
				assertEquals(3, timerTaskForTests.getNumberOfTimerRuns());
				sleepThread(taskDelay * 1);
				assertEquals(4, timerTaskForTests.getNumberOfTimerRuns());
			}

			@Test
			public void canPauseAndResumeSeveralTimesAndRunAfterGoodDelay() {

				int cumulatedTimeOutsideOfPause = 0;
				int cumulatedTimeDuringPause = 0;

				for (int i = 0; i < 2; i++) {

					timerTaskForTests.pause();
					sleepThread(taskDelay * 0.5);
					cumulatedTimeDuringPause += taskDelay * 0.5;
					System.out.println("Cumulated waited during pause: " + cumulatedTimeDuringPause);

					assertEquals(1, timerTaskForTests.getNumberOfTimerRuns());

					timerTaskForTests.resume();
					sleepThread(taskDelay * 0.4);
					cumulatedTimeOutsideOfPause += taskDelay * 0.4;
					System.out.println("Cumulated waited outside of pause: " + cumulatedTimeOutsideOfPause);
					assertEquals(1, timerTaskForTests.getNumberOfTimerRuns());
				}

				sleepThread(taskDelay * 0.3);
				cumulatedTimeOutsideOfPause += taskDelay * 0.3;
				System.out.println("Cumulated waited outside of pause: " + cumulatedTimeOutsideOfPause);
				assertEquals(2, timerTaskForTests.getNumberOfTimerRuns());
			}

			@Test
			public void canPauseAndResumeSeveralTimesWithoutCrash() {
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				timerTaskForTests.pause();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

				timerTaskForTests.resume();
				sleepThread(taskDelay * 0.1);
				assertEquals(timerTaskForTests.getNumberOfTimerRuns(), 1);

			}

		}

	}
}
