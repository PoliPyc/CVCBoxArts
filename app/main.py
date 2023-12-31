import base64
import os
from io import BytesIO
from pathlib import Path

import PySimpleGUI as sg
from PIL import Image, ImageTk

USBLOADER_COVER_WIDTH = 160

root_path = Path(__file__).resolve().parent
data_path = Path(str(root_path) + "/../data").resolve()
home_catalog = os.path.expanduser("~") + "/projects/CVCBoxArts/input"
filetypes = (("all images", "*.png *.jpg *.jpeg"),)
gametypes = ("NES", "SNES", "N64", "GENESIS", "TGX16")
boxtypes = ("Front", "Back", "Full", "3D")


class BoxArt:
    def __init__(
        self,
        cover_path: str = None,
        gametype: str = None,
        boxtype: str = None,
        name: str = None,
    ) -> None:
        self.cover_path = cover_path
        self.gametype = gametype
        self.boxtype = boxtype
        self.name = None
        self.boxart = None

    def generate_new_boxart(self) -> Image:
        def resize_to_width(image, width):
            wpercent = width / float(image.size[0])
            hsize = int((float(image.size[1]) * float(wpercent)))
            return image.resize((width, hsize), Image.LANCZOS)

        try:
            cover = Image.open(self.cover_path)
        except Exception as e:
            print(e)
            return

        banner = self._get_banner()
        self.boxart = cover.copy()
        self.name = cover.filename
        if banner.width > self.boxart.width:
            print("Resizing banner")
            banner = resize_to_width(banner, self.boxart.width)
        else:
            print("resizing cover")
            self.boxart = resize_to_width(self.boxart, banner.width)

        self.boxart.paste(banner, (0, 0), banner)
        self.boxart = resize_to_width(self.boxart, USBLOADER_COVER_WIDTH)
        # boxart.save("/home/poli/projects/CVCBoxArts/output/test.png", quality=95)
        # print("zapisalo sie")
        return self.boxart

    def _get_banner(self) -> Image:
        return Image.open(
            str(data_path) + f"/banner_{self.boxtype}_{self.gametype}_hq.png"
        )

    @staticmethod
    def convert_image_to_base64(image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue())


def run():
    sg.theme("DarkTeal11")
    layout = [
        [
            [sg.Text("Select cover: ", key="cover_label")]
            + [
                sg.FileBrowse(
                    initial_folder=home_catalog,
                    file_types=filetypes,
                    enable_events=True,
                    key="selected_cover",
                    target=(0, 1),
                )
            ]
        ],
        [
            [sg.Text("Select gametype: ")]
            + [
                sg.Combo(
                    gametypes,
                    default_value=gametypes[0],
                    enable_events=True,
                    readonly=False,
                    key="gametype",
                )
            ]
        ],
        [sg.Text("Select boxtype: ")],
        [
            [sg.Checkbox("Front", default=True, key="box-front")]
            + [sg.Checkbox("Back", key="box-back")]
            + [sg.Checkbox("Full", key="box-full")]
            + [sg.Checkbox("3D", key="box-3d")]
        ],
        [sg.Text("Preview:")],
        [sg.Image(key="preview_image")],
        [sg.Button("Save"), sg.Button("Cancel")],
        [
            sg.StatusBar(
                "code: polipyc, graphics: krohmal © 2023",
                relief=sg.RELIEF_FLAT,
                justification="right",
            )
        ],
    ]

    window = sg.Window("CVCBoxArts v.0.2", layout, finalize=True)

    while True:
        event, values = window.read()
        window["cover_label"].expand(expand_x=True)  # broken
        if event in ("selected_cover", "gametype"):
            print("wybrano okładkę")
            print(values)
            if values["box-front"]:
                boxtypes = "front"
            new_boxart = BoxArt(values["selected_cover"], values["gametype"], boxtypes)
            try:
                data = ImageTk.PhotoImage(new_boxart.generate_new_boxart())
                window["preview_image"].update(data=data)
            except Exception as e:
                print(e)

        if event == "Save":
            filename = sg.tk.filedialog.asksaveasfilename(
                defaultextension="png",
                filetypes=filetypes,
                initialdir=home_catalog,
                initialfile=new_boxart.name,  # Option added here
                parent=window.TKroot,
                title="Save As",
            )
            new_boxart.boxart.save(filename)
        if (
            event == sg.WIN_CLOSED or event == "Cancel"
        ):  # if user closes window or clicks cancel
            break

    window.close()


if __name__ == "__main__":
    run()
