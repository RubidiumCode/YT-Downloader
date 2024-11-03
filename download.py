from pytubefix import YouTube
from pytubefix import Playlist
from pytubefix.cli import on_progress
import tkinter as tk
from tkinter import ttk
from requests import get
from os.path import isdir
from os import mkdir, remove, listdir
from re import compile
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def ffmpeg_audio(video: str, audio: str, output: str) -> None:
    subprocess.run(
        f'ffmpeg -i "{video}" -i "{audio}" -c copy -map 0:v:0 -map 1:a:0 "{output}"'
    )
    

def ffmpeg_subs(video: str, subs: str, output: str) -> None:
    subprocess.run(
        f'ffmpeg -i "{video}" -i "{subs}" -c copy -c:s mov_text "{output}"'
    )

def download_playlist(
        url: str, savepath: str, videoQuality: str, root: tk.Tk, 
        font: list, getSubs: bool, getThumbnail: bool, onlyAudio: bool,
        getExtraInfo: bool
    ) -> None:
    try:
        pl = Playlist(url=url)
    except:
        can_connect = tk.Label(root, text = 'Unable to connect, check Wi-FI and URL', font=font)
        can_connect.grid(row=7, column=1)
        return
    
    pl._video_regex = compile(r"\"url\":\"(/watch\?v=[\w-]*)")

    try:
        mkdir(f"{savepath}\{pl.title}")
    except FileExistsError:
        pass
    savepath = f"{savepath}\{pl.title}"

    for vid_url in pl.video_urls:
        print(bcolors.OKGREEN + bcolors.BOLD + vid_url + bcolors.ENDC)
        download(vid_url, savepath, videoQuality, root, font, getSubs, getThumbnail, onlyAudio, getExtraInfo)

def clearCache(filepath="./temp") -> None:
    try:
        remove(filepath)
    except:
        for file in listdir(filepath):
            remove(f"{filepath}/{file}")

def createCache(filepath="./temp") -> None:
    try:
        mkdir(filepath)
    except FileExistsError:
        pass

def remove_chars(string: str) -> str:
    illegal_chars = [
        "   ", "\t", "'", '"', "*", "/", "\\", "<", ">", ":", "|", "?", "."
    ]
    for char in illegal_chars: string = string.replace(char, "")
    return string

def download(
        url: str, savepath: str, videoQuality: str, root: tk.Tk, 
        font: list, getSubs: bool, getThumbnail: bool, onlyAudio: bool,
        extraInfo: bool
    ) -> None:

    url = url.replace(" ", "")

    url_required        = tk.Label(root, text = 'URL is required text field', font=font)
    savepath_required   = tk.Label(root, text = 'Save path is required text field', font=font)
    valid_dir           = tk.Label(root, text = 'Filepath does not exist', font=font)

    # TODO: fix destroy() method for warnings

    #####################################################
    #                                                   #
    #####################################################

    if url == "":
        savepath_required.grid_remove()
        valid_dir.grid_remove()
        url_required.grid(row=6, column=1)
        return
    elif savepath == "":
        url_required.grid_remove()
        valid_dir.grid_remove()
        savepath_required.grid(row=6, column=1)
        return
    elif not isdir(savepath):
        url_required.grid_remove()
        savepath_required.grid_remove()
        valid_dir.grid(row=6, column=1)
        return
    
    #####################################################
    #                                                   #
    #####################################################

    if "list" in url:
        download_playlist(url, savepath, videoQuality, root, font, getSubs, getThumbnail, onlyAudio, extraInfo)
        return

    #####################################################
    #                                                   #
    #####################################################

    try:
        yt = YouTube(url=url, on_progress_callback = on_progress)
    except:
        tk.Label(root, text = 'Unable to connect, check Wi-FI and URL', font=font).grid(row=7, column=1)
        return

    #####################################################
    #                                                   #
    #####################################################

    print(yt.title)
    print(yt.thumbnail_url)

    stream = yt.streams.filter(file_extension="mp4", res=videoQuality)
    print(stream)

    video = stream[-1]
    vid_title = remove_chars(yt.title)
    print(vid_title)

    createCache()
    
    #####################################################
    #                                                   #
    #####################################################

    progress = ttk.Progressbar(
                    root, length=300, mode='determinate'
                ) 
    progress.grid(row=6, column=1)

    #####################################################
    #                                                   #
    #####################################################

    if onlyAudio:
        audio = yt.streams.filter(only_audio=True)[-1]
        audio.download(output_path=savepath)
        return

    progress["value"] += 20
    #####################################################
    #                                                   #
    #####################################################

    if extraInfo:
        info = list(zip(list(yt.vid_info.keys()), list(yt.vid_info.values())))
        with open(f"{savepath}\{vid_title} info.txt", "w") as info_file:
            for item in info:
                info_file.write(f"{item[0]}: {item[1]}\n\n")

    progress["value"] += 20
    #####################################################
    #                                                   #
    #####################################################

    if getSubs:
        try:
            yt.captions["en"].download(output_path=".\\temp", title=vid_title)
            lang = "(en)"
        except:
            try:
                yt.captions["a.en"].download(output_path=".\\temp", title=vid_title)
                lang = "(a.en)"
            except:
                subErr = tk.Label(root, text = 'Subtitles not availble', font=font)
                subErr.grid(row=6, column=1)
                getSubs = False

    progress["value"] += 20
    #####################################################
    #                                                   #
    #####################################################

    if getThumbnail:
        with open(f'{savepath}\{vid_title}.jpg', 'wb') as handler:
            handler.write(
                get(yt.thumbnail_url).content
            )

    progress["value"] += 20
    #####################################################
    #                                                   #
    #####################################################

    if video.is_progressive:
        if getSubs:
            video.download(output_path=".\\temp")
            ffmpeg_subs(
                video=f".\\temp\{vid_title}.mp4",
                subs=f".\\temp\{vid_title} {lang}.srt",
                output=f"{savepath}\{vid_title}.mp4"
            )
        else:
            video.download(output_path=savepath)
    else:
        audio = yt.streams.filter(only_audio=True)[-1]

        audio.download(output_path="temp")
        video.download(output_path="temp")

        if getSubs:
            ffmpeg_audio(
                video=f".\\temp\{vid_title}.mp4",
                audio=f".\\temp\{vid_title}.webm",
                output=f".\\temp\{vid_title}1.mp4"
            )
 
            ffmpeg_subs(
                video=f".\\temp\{vid_title}1.mp4",
                subs=f".\\temp\{vid_title} {lang}.srt",
                output=f"{savepath}\{vid_title}.mp4"
            )        
        else:
            ffmpeg_audio(
                video=f".\\temp\{vid_title}.mp4",
                audio=f".\\temp\{vid_title}.webm",
                output=f"{savepath}\{vid_title}.mp4"
            )

    print(f"{savepath}\{vid_title}.mp4")
    #clearCache()
    progress["value"] += 20
