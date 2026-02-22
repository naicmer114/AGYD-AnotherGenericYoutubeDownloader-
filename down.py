# Importaciones externas
from yt_dlp import YoutubeDL
from win10toast import ToastNotifier
import os

# stdout t
import sys
import re


class download:
    def __init__(self, url, ruta, is_video, formato, calidad_general, label):

        # Se declaran las rutas de ffmpeg y ffprobe
        self.ffmpeg_dir = os.path.dirname(self.resource_path("ffmpeg.exe"))
        self.ffprobe_dir = os.path.dirname(self.resource_path("ffprobe.exe"))
        # print("ffmpeg:", ffmpeg_dir, os.path.exists(ffmpeg_dir))
        # print("ffprobe:", ffprobe_dir, os.path.exists(ffprobe_dir))
        # print("PATH:", os.environ["PATH"])

        # Lists of quality presets
        self.Quality = ["worst", "best"]
        self.Quality_list_for_audio = ["worstaudio", "bestaudio"]
        self.Quality_list_for_video = ["worstvideo", "bestvideo"]

        # Visual Misc
        self.toaster = ToastNotifier()

        # -- Declaro la variable para posterior uso
        self.Quality_global = self.Quality[calidad_general]
        self.Quality_audio = ""
        self.Quality_vid = ""

        # -- PROCESADO DE ydl_opts
        # PARA AUDIO, con inyection de portadas y metadata
        if is_video == 0:
            self.Quality_audio = self.Quality_list_for_audio[calidad_general]
            self.ydl_opts = {
                "format": self.Quality_global,
                "progress_hooks": [
                    self.progress_hook_factory(self.gui_callback, label)
                ],
                "outtmpl": ruta + "/Track: %(playlist_index)s - %(title)s.%(ext)s",
                "quiet": False,  # Desactiva el output a consola
                "ffmpeg_location": self.ffmpeg_dir,
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
            self.Quality_audio = self.Quality_list_for_audio[calidad_general]
            self.Quality_vid = self.Quality_list_for_video[calidad_general]
            self.ydl_opts = {
                "progress_hooks": [
                    self.progress_hook_factory(self.gui_callback, label)
                ],
                "format": formato + "/" + self.Quality_audio + "/" + self.Quality_vid,
                "outtmpl": ruta + "/%(title)s.%(ext)s",
                "quiet": False,  # Desactiva el output a consola
                "ffmpeg_location": os.path.realpath("./libs/ffmpeg/bin/ffmpeg.exe"),
            }

        """
            --- Dowload Section ---
        """

        print("> Descargando")
        print(self.ydl_opts)
        YoutubeDL(self.ydl_opts).download(url)

        # Se muestra la notificacion
        self.toaster.show_toast(
            "AGYD", "Descarga/s terminada/s", icon_path="AGYD_logo.ico", duration=5
        )

        print("> Hilo terminado")

    # Search resources function
    def resource_path(self, name):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, name)
        return os.path.join(os.path.abspath("."), name)

    # Procesos asociados a la redireccion de la informacion de ytdlp
    def progress_hook_factory(self, gui_callback, label):
        # Procesamos la redireccion de la informacion sobre el progreso de ytdlp
        def hook(d):
            # Si esta descargando procesamos y presentamos la info en el gui
            if d["status"] == "downloading":
                # Se toman los datos y se quitan espacios vacios
                percent = d.get("_percent_str", "").strip()
                speed = d.get("_speed_str", "").strip()
                eta = d.get("_eta_str", "").strip()
                # Se reconstruye el texto a presentar bajo el formato deseado
                texto = f"{percent} {speed}\nTiempo faltante: {eta}"

                # Limpiamos los códigos ANSI (caracteres invalidos) antes de mostrar
                texto_limpio = self.limpiar_ansi(texto)
                # Pasamos la informacion a la funcion que modificara el gui
                self.gui_callback(texto_limpio, label)

        return hook

    # Limpiamos el texto que se pase de caracteres invialidos para la presentacion
    def limpiar_ansi(self, texto):
        # Regex que elimina todos los códigos de color ANSI
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub("", texto)  # Se devuelven los datos sin comillas

    # Se actualizan los datos de la gui e nbase a los datos disponibles
    def gui_callback(self, texto, label):
        # Se modifica el Label del gui que muestra la velocidad de descarga
        label.config(text=texto)
