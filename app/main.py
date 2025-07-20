"""Custom cover generator for Virtual Console injections designed for use with USBLoaderGX cover system."""

import base64
import os
from io import BytesIO
from pathlib import Path
from typing import Optional

import FreeSimpleGUI as sg # type: ignore
from PIL import Image, ImageTk # type: ignore

__APP_NAME = "ViiCovers"
__VERSION = "0.2.3"

USBLOADER_COVER_FRONT_WIDTH = 160
USBLOADER_COVER_FRONT_HEIGHT = 224

FIT_OPTIONS = [
    {"text": "fit to width", "key": "fit_w", "value": "width"},
    {"text": "fit to height", "key": "fit_h", "value": "height"},
]

root_path = Path(__file__).resolve().parent
data_path = Path(str(root_path) + "/../data").resolve()
home_catalog = os.path.expanduser("~")
filetypes = (("all images", "*.png *.jpg *.jpeg"),)
gametypes = ("NES", "SNES", "N64", "GENESIS", "TGX16")
boxtypes = ("Front", "Back", "Full", "3D")


class BoxArt:
    """Class for creating and processing game box art with banners."""

    def __init__(
        self,
        cover_path: Optional[str] = None,
        gametype: Optional[str] = None,
        boxtype: Optional[str] = None,
        fit: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """Initialize a BoxArt object with the given parameters.

        Args:
            cover_path: Path to the cover image file.
            console_type: Game console type (e.g., NES, SNES).
            box_type: Box art type (e.g., Front, Back).
            fit: Scaling mode (width or height).
        """
        self.cover_path = cover_path
        self.gametype = gametype
        self.boxtype = boxtype
        self.fit = fit
        self.name = None
        self.boxart: Image = None
        self.cover = Image.new(
            "RGB", (USBLOADER_COVER_FRONT_WIDTH, USBLOADER_COVER_FRONT_HEIGHT)
        )

    def generate_new_boxart(self) -> Image.Image:
        """Create a new box art image with an overlaid banner.

        Returns:
            PIL.Image object with the processed box art or None if an error occurs.

        Raises:
            ValueError: If input parameters are invalid.
            FileNotFoundError: If cover or banner file is not found.
        """

        def resize_to_width(image, width):
            wpercent = width / float(image.size[0])
            hsize = int((float(image.size[1]) * float(wpercent)))
            return image.resize((width, hsize), Image.LANCZOS)

        def resize_to_height(image, height):
            hpercent = height / float(image.size[1])
            wsize = int((float(image.size[0]) * float(hpercent)))
            return image.resize((wsize, height), Image.LANCZOS)

        try:
            if not self.cover_path or not Path(self.cover_path).is_file():
                raise ValueError("Invalid or missing cover image path")
            if self.gametype not in gametypes:
                raise ValueError(f"Invalid console type: {self.gametype}")
            if self.boxtype not in boxtypes:
                raise ValueError(f"Invalid box type: {self.boxtype}")
            # if self.fit not in FIT_OPTIONS:
            # raise ValueError(f"Invalid fit option: {self.fit}")
            self.boxart = Image.open(self.cover_path)

        except (ValueError, FileNotFoundError) as e:
            sg.popup_error(f"Error creating box art: {e}", title="Error")
            return None
        except Exception as e:
            sg.popup_error(f"Unexpected error: {e}", title="Error")
            return None

        banner = self._get_banner()
        self.name = self.boxart.filename
        print("Resizing banner")
        banner = resize_to_width(banner, USBLOADER_COVER_FRONT_WIDTH)
        print("resizing cover")
        if self.fit == "width":
            self.boxart = resize_to_width(self.boxart, USBLOADER_COVER_FRONT_WIDTH)
        elif self.fit == "height":
            self.boxart = resize_to_height(self.boxart, USBLOADER_COVER_FRONT_HEIGHT)

        self.cover.paste(self.boxart, (0, 0))
        self.cover.paste(banner, (0, 0), banner)
       
        return self.cover

    def _get_banner(self) -> Image:
        return Image.open(
            str(data_path) + f"/banner_{self.boxtype}_{self.gametype}_hq.png"
        )

    @staticmethod
    def convert_image_to_base64(image) -> bytes:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue())


def create_layout() -> list:
    """Create the GUI layout for the application.

    Returns:
        List defining the GUI layout.
    """
    return [
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
        # TODO:
        [sg.Text("Select boxtype: ")],
        [
            [sg.Checkbox("Front", default=True, key="box-front")]
            #     + [sg.Checkbox("Back", key="box-back")]
            #     + [sg.Checkbox("Full", key="box-full")]
            #     + [sg.Checkbox("3D", key="box-3d")]
        ],
        [
            [
                sg.Radio(
                    option["text"],
                    "fit",
                    default=(i == 0),
                    enable_events=True,
                    key=option["key"],
                )
            ]
            for i, option in enumerate(FIT_OPTIONS)
        ],
        [sg.Text("Preview:")],
        [sg.Image(key="preview_image")],
        [sg.Button("Save"), sg.Button("Cancel")],
        [
            sg.StatusBar(
                "code: polipyc, graphics: krohmal © 2025",
                relief=sg.RELIEF_FLAT,
                justification="right",
            )
        ],
    ]


def run():
    sg.theme("DarkTeal11")

    window = sg.Window(__APP_NAME + " v." + __VERSION, create_layout(), finalize=True)

    while True:
        event, values = window.read()
        window["cover_label"].expand(expand_x=True)  # broken
        print(event)
        if event in ("selected_cover", "gametype") or event.startswith("fit_"):
            print("wybrano okładkę")
            print(values)
            if values["box-front"]:
                boxtypes = "Front"
            for option in FIT_OPTIONS:
                if values[option["key"]]:
                    fit = option["value"]
            new_boxart = BoxArt(
                values["selected_cover"], values["gametype"], boxtypes, fit
            )
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
