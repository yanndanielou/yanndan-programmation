from logger import logger_config
import time


if __name__ == "__main__":
    with logger_config.application_logger("example_of_use_logger"):
      logger_config.print_and_log_info("print_and_log_info example")
      logger_config.print_and_log_warning("print_and_log_warning example")
      with logger_config.stopwatch_with_label(label="Wait 300 ms",inform_beginning=True):
        time.sleep(0.3)
      pass