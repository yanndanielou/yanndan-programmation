# -*-coding:Utf-8 -*


import time


from logger import logger_config
from common import date_time_formats, multilanguage_management

import tkinter


def change_language(new_language:str)->None:
    multilanguage_mgt.current_language = new_language
    root.title(multilanguage_mgt.get_current_language_translation("application_title"))
    checkbox.config(multilanguage_mgt.get_current_language_translation('checkbox_1_label'))

logger_config.configure_logger_with_random_log_file_suffix("Mulitlanguage")
        
logger_config.print_and_log_info('Start application')



translations_json_file_path = "example_translation_file.json"
multilanguage_mgt = multilanguage_management.MultilanguageManagement(translations_json_file_path, "fr")
root = tkinter.Tk()
root.title("Multilanguage")
main_frame = tkinter.Frame(root)
checkbox = tkinter.Checkbutton(main_frame, text="Checkbox 1")
label = tkinter.Label(main_frame, text="Label 1")
entry = tkinter.Entry(main_frame, textvariable='entry 1')

phone = tkinter.StringVar()
option_home = tkinter.Radiobutton(main_frame, text='Home', variable=phone, value='home')
option_office = tkinter.Radiobutton(main_frame, text='Office', variable=phone, value='office')
option_cell = tkinter.Radiobutton(main_frame, text='Mobile', variable=phone, value='cell')

button = tkinter.Button(main_frame, text='button 1')


checkbox.grid(row= 0, column=0)
label.grid(row= 1, column=0)
entry.grid(row= 2, column=0)
option_home.grid(row= 3, column=0)
option_office.grid(row= 3, column=1)
option_cell.grid(row= 3, column=2)
button.grid(row= 4, column=0)

# Menu pour changer la langue
menu = tkinter.Menu(root)
root.config(menu=menu)

language_menu = tkinter.Menu(menu, tearoff=0)
menu.add_cascade(label="Language", menu=language_menu)

for lang in ["fr", "en"]:
    language_menu.add_command(label=lang.upper(), command=lambda l=lang: change_language(l))

main_frame.pack()
root.mainloop()

logger_config.print_and_log_info("End. Nominal end of application")
