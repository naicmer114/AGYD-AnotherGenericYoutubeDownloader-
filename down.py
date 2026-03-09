# Importaciones externas
from yt_dlp import YoutubeDL
from win10toast import ToastNotifier
import os

# stdout t
import sys
import re
from PIL import Image
import customtkinter as ctk


class download:
    def __init__(
        self,
        url,
        ruta,
        is_video,
        formato,
        calidad_general,
        label_speed,
        progress,
        label_nombre_archivo,
        label_image,
        stop_signal,
    ):
        # Declaramos previamente la variable encargada de evitar modificaciones
        # inecesarias en cuanto a la portada del archivo descargado
        self.prev_nombre_thumbnail = ""

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
                    self.progress_hook_factory(
                        self.gui_callback,
                        label_speed,
                        label_nombre_archivo,
                        label_image,
                        progress,
                    )
                ],
                "outtmpl": ruta + "/Track: %(playlist_index)s - %(title)s.%(ext)s",
                "quiet": True,  # Desactiva el output a consola
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
                    self.progress_hook_factory(
                        self.gui_callback,
                        label_speed,
                        label_nombre_archivo,
                        label_image,
                        progress,
                    )
                ],
                "format": formato + "/" + self.Quality_audio + "/" + self.Quality_vid,
                "outtmpl": ruta + "/%(title)s.%(ext)s",
                "quiet": True,  # Desactiva el output a consola
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

        """
            Cambiamos el estado de la señal para saber que el hilo termino.
            Se usa para cambios en la funcion:
                "wait_to_kill_progress_bar"(07/03/2026)
        """
        stop_signal.set()

    # Search resources function
    def resource_path(self, name):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, name)
        return os.path.join(os.path.abspath("."), name)

    # Procesos asociados a la redireccion de la informacion de ytdlp
    def progress_hook_factory(
        self, gui_callback, label_speed, label_nombre_archivo, label_image, progress
    ):
        # Procesamos la redireccion de la informacion sobre el progreso de ytdlp
        def hook(d):
            # Declaramos las variables que deben permanecer a lo largo de las
            # iteraciones de yt_dlp
            texto_limpio = ""
            nombre_archivo = ""

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

            # Si el nombre del archivo en descarga esta disponible, realizamos
            if d.get("filename"):
                # Se toma el nombre del archivo en descarga
                nombre_archivo = os.path.basename(d.get("filename"))
                """
                    Explicacion resumida:
                        Se toma el nombre del archivo y se pasa a clean_filename()
                        para limpiar el texto, pero al pasar el parametro 0 solo
                        accedemos al retiro de la extension del archivo. Esto
                        porque las portadas tienen el mismo nombre que el archivo
                        descargado.
                        
                        Con el parametro en 1, accedemos al retiro de todo texto
                        no considerable util para el usuario. En este caso solo nos
                        quedara el nombre relativo de la cancion o video descargado
                        
                        EJ:
                            Track# 06 - Missed Kiss.temp.mp3
                            
                            Si parametro es 0, nos quedara: Track# 06 - Missed Kiss
                            Si parametro 1, nos quedara: Missed Kiss
                """
                # Nos quedamos con todo menos la extension, y reemplazamos
                # dicha extension con ".webp", ya que asi baja yt_dlp
                # las portadas
                nombre_thumbnail = self.clean_filename(nombre_archivo, 0) + ".webp"

                # Nos quedamos solo con el titulo en si de lo que se este
                # descargando
                nombre_archivo = self.clean_filename(nombre_archivo, 1)

            # Si no esta disponible el nombre del archivo en descarga,
            # declaramos un placeholder
            else:
                nombre_archivo = "N0N3"

            # Si el texto del progreso y el nombre del archivo en descarga
            # estan disponibles, procedemos
            if texto_limpio and nombre_archivo:
                # Pasamos la informacion a la funcion que modificara el gui
                self.gui_callback(
                    texto_limpio,
                    nombre_archivo,
                    nombre_thumbnail,
                    label_speed,
                    label_nombre_archivo,
                    label_image,
                    progress,
                    percent,
                )

        return hook

    # Limpiamos el texto que se pase de caracteres invialidos para la presentacion
    def limpiar_ansi(self, texto):
        # Regex que elimina todos los códigos de color ANSI
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub("", texto)  # Se devuelven los datos sin comillas

    """
        Limpiamos sea el nombre del archivo
        de la imagen (relativo) sin pasarle un parametro
        (param), si se pasa 0 entonces el nombre del archivo
        procesandose es para presentarlo al usuario, mas no
        para buscar la imagen de lo que esta descargando
        el usuario. 
    """

    def clean_filename(self, filename, param: None):

        if param == 1:
            # se quita la extension
            filename = re.sub(r"\.mp4$", "", filename)

            # se quita "Track# NA - "
            filename = re.sub(r"^Track#\s\w+\s-\s", "", filename)

            # se quita el slash vertical
            filename = filename.replace("｜", "")
        else:
            # se quita la extension
            filename = re.sub(r"\.mp4$", "", filename)

        return filename.strip()

    # Se actualizan los datos de la gui e nbase a los datos disponibles
    def gui_callback(
        self,
        texto_limpio,
        nombre_archivo,
        nombre_thumbnail,
        label_speed,
        label_nombre_archivo,
        label_image,
        progress,
        percent,
    ):
        """
        Primero se modifican los labels, luego lo demas
        """
        # Se modifica el Label del gui que muestra la velocidad de descarga
        label_speed.configure(text=texto_limpio)

        # Presentamos el nombre (titulo) de lo que se este descargando
        label_nombre_archivo.configure(text=nombre_archivo)
        """
            Si el nombre de la portada previa (en caso de albumes o playlists)
            del contenido que se este descargando difiere de la actual en
            proceso, procedemos a cambiar la portada del archivo en proceso
            en la interfaz
        """
        if self.prev_nombre_thumbnail != nombre_thumbnail:
            try:
                # Cargo la imagen ya con placeholder
                self.img = Image.open(nombre_thumbnail)
                # Redimenciono al deseado
                self.img = self.img.resize((135, 83), Image.LANCZOS)
                # Se carga como un elemento para tkinter
                self.python_image = ctk.CTkImage(
                    light_image=self.img, dark_image=self.img, size=(135, 83)
                )
                label_image.configure(image=self.python_image)
            # No se como reaccionar a un error, el unico error seria que esta
            # portada no exista o su formato no sea el esperado o procesable
            except:
                pass
            # Ya despues de realizar lo anterior. Guardamos el nombre de la
            # portada para mantener la coerencia de la verificacion habia antes
            # del try al que pertenece este "finally"
            finally:
                self.prev_nombre_thumbnail = nombre_thumbnail

        # Bar Progress Section
        # Se limpia el hook del porcentaje
        per = self.limpiar_ansi(percent)

        # Se retira el simbolo del porcentaje
        per = per.replace("%", "")

        # Se pasa a flotante (porque aveces viene como 0.0 o 0.1) y luego a entero
        per = int(float(per))

        # Se actualiza la barra de progreso
        progress.config(value=per)
