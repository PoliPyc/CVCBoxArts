
import PySimpleGUI as sg
from PIL import Image
import os

import base64
from io import BytesIO

home_catalog = os.path.expanduser('~') + "/projects/CVCBoxArts/input"
filetypes = (('all images', '*.png *.jpg *.jpeg'),)
gametypes = ('NES', 'SNES', 'N64', 'GENESIS', 'TGX16')
boxtypes = ('Front', 'Back', 'Full', '3D')

class BoxArt():
    def __init__(self, cover_path: str = None, gametype: str = None, boxtype: str = None) -> None:
        self.cover_path = cover_path
        self.gametype = gametype
        self.boxtype = boxtype
        self.file = None
    
    def generate_new_boxart(self) -> Image:
        cover = Image.open(self.cover_path)
        banner = Image.open('/home/poli/projects/CVCBoxArts/data/banner_front_nes.png')
        boxart = cover.copy()
        boxart.paste(banner)
        return boxart

    @staticmethod
    def convert_image_to_base64(image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue())
def run():
    
    sg.theme("DarkAmber")
    layout = [
        [[sg.Text("Select cover: ")] + [sg.FileBrowse(initial_folder=home_catalog, file_types=filetypes, enable_events=True, key="selected_cover", target=(0, 1))]],
        [[sg.Text("Select gametype: ")] + [sg.OptionMenu(gametypes, default_value=gametypes[0], key='gametype')]],
        [[sg.Text("Select boxtype: ")] + [sg.OptionMenu(boxtypes, default_value=boxtypes[0], key='boxtype')]],
        [sg.Text("Preview:")],
        [sg.Image(key="preview_image")],
        [sg.Button("Save"), sg.Button("Cancel")],
        [sg.StatusBar("code: polipyc, graphics: krohmal © 2023")]
    ]

    window = sg.Window("CVCBoxArts v.0.1", layout, finalize=True)

    while True:
        event, values = window.read()
        if ( event == "selected_cover"):
            print('wybrano okładkę')
            print(values)
            new_boxart = BoxArt(values['selected_cover'], values['gametype'], values['boxtype'])
            data = BoxArt.convert_image_to_base64(new_boxart.generate_new_boxart())
            print(data)
            window['preview_image'].update(source=data)
        if (
            event == sg.WIN_CLOSED or event == "Cancel"
        ):  # if user closes window or clicks cancel
            break

    window.close()


if __name__ == "__main__":
    run()
