@CALL SET_PYTHON_HOME.bat


@call :INSTALL_PYTHON_LIB Spire.Doc
@call :INSTALL_PYTHON_LIB psutil
@call :INSTALL_PYTHON_LIB pyttsx3  
@call :INSTALL_PYTHON_LIB pygame 
@call :INSTALL_PYTHON_LIB pypiwin32 
@call :INSTALL_PYTHON_LIB xlwings
@call :INSTALL_PYTHON_LIB watchdog
@call :INSTALL_PYTHON_LIB imageio-ffmpeg
@call :INSTALL_PYTHON_LIB moviepy
@call :INSTALL_PYTHON_LIB Pillow
@call :INSTALL_PYTHON_LIB pyxtream[REST_API]
@call :INSTALL_PYTHON_LIB pyxtream
@call :INSTALL_PYTHON_LIB pytest-timeout
@call :INSTALL_PYTHON_LIB stubs
@call :INSTALL_PYTHON_LIB selenium
@call :INSTALL_PYTHON_LIB bs4
@call :INSTALL_PYTHON_LIB mplcursors
@call :INSTALL_PYTHON_LIB mpld3
rem call %PYTHON_HOME%\python.exe  -m pip install --config-settings="--global-option=build_ext" --config-settings="--global-option=-IC:\Program Files\Graphviz\include" --config-settings="--global-option=-LC:\Program Files\Graphviz\lib" pygraphviz
@call :INSTALL_PYTHON_LIB Graphviz
rem @call :INSTALL_PYTHON_LIB pygraphviz
@call :INSTALL_PYTHON_LIB networkx
@call :INSTALL_PYTHON_LIB openpyxl
@call :INSTALL_PYTHON_LIB pandas
@call :INSTALL_PYTHON_LIB parameterized
@call :INSTALL_PYTHON_LIB pytest-cov
@call :INSTALL_PYTHON_LIB unidecode
@call :INSTALL_PYTHON_LIB humanize
@call :INSTALL_PYTHON_LIB langdetect
@call :INSTALL_PYTHON_LIB Langid
@call :INSTALL_PYTHON_LIB py3langid
@call :INSTALL_PYTHON_LIB nltk
@call :INSTALL_PYTHON_LIB requests
@call :INSTALL_PYTHON_LIB tqdm
@call %PYTHON_HOME%\python.exe -m pip install --upgrade nltk
@call :INSTALL_PYTHON_LIB numpy
@call :INSTALL_PYTHON_LIB pyconvert
rem does not fix lazyxml @call :INSTALL_PYTHON_LIB utils
rem does not work @call :INSTALL_PYTHON_LIB lazyxml
@call :INSTALL_PYTHON_LIB xspf-lib
@call :INSTALL_PYTHON_LIB mysql
@call :INSTALL_PYTHON_LIB mysql-connector
@call :INSTALL_PYTHON_LIB pycairo
@call :INSTALL_PYTHON_LIB PyGObject
@call :INSTALL_PYTHON_LIB mypy
@call :INSTALL_PYTHON_LIB m3uspiff
@call :INSTALL_PYTHON_LIB ffmpeg
@call :INSTALL_PYTHON_LIB ffprobe 
@call :INSTALL_PYTHON_LIB customtkinter
@call :INSTALL_PYTHON_LIB matplotlib
@call :INSTALL_PYTHON_LIB ipywidgets


@GOTO :END_OF_FILE


:INSTALL_PYTHON_LIB
@Title install python library %1
@Echo install python library %1
call %PYTHON_HOME%\python.exe -m pip install %1
@EXIT /B 0


:END_OF_FILE

@timeout /t 100
