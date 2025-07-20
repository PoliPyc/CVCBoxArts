#!/bin/env bash

pyinstaller --distpath=dist \
            --add-data=./data/:. \
            --contents-directory=data \
            --hidden-import=PIL._tkinter_finder \
            --name=ViiCovers \
            app/main.py
