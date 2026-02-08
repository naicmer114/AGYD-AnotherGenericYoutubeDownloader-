# Importaciones externas
from tkinter import Tk, Label, ttk, Button, Entry, filedialog
from threading import Thread
import os

# Importaciones internas
from down import download

# -- MANEJO DE LOG
def log_on_startup():
    # Si existe un log previo se elimina
    if os.path.exists("out.txt"):
        os.remove("out.txt")
    # Si por alguna razon, no existia un log previo, se notifica por si acaso
    else:
        print("The file does not exist")
    # Se crea el archivo para el log
    open("out.txt", "x")

"""
    -----------------------
    Diccionario de configuracion para down.py, ergo, ydl_opts
    Orden en download(): url, ruta, video, formato, calidad
    -----------------------
"""
config = {
    # La ruta tomara por defecto el donde se este ejecutando AGYD
    "ruta": os.getcwd(),
    "is_video": 0,
    "formato": "mp3",
    "calidad_general": 1,
    #'video_calidad': 1,
    #'audio_calidad': 1,
}

"""
    -----------------------
    Buttons
      and
    Behavior
    Fuctions for AGYD GUI
    -----------------------
"""


# -- Function associated with the download button
def down():
    """
    Se declaran los procedimientos por hilos por ser tareas tardadas,
    lo que previene que el GUI del AGYD se congele
    """
    # Seteo del hilo de descarga
    global trhead_download
    trhead_download = Thread(
        target=download,
        args=(
            urlTP.get(),
            config["ruta"],  # SI NO se coloca ruta se usa la del programa
            config["is_video"],
            config["formato"],
            config["calidad_general"],
        ),
    )

    # Seteo del hilo de la barra de progreso
    global thread_progress
    thread_progress = Thread(
        target=check_progress,
    )  # Se declara el hilo a usar para la descarga, previniendo de que el GUI se congele

    # Arranque de hilos
    trhead_download.start()
    thread_progress.start()


# -- DEFAULTS PRESET FUNCTIONS
# Default Audio Preset
def audio_default():
    config.update(formato="mp3")
    config.update(is_video=0)
    what_is_downloading.config(text="Audio")


# Default Video Preset
def video_default():
    config.update(formato="mp4")
    config.update(is_video=1)
    what_is_downloading.config(text="Video")


# -- PROGRESS BAR BEHAVIOR
# Fuction used on thread declaration on down() fuction from Submmit Button
def check_progress():
    start_progress()
    trhead_download.join()
    stop_progress()


# Start "Animation" for progress bar
def start_progress():
    progress.start()
    progress.state = "disabled"
    progress.state = "normal"


# Stop "Animation" for progress bar
def stop_progress():
    progress.stop()
    progress.state = "normal"
    progress.state = "disabled"


# -- Path desired function
def path_finder():
    # Declaramos la ruta elejida para guardarla
    ruta_elejida = ""
    # Guardamos la ruta en la variable al usar "filedialog"
    ruta_elejida = filedialog.askdirectory(title="Elija la ruta de descarga")
    # Si se elije una ruta
    if ruta_elejida != "":
        rutaT.config(text=ruta_elejida)
        config.update(ruta=ruta_elejida)
    else:  # Si NO se elije una ruta
        # Reescribimos la ruta, tomando la locacion de ejecucion del AGYD
        ruta_elejida = os.getcwd()
        rutaT.config(text=ruta_elejida)
        config.update(ruta=ruta_elejida)


# -- Visual structure of AnotherGenericYoutubeDownloader (AGYD)
main = Tk()
main.title("AGYD")

# Seccion URL
Label(main, text="URL").grid(row=0, column=0)
urlTP = Entry(main)
urlTP.grid(row=0, column=1)

# Botones defaults
# Seccion Audio Default Preset
audio_default_button = Button(main, text="Audio Default Preset", command=audio_default)
audio_default_button.grid(row=0, column=2)

# Seccion Video Default Preset
video_default_button = Button(main, text="Video Default Preset", command=video_default)
video_default_button.grid(row=0, column=3)

# Seccion RUTA
Label(main, text="Ruta").grid(row=1, column=0)
rutaT = Label(main, text=os.getcwd())  # Por defecto, mostrara la ruta del AGYD
rutaT.grid(row=1, column=1)
pathB = Button(main, text="Buscar", command=path_finder)
pathB.grid(row=1, column=2)

# Seccion SUBMIT
submit = Button(
    main, text="Descargar", command=down
)  # sin parentesis pq si no se considera un llamado injectado
submit.grid(row=2, column=1)

# Seccion Feedback User what_is_downloading
what_is_downloading = Label(main, text="Audio")
what_is_downloading.grid(row=2, column=2)

# Seccion BARRA DE PROGRESO
progress = ttk.Progressbar(main, length=200, mode="indeterminate")
progress.grid(row=3, column=2)

# Ejecucion del GUI
main.mainloop()

# Se crea el log de AGYD 
log_on_startup()