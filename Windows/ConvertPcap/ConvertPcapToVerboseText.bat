SETLOCAL EnableDelayedExpansion


@SET INPUT_PCAP_FILE_WITH_EXTENSION=%1

@for %%A IN (%INPUT_PCAP_FILE_WITH_EXTENSION%) DO (@SET input_file_extension="%%~xA")
@echo input_file_extension:%input_file_extension%

@for %%A IN (%INPUT_PCAP_FILE_WITH_EXTENSION%) DO (@SET input_file_name_without_extension=!input_file_name_without_extension!" ""%%~nA")
@set input_file_name_without_extension=%input_file_name_without_extension:"=%
@for /f "tokens=* delims= " %%a in ("%input_file_name_without_extension%") do @set input_file_name_without_extension=%%a
@echo input_file_name_without_extension:%input_file_name_without_extension%

@SET output_file_name=%input_file_name_without_extension%.txt
@echo output_file_name:%output_file_name%

@echo Convert file %INPUT_PCAP_FILE_WITH_EXTENSION% to "%output_file_name%"


call "%ProgramFiles%\Wireshark\tshark.exe" -V -r %INPUT_PCAP_FILE_WITH_EXTENSION% > "%output_file_name%"


@timeout /t 100
