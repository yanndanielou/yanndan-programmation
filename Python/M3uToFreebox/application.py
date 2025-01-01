# -*-coding:Utf-8 -*

from warnings import deprecated

import requests
import tqdm

import Dependencies.Logger.logger_config as logger_config
import Dependencies.Common.date_time_formats as date_time_formats

import m3u
import xspf

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_view import M3uToFreeboxMainView
import importlib

import io

import urllib.request
import urllib.error

import urllib.request
from urllib.error import URLError, HTTPError

class M3uToFreeboxApplication:
    """ Application """

    def __init__(self, mainview):

        self._m3u_library: m3u.M3uEntriesLibrary = m3u.M3uEntriesLibrary()

        self._main_view:'M3uToFreeboxMainView' = mainview

    def download_file_blocking_without_progress(self, file_destination_full_path:str, m3u_entry:m3u.M3uEntry, filename: str):
        logger_config.print_and_log_info("Start download of " + file_destination_full_path)
        url_open = urllib.request.urlopen(m3u_entry.link)
        meta = url_open.info()
        logger_config.print_and_log_info(f'File to download size {url_open.length}')
        logger_config.print_and_log_info(f"File to download meta content length {meta.get('Content-Length')}")

        try:    
            urlretrieve_result = urllib.request.urlretrieve(m3u_entry.link, file_destination_full_path)
        except urllib.error.URLError as e:
            print(e)
            #logger_config.print_and_log_info(e)
            pass
        except urllib.error.HTTPError as e:
            print(e)
            #logger_config.print_and_log_info(e)
            pass
        except urllib.error.ContentTooShortError as e:
            print(e)
            #logger_config.print_and_log_info(e)
            pass
        except OSError as e:
            print(e)
            #logger_config.print_and_log_info(e)
            pass
        except Exception as e:
            print(e)
            #logger_config.print_and_log_info(e)
            pass
        logger_config.print_and_log_info(f"Download ended. urlretrieve_result {urlretrieve_result}")

        #self.download_tqdm(m3u_entry.link, file_destination_full_path)



    def download_urllib_request_with_progress(self, url: str, filename: str):
        with urllib.request.urlopen(url) as Response:
            Length = Response.getheader('content-length')
            BlockSize = 1000000  # default value

            if Length:
                Length = int(Length)
                BlockSize = max(4096, Length // 20)

            print("UrlLib len, blocksize: ", Length, BlockSize)

            BufferAll = io.BytesIO()
            Size = 0
            while True:
                BufferNow = Response.read(BlockSize)
                if not BufferNow:
                    break
                BufferAll.write(BufferNow)
                Size += len(BufferNow)
                if Length:
                    Percent = int((Size / Length)*100)
                    print(f"download: {Percent}% {url}")

            print("Buffer All len:", len(BufferAll.getvalue()))

        with open(filename) as f: ## Excel File
            print(type(f))           ## Open file is TextIOWrapper
            bw=io.TextIOWrapper(BufferAll)   ## Conversion to TextIOWrapper
            print(type(bw))          ## Just to confirm 

    def download_tqdm(self, url: str, filename: str):
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

        
    def download_movie_file_by_id_str(self, destination_directory:str, m3u_entry_id:str):
        m3u_entry_id_int = int(m3u_entry_id)
        self.download_movie_file_by_id(destination_directory, m3u_entry_id_int)




    def download_movie_file_by_id(self, destination_directory:str, m3u_entry_id:int):
        m3u_entry:m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id)
        if m3u_entry.can_be_downloaded():
            file_destination_full_path = destination_directory + "\\" + m3u_entry.title_as_valid_file_name + m3u_entry.file_extension

            with open(file_destination_full_path, 'wb') as f:
                # Get Response From URL
                response = requests.get(m3u_entry.link, stream=True)
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
        m3u_entry_id_int = int(m3u_entry_id_str)
        m3u_entry:m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id_int)       
        m3u_entry.file_size = 105
        return True

    def load_m3u_entry_size_by_id_str(self, m3u_entry_id_str:str) -> bool:
        m3u_entry_id_int = int(m3u_entry_id_str)
        m3u_entry:m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id_int)       

        if m3u_entry.can_be_downloaded():
            try:
                with urllib.request.urlopen(m3u_entry.link) as url_open:
                    m3u_entry.file_size = url_open.length
                    return True
            except HTTPError as e:
                # do something
                logger_config.print_and_log_error(f'Error code: {e.code} for {m3u_entry}')
                m3u_entry.file_size = f'Error! {e}'
            except URLError as e:
                # do something
                logger_config.print_and_log_error(f'Error code: {e.code} for {m3u_entry}')
                m3u_entry.file_size = f'Error! {e}'

        else:
            m3u_entry.file_size = 'NA'
        
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
    
        
    def load_file(self, file_path):
        """ Load file """
        logger_config.print_and_log_info("Load file:" + file_path)

        

        m3u_file_parser =  m3u.M3uFileParser()
        for m3u_entry in m3u_file_parser.parse_file(file_path):
            self._m3u_library.add(m3u_entry)
        
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