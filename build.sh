pyinstaller --distpath=dist --add-data=./data/:. --contents-directory=data --hidden-import=PIL._tkinter_finder app/main.py
