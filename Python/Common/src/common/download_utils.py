# -*-coding:Utf-8 -*

import fnmatch
import os
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from warnings import deprecated

from logger import logger_config
from watchdog.events import (
    DirCreatedEvent,
    DirModifiedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer


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


def get_files_and_modification_time(directory_path: str, filename_pattern: str) -> List[Tuple[str, float]]:
    files_and_modified_time: List[Tuple[str, float]] = []
    for file in os.listdir(directory_path):
        if fnmatch.fnmatch(file, filename_pattern):
            file_path = os.path.join(directory_path, file)
            files_and_modified_time.append((file_path, os.path.getmtime(file_path)))
    return files_and_modified_time


@dataclass
class DownloadFileDetector:
    directory_path: str
    filename_pattern: str
    remaining_timeout_in_seconds: int = field(init=False)
    timeout_in_seconds: int = 100
    initial_files_and_modified_time: List[Tuple[str, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.remaining_timeout_in_seconds = self.timeout_in_seconds
        self.initial_files_and_modified_time = get_files_and_modification_time(self.directory_path, self.filename_pattern)
        logger_config.print_and_log_info(f"At init, {len(self.initial_files_and_modified_time)} files detected:{self.initial_files_and_modified_time}")

    def rescan_directory_for_changes(self) -> List[Tuple[str, float]]:
        current_files_and_modified_time = get_files_and_modification_time(self.directory_path, self.filename_pattern)
        logger_config.print_and_log_info(f"Current {len(current_files_and_modified_time)} files detected:{current_files_and_modified_time}")

        differences = list(set(current_files_and_modified_time) - set(self.initial_files_and_modified_time))
        logger_config.print_and_log_info(f"differences:{differences}")
        return differences

    def monitor_download(self) -> Optional[str]:
        download_event_handler = DownloadEventHandler(self.filename_pattern)
        observer = Observer()
        observer.schedule(download_event_handler, self.directory_path, recursive=False)
        observer.start()

        logger_config.print_and_log_info("Waiting download...")
        try:
            while not download_event_handler.file_detected and self.remaining_timeout_in_seconds > 0:
                time.sleep(1)
                self.remaining_timeout_in_seconds -= 1
                manual_scan_files_modified_name_and_timestamp = self.rescan_directory_for_changes()
                logger_config.print_and_log_info(f"Files downloaded found after manual scan:{manual_scan_files_modified_name_and_timestamp}")

                if len(manual_scan_files_modified_name_and_timestamp) == 1:
                    file_detected: Tuple[str, float] = manual_scan_files_modified_name_and_timestamp[0]
                    file_detected_name = file_detected[0]
                    logger_config.print_and_log_info(f"File download found after manual scan:{file_detected_name}")
                    return file_detected_name
        except KeyboardInterrupt:
            observer.stop()
            logger_config.print_and_log_warning("KeyboardInterrupt")
        observer.stop()
        observer.join()

        logger_config.print_and_log_info("End monitor_download")

        return download_event_handler.file_detected_path


# Fonction pour vérifier l'achèvement de téléchargement
@deprecated("Kept just in case")
def wait_for_download_to_complete_deprecated(download_dir: str, timeout: int = 120) -> None:
    seconds_passed = 0
    while seconds_passed < timeout:
        files = os.listdir(download_dir)
        # Vérifiez si un fichier temporaire est téléchargé
        if not any(file.endswith(".part") or file.endswith(".crdownload") for file in files):
            # Si aucun fichier temporaire trouvé, vérifiez si le fichier Excel est présent et complet
            logger_config.print_and_log_info(f"downloaded is in progress {(file.endswith(".part") or file.endswith(".crdownload") for file in files)}")

            if any(file.endswith(".xlsx") for file in files):
                logger_config.print_and_log_info(f"downloaded filee found:{(file.endswith(".xlsx") for file in files)}")
                break
        time.sleep(1)
        seconds_passed += 1
    else:
        raise Exception("Le téléchargement n'a pas pu être confirmé dans le délai imparti.")
