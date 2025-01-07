# -*-coding:Utf-8 -*

#import pyconvert.pyconv

from logger import logger_config


class XspfFileContent:

    class Track:

        class Extension:

            def __init__(self, vlc_id = 0, application = "http://www.videolan.org/vlc/playlist/0") -> None:
                self._vlc_id = vlc_id
                self._application = application

        def __init__(self, location, duration = 9999) -> None:
            self._location = location
            self._duration = duration
            self._extension = XspfFileContent.Track.Extension()

        @property
        def location(self):
            return self._location

        @location.setter
        def location(self, value):
            self._location = value

        @property
        def duration(self):
            return self._duration

        @duration.setter
        def duration(self, value):
            self._duration = value

        @property
        def extension(self):
            return self._extension

        @extension.setter
        def extension(self, value):
            self._extension = value

    def __init__(self, title:str, location:str) -> None:
        self._title:str = title
        self._tracks:list[XspfFileContent.Track] = []
        self._tracks.append(XspfFileContent.Track(location))

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        self._tracks = value

    
    


class XspfFileCreator:
    """ Creator of xspf file """
    def __init__(self) -> None:
        pass
    
    def write(self, xspf_file_content:XspfFileContent, output_directory_path:str, output_file_name: str, print_result:bool = False) -> bool:
        """ Create xspf file """
        #xml_content = pyconvert.pyconv.convert2XML(xspf_file_content)
        #pretty_xml = xml_content.toprettyxml()
        #print(pretty_xml)
        
        full_path = output_directory_path + "\\" + output_file_name
        with open(full_path, 'w', encoding="utf-8") as f:
            if print_result:
                logger_config.print_and_log_info("File created: " + full_path)
            
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">\n')
            f.write('\t<title>' + xspf_file_content.title + '</title>\n')
            f.write('\t<trackList>\n')
            f.write('\t\t<track>\n')
            f.write('\t\t\t<location>' + xspf_file_content.tracks[0].location + '</location>\n')
            f.write('\t\t\t<duration>8981</duration>\n')
            f.write('\t\t\t<extension application="http://www.videolan.org/vlc/playlist/0">\n')
            f.write('\t\t\t\t<vlc:id>0</vlc:id>\n')
            f.write('\t\t\t</extension>\n')
            f.write('\t\t</track>\n')
            f.write('\t</trackList>\n')
            f.write('</playlist>\n')
            
            return True
        
        return False

                  
    
