SET JSON_FILE=%1
Echo JSON_FILE:%JSON_FILE%
timeout /t 30

C:\Produits\Python35\python.exe outil_extraction.py --json_config_file=%JSON_FILE%


timeout /t 150