from yt_dlp import YoutubeDL

import os
import sys


# Search resources function
def resource_path(name):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.abspath("."), name)


# Se declaran las rutas de ffmpeg y ffprobe
ffmpeg_dir = os.path.dirname(resource_path("ffmpeg.exe"))
ffprobe_dir = os.path.dirname(resource_path("ffprobe.exe"))
# print("ffmpeg:", ffmpeg_dir, os.path.exists(ffmpeg_dir))
# print("ffprobe:", ffprobe_dir, os.path.exists(ffprobe_dir))
# print("PATH:", os.environ["PATH"])


# Lists of quality presets
Quality = ["worst", "best"]
Quality_list_for_audio = ["worstaudio", "bestaudio"]
Quality_list_for_video = ["worstvideo", "bestvideo"]


def download(url, ruta, is_video, formato, calidad_general):
    # -- Declaro la variable para posterior uso
    Quality_global = Quality[calidad_general]
    Quality_audio = ""
    Quality_vid = ""

    # -- PROCESADO DE ydl_opts
    # PARA AUDIO, con inyection de portadas y metadata
    if is_video == 0:
        Quality_audio = Quality_list_for_audio[calidad_general]
        ydl_opts = {
            "format": Quality_global,
            "outtmpl": ruta + "/Track: %(playlist_index)s - %(title)s.%(ext)s",
            "quiet": True,  # Desactiva el output a consola
            "ffmpeg_location": ffmpeg_dir,
            "postprocessors": [  # Extract audio using ffmpeg
                {
                    # Separacion de audio del video para posprocesado
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": formato,  # Codec de audio/video a usar
                    "preferredquality": "320",
                    "nopostoverwrites": False,
                },
                {
                    # Se incorpora la metadata de la cancion.
                    # Se hace primero ya que la portada se pierde al reescribir
                    # la metadata, mas no al revez
                    "key": "FFmpegMetadata"
                },
                {"key": "EmbedThumbnail"},  # Se incorpora la portada al archivo
            ],
            "writethumbnail": True,  # Se baja la portada
            "verbose": True,
        }

    # PARA VIDEO, con inyection de portadas y metadata
    if is_video == 1:
        Quality_audio = Quality_list_for_audio[calidad_general]
        Quality_vid = Quality_list_for_video[calidad_general]

        ydl_opts = {
            "format": formato + "/" + Quality_audio + "/" + Quality_vid,
            "outtmpl": ruta + "/Track: %(playlist_index)s - %(title)s.%(ext)s",
            "quiet": True,  # Desactiva el output a consola
            "ffmpeg_location": os.path.realpath("./libs/ffmpeg/bin/ffmpeg.exe"),
        }

    org_std = sys.stdout  # save the original sys.stdout to reset it
    with open("out.txt", "a") as f:
        sys.stdout = f  # redirect stdout to direct write
        """
            Usando el metodo YoutubeDL y dandole las configuraciones previas
            como parametros, se emplea su comportameniento de descargar
            (Download) dandole el url del video / playlist
        """
        print("> Descargando")
        print(ydl_opts)
        YoutubeDL(ydl_opts).download(url)
    sys.stdout = org_std  # reset the stdout as original as it was
