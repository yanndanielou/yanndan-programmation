# -*-coding:Utf-8 -*
import shutil
import fnmatch
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple
from warnings import deprecated

from logger import logger_config
from watchdog.events import DirCreatedEvent, DirModifiedEvent, FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from common import file_utils


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


def get_files_and_modification_time(directory_path: str, filename_pattern: str) -> List[Tuple[str, datetime]]:
    return file_utils.get_files_modification_time(file_utils.get_files_by_directory_and_file_name_mask(directory_path=directory_path, filename_pattern=filename_pattern))


@dataclass
class DownloadFileDetector:

    @dataclass
    class FileMoveAfterDownloadAction:
        final_path: str
        retry_in_case_of_error: bool = False

    directory_path: str
    filename_pattern: str
    remaining_timeout_in_seconds: int = field(init=False)
    timeout_in_seconds: int = 100
    initial_files_and_modified_time: List[Tuple[str, datetime]] = field(default_factory=list)
    file_move_after_download_action: Optional[FileMoveAfterDownloadAction] = None

    def __post_init__(self) -> None:
        self.remaining_timeout_in_seconds = self.timeout_in_seconds
        self.initial_files_and_modified_time = get_files_and_modification_time(self.directory_path, self.filename_pattern)
        logger_config.print_and_log_info(f"At init, {len(self.initial_files_and_modified_time)} {self.filename_pattern} files detected:{self.initial_files_and_modified_time}")

    def rescan_directory_for_changes(self) -> List[Tuple[str, datetime]]:
        current_files_and_modified_time = get_files_and_modification_time(self.directory_path, self.filename_pattern)
        logger_config.print_and_log_info(f"Current {len(current_files_and_modified_time)} files {self.filename_pattern} detected:{current_files_and_modified_time}")

        differences = list(set(current_files_and_modified_time) - set(self.initial_files_and_modified_time))
        logger_config.print_and_log_info(f"differences:{differences}")
        return differences

    def wait_for_file_size_is_stable(self, file_path: str) -> None:
        # initial_file_modification_time = os.path.getmtime(file_path)
        initial_file_size = os.path.getsize(file_path)
        logger_config.print_and_log_info(f"Initial size of {file_path} is {initial_file_size }")

        while os.path.getsize(file_path) == 0:
            logger_config.print_and_log_info(f"Size of {file_path} is still null. Keep waiting")
            time.sleep(1)

        if initial_file_size == 0:
            logger_config.print_and_log_info(f"Size of {file_path} is no more null")

        previous_file_size = os.path.getsize(file_path)

        while True:
            time.sleep(1)
            current_file_size = os.path.getsize(file_path)
            if current_file_size == previous_file_size:
                logger_config.print_and_log_info(f"Size of {file_path} is stable to {current_file_size}. Do not wait anymore")
                return

            logger_config.print_and_log_info(f"Size of {file_path} changed from {previous_file_size} to {current_file_size}. Keep waiting")
            previous_file_size = current_file_size

    def monitor_download(self) -> Optional[str]:
        download_event_handler = DownloadEventHandler(self.filename_pattern)
        observer = Observer()
        observer.schedule(download_event_handler, self.directory_path, recursive=False)
        observer.start()

        logger_config.print_and_log_info(f"Waiting download {self.filename_pattern}...")
        try:
            while not download_event_handler.file_detected and self.remaining_timeout_in_seconds > 0:
                time.sleep(1)
                self.remaining_timeout_in_seconds -= 1
                manual_scan_files_modified_name_and_timestamp = self.rescan_directory_for_changes()
                logger_config.print_and_log_info(
                    f"{self.remaining_timeout_in_seconds} remaining seconds (already {self.timeout_in_seconds-self.remaining_timeout_in_seconds} s waited): Files downloaded found after manual scan:{manual_scan_files_modified_name_and_timestamp}"
                )

                if len(manual_scan_files_modified_name_and_timestamp) == 1:
                    file_detected = manual_scan_files_modified_name_and_timestamp[0]
                    file_detected_path = file_detected[0]
                    logger_config.print_and_log_info(f"File download found after manual scan:{file_detected_path}")
                    self.wait_for_file_size_is_stable(file_path=file_detected_path)

                    if self.file_move_after_download_action:
                        logger_config.print_and_log_info(f"File downloaded : {file_detected_path}, will be moved to {self.file_move_after_download_action.final_path}")
                        move_success = False

                        if self.file_move_after_download_action.retry_in_case_of_error:
                            while not move_success:
                                try:
                                    shutil.move(file_detected_path, self.file_move_after_download_action.final_path)
                                    move_success = True
                                except PermissionError as perm_error:
                                    # logger_config.print_and_log_exception(permErr)
                                    logger_config.print_and_log_error("File " + file_detected_path + " is used. Relase it")
                                    time.sleep(1)
                        else:
                            shutil.move(file_detected_path, self.file_move_after_download_action.final_path)

                        return self.file_move_after_download_action.final_path

                    return file_detected_path
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
