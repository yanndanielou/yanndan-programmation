# -*-coding:Utf-8 -*

import fnmatch
import time
from typing import Optional

from watchdog.events import (
    DirCreatedEvent,
    DirModifiedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from logger import logger_config


class DownloadEventHandler(FileSystemEventHandler):
    def __init__(self, filename_pattern: str) -> None:
        self.filename_pattern: str = filename_pattern
        self.file_detected: bool = False
        self.file_detected_path: Optional[str] = None

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        if fnmatch.fnmatch(event.src_path, self.filename_pattern):
            logger_config.print_and_log_info(f"File downloaded (created): {event.src_path}")
            self.file_detected = True
            self.file_detected_path = event.src_path

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if fnmatch.fnmatch(event.src_path, self.filename_pattern):
            logger_config.print_and_log_info(f"File downloaded (updated) : {event.src_path}")
            self.file_detected = True
            self.file_detected_path = event.src_path


def monitor_download(directory_path: str, filename_pattern: str, timeout_in_seconds: int = 100) -> Optional[str]:
    download_event_handler = DownloadEventHandler(filename_pattern)
    observer = Observer()
    observer.schedule(download_event_handler, directory_path, recursive=False)
    observer.start()

    logger_config.print_and_log_info("En attente du téléchargement ou de la mise à jour du fichier...")
    try:
        while not download_event_handler.file_detected and timeout_in_seconds > 0:
            time.sleep(1)
            timeout_in_seconds -= 1
    except KeyboardInterrupt:
        observer.stop()
        logger_config.print_and_log_warning("KeyboardInterrupt")
    observer.stop()
    observer.join()

    return download_event_handler.file_detected_path
