# -*-coding:Utf-8 -*

from warnings import deprecated

import requests
import tqdm

from logger import logger_config
from common import file_size_utils

import m3u
import xspf

import param

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_view import M3uToFreeboxMainView
import importlib

import io

import urllib.request
import urllib.error

from urllib.error import URLError, HTTPError, ContentTooShortError

class M3uToFreeboxApplication:
    """ Application """

    def __init__(self, mainview:'M3uToFreeboxMainView')->None:

        self._m3u_library: m3u.M3uEntriesLibrary = m3u.M3uEntriesLibrary()

        self._main_view:'M3uToFreeboxMainView' = mainview

    def download_file_blocking_without_progress(self, file_destination_full_path:str, m3u_entry:m3u.M3uEntry, filename: str)->None:
        """ download_file_blocking_without_progress """
        logger_config.print_and_log_info("Start download of " + file_destination_full_path)
        url_open = urllib.request.urlopen(m3u_entry.link)
        meta = url_open.info()
        logger_config.print_and_log_info(f'File to download size {url_open.length}')
        logger_config.print_and_log_info(f"File to download meta content length {meta.get('Content-Length')}")

        try:    
            urlretrieve_result = urllib.request.urlretrieve(m3u_entry.link, file_destination_full_path)
        except HTTPError as e:
            print(e)
            #logger_config.print_and_log_info(e)
        except ContentTooShortError as e:
            print(e)
            #logger_config.print_and_log_info(e)
        except URLError as e:
            print(e)
            #logger_config.print_and_log_info(e)
        except OSError as e:
            print(e)
            #logger_config.print_and_log_info(e)
        except Exception as e:
            print(e)
            #logger_config.print_and_log_info(e)

        logger_config.print_and_log_info(f"Download ended. urlretrieve_result {urlretrieve_result}")

        #self.download_tqdm(m3u_entry.link, file_destination_full_path)



    def download_urllib_request_with_progress(self, url: str, filename: str)-> None:
        """ download_urllib_request_with_progress """
        with urllib.request.urlopen(url) as response:
            length = response.getheader('content-length')
            block_size = 1000000  # default value

            if length:
                length = int(length)
                block_size = max(4096, length // 20)

            print("UrlLib len, blocksize: ", length, block_size)

            buffer_all = io.BytesIO()
            size = 0
            while True:
                buffer_now = response.read(block_size)
                if not buffer_now:
                    break
                buffer_all.write(buffer_now)
                size += len(buffer_now)
                if length:
                    Percent = int((size / length)*100)
                    print(f"download: {Percent}% {url}")

            print("Buffer All len:", len(buffer_all.getvalue()))

        with open(filename) as f: ## Excel File
            print(type(f))           ## Open file is TextIOWrapper
            bw=io.TextIOWrapper(buffer_all)   ## Conversion to TextIOWrapper
            print(type(bw))          ## Just to confirm

    def download_tqdm(self, url: str, filename: str)->None:
        """ download_tqdm """
        with open(filename, 'wb') as f:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))

                # tqdm has many interesting parameters. Feel free to experiment!
                tqdm_params = {
                    'desc': url,
                    'total': total,
                    'miniters': 1,
                    'unit': 'B',
                    'unit_scale': True,
                    'unit_divisor': 1024,
                }
                with tqdm.tqdm(**tqdm_params) as pb:
                    for chunk in r.iter_content(chunk_size=8192):
                        pb.update(len(chunk))
                        f.write(chunk)

        
    def download_movie_file_by_id_str(self, destination_directory:str, m3u_entry_id:str)->None:
        """ download_movie_file_by_id_str """
        m3u_entry_id_int = int(m3u_entry_id)
        self.download_movie_file_by_id(destination_directory, m3u_entry_id_int)




    def download_movie_file_by_id(self, destination_directory:str, m3u_entry_id:int) -> None:
        """ download_movie_file_by_id """
        m3u_entry:m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id)
        if m3u_entry.can_be_downloaded():
            file_destination_full_path = destination_directory + "\\" + m3u_entry.title_as_valid_file_name + m3u_entry.file_extension

            with open(file_destination_full_path, 'wb') as f:
                # Get Response From URL
                response = requests.get(m3u_entry.link, stream=True, timeout=5)
                # Find Total Download Size
                total_length = response.headers.get('content-length')
                logger_config.print_and_log_info(f'total_length: {total_length}')
                # Number Of Iterations To Write To The File
                #self.download_urllib_request_with_progress(m3u_entry.link, file_destination_full_path)
                #chunk_size = 4096

                self.download_file_blocking_without_progress(file_destination_full_path,m3u_entry,file_destination_full_path)

            logger_config.print_and_log_info("Download ended")

        else:
            logger_config.print_and_log_error(str(m3u_entry) + " cannot be downloaded")


    @deprecated("Just for tests")
    def load_fake(self, m3u_entry_id_str:str) -> bool:
        """ load_fake """
        m3u_entry_id_int = int(m3u_entry_id_str)
        m3u_entry:m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id_int)       
        m3u_entry.set_last_computed_file_size(105)
        return True

    def load_m3u_entry_size_by_id_str(self, m3u_entry_id_str:str) -> bool:
        """ load_m3u_entry_size_by_id_str """
        m3u_entry_id_int = int(m3u_entry_id_str)
        m3u_entry:m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id_int)       

        if m3u_entry.can_be_downloaded():
            result, length_or_error = file_size_utils.get_url_file_size(m3u_entry.link)

            if result:
                m3u_entry.set_last_computed_file_size(file_size_utils.convert_bits_to_human_readable_size(length_or_error))
                return True

            else:
                logger_config.print_and_log_error(f'Error code: {length_or_error} for {m3u_entry}')
                m3u_entry.last_error_when_trying_to_retrieve_size = f'Error! {length_or_error}'
        
        return False

    def create_xspf_file_by_id_str(self, destination_directory:str, m3u_entry_id:str):
        m3u_entry_id_int = int(m3u_entry_id)
        self.create_xspf_file_by_id(destination_directory, m3u_entry_id_int)
        
    def create_xspf_file_by_id(self, destination_directory:str, m3u_entry_id:int):
        
        m3u_entry:m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id)

        xspf_file_content = xspf.XspfFileContent(m3u_entry.cleaned_title, m3u_entry.link)
        xsp_file_creator = xspf.XspfFileCreator()
        xsp_file_creator.write(xspf_file_content,destination_directory, m3u_entry.title_as_valid_file_name + ".xspf", True)
        
    def reset_library(self):
        self._m3u_library = m3u.M3uEntriesLibrary()
    
        
    def load_file(self, file_path, save_path_of_m3u_file:bool=True):
        """ Load file """
        logger_config.print_and_log_info("Load file:" + file_path)

        

        m3u_file_parser =  m3u.M3uFileParser()
        for m3u_entry in m3u_file_parser.parse_file(file_path):
            self._m3u_library.add(m3u_entry)
         
        if save_path_of_m3u_file:   
            with open(param.PATH_OF_FILE_LISTING_LAST_M3U_FILE_LOADED, 'w', encoding="utf-8") as file_listing_last_m3u_file_loaded:
                file_listing_last_m3u_file_loaded.write(f"{file_path}")

    def load_last_loaded_m3u_file(self)->bool:
        """ load_last_loaded_m3u_file """
        try:
            with open(param.PATH_OF_FILE_LISTING_LAST_M3U_FILE_LOADED, 'r', encoding="utf-8") as file_listing_last_m3u_file_loaded:
                content = file_listing_last_m3u_file_loaded.read()
                logger_config.print_and_log_info(f'Last loaded m3u file:{content}')
                self.load_file(content, False)
                return True
        
        except FileNotFoundError:
            logger_config.print_and_log_info(f'Could not open file:{param.PATH_OF_FILE_LISTING_LAST_M3U_FILE_LOADED}')
            return False
        
    @property
    def m3u_library(self) -> m3u.M3uEntriesLibrary :
        return self._m3u_library

    @m3u_library.setter
    def m3u_library(self, value:m3u.M3uEntriesLibrary):
        self._m3u_library = value

if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()