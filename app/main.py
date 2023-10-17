
import PySimpleGUI as sg
from PIL import ImageGrab

gametypes = ('NES', 'SNES', 'N64', 'GENESIS', 'TGX16')
boxtypes = ('Front', 'Back', 'Full', '3D')

def run():
    
    sg.theme("DarkAmber")
    layout = [
        [[sg.Text("Select cover: ")] + [sg.FileBrowse()]],
        [[sg.Text("Select gametype: ")] + [sg.OptionMenu(gametypes, default_value=gametypes[0])]],
        [[sg.Text("Select boxtype: ")] + [sg.OptionMenu(boxtypes, default_value=boxtypes[0])]],
        [sg.Text("Preview:")],
        [
            sg.Graph(
                canvas_size=(200, 400),
                graph_bottom_left=(0, 0),
                graph_top_right=(200, 400),
                background_color="white",
                enable_events=True,
                key="preview",
            )
        ],
        [sg.Button("Save"), sg.Button("Cancel")],
        [sg.StatusBar("code: polipyc, graphics: krohmal © 2023")]
    ]

    window = sg.Window("CVCBoxArts v.0.1", layout, finalize=True)

    while True:
        event, values = window.read()
        
        if (
            event == sg.WIN_CLOSED or event == "Cancel"
        ):  # if user closes window or clicks cancel
            break

    window.close()


if __name__ == "__main__":
    run()
