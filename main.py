import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
import sv_ttk
from download import download
import threading

def download_thread(
        url: str, savepath: str, videoQuality: str, root: tk.Tk, font: list,
        getSubs: bool, getThumb: bool, onlyAudio: bool, getInfo: bool
    ) -> None:
    threading.Thread(target=download, args=(
        url, savepath, videoQuality, root, font, getSubs, getThumb, onlyAudio, getInfo
    )).start()

def open_file(entry: tk.StringVar):
   folder = askdirectory()
   print(folder)
   entry.set(folder)

def toggle(elements: list[tk.Checkbutton], places: list[list[int]], onOff: bool) -> None:
    for elem in range(len(elements)):
        if not onOff:
            elements[elem].grid(row=places[elem][0], column=places[elem][1])
        else:
            elements[elem].grid_remove()

root=tk.Tk()
root.geometry("600x400")
root.title("YoutubeDownload v1.0.0-Alpha")
FONT = ('calibre', 10, 'bold')
 
url_input      = tk.StringVar()
filepath_input = tk.StringVar()
video_quality  = tk.StringVar()
getSubs        = tk.BooleanVar()
getThumb       = tk.BooleanVar()
audioOnly      = tk.BooleanVar()
extraInfo      = tk.BooleanVar()

video_quality_options = [
    '144p',
    "240p",
    "360p",
    "720p",
    "1080p",
    "1440p",
    "2160p"
]

url_label = tk.Label(root, text = 'Video URL: ', font=FONT)
url_entry = tk.Entry(root, textvariable=url_input, width=60)

filepath_label  = tk.Label(root, text = 'Save Path: ', font=FONT)
filepath_entry  = tk.Entry(root, textvariable=filepath_input, width=60)
filepath_button = ttk.Button(root, text="Browse", command=lambda: open_file(filepath_input))

video_quality_label = tk.Label(root, text = 'Video Quality: ', font=FONT)
video_quality_menu = tk.OptionMenu(root, video_quality, *video_quality_options)
video_quality.set("720p")

subs_checkbox = tk.Checkbutton(
     root, text="Subtitles", 
     variable=getSubs, 
     offvalue=False, 
     onvalue=True
)
#subs_checkbox.config(selectcolor="black")

thumb_checkbox = tk.Checkbutton(
     root, text="Thumbnail", 
     variable=getThumb, 
     offvalue=False, 
     onvalue=True
)
#thumb_checkbox.config(selectcolor="black")

extraInfo_checkbox = tk.Checkbutton(
     root, text="Extra Info", 
     variable=extraInfo, 
     offvalue=False, 
     onvalue=True
)
#extraInfo_checkbox.config(selectcolor="black")

download_button = ttk.Button(
    root, text="Download", 
    command=lambda: download_thread(
        url_input.get(),
        filepath_input.get(),
        video_quality.get(),
        root, FONT, 
        getSubs.get(), getThumb.get(),
        audioOnly.get(), extraInfo.get()
    )
)

audioOnly_checkbox = tk.Checkbutton(
     root, text="Audio only", 
     variable=audioOnly, 
     offvalue=False, 
     onvalue=True,
     command=lambda: toggle(
         [thumb_checkbox, subs_checkbox, video_quality_label, video_quality_menu],
         [[3, 2],         [3, 1],        [2, 0],              [2, 1]],
         audioOnly.get()
     )
)
#audioOnly_checkbox.config(selectcolor="black")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

url_label.grid           (row=0, column=0)
url_entry.grid           (row=0, column=1)
 
filepath_label.grid      (row=1, column=0)
filepath_entry.grid      (row=1, column=1)
filepath_button.grid     (row=1, column=2)
 
video_quality_label.grid (row=2, column=0)
video_quality_menu.grid  (row=2, column=1)
 
audioOnly_checkbox.grid  (row=3, column=0)

subs_checkbox.grid       (row=3, column=1)

thumb_checkbox.grid      (row=3, column=2)

extraInfo_checkbox.grid  (row=4, column=0)

download_button.grid     (row=5, column=0)

#sv_ttk.set_theme("dark")
root.mainloop()