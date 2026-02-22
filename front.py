# Importaciones externas
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
import os

# Importaciones internas
from down import download


class window(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        # --- Inicializacion de datos ---
        """
        -----------------------
        Diccionario de configuracion para down.py, ergo, ydl_opts
        Orden en download(): url, ruta, video, formato, calidad
        -----------------------
        """
        self.download_config = {
            # La ruta tomara por defecto el donde se este ejecutando AGYD
            "ruta": os.getcwd(),
            "is_video": 0,
            "formato": "mp3",
            "calidad_general": 1,
            #'video_calidad': 1,
            #'audio_calidad': 1,
        }

        """
            --- Tratado de tkinter --- 
        """
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Se establece el titulo de la ventana
        parent.title("AGYD")

        parent.resizable(False, False)
        # Se establece el icono de la ventana
        # parent.iconbitmap("AGYD_logo.ico")

        """
            --- Static Style Section ---
        """
        # Se abrevia el ttk.Style() en una variable
        style = ttk.Style()
        # Estilo en general configurado
        style.theme_use("clam")  # Try: 'alt', 'default', 'classic', 'clam'

        # Color/Fondo del frame y ventana
        bg_color_GENERAL = "#fcff7d"
        self.parent.config(bg=bg_color_GENERAL)
        style.configure(
            "TFrame",
            background=bg_color_GENERAL,
        )
        # Color/Fondo de los botones de la ventana
        bg_button_color_GENERAL = "#807dff"
        bg_button_color_FOCUSED = "#adacff"
        style.configure(
            "TButton",
            relief="ridge",
            background=bg_button_color_GENERAL,
            foreground="black",
            focusthickness=3,
            focuscolor="none",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TLabel",
            background=bg_color_GENERAL,
            font=("Segoe UI", 10, "bold"),
        )

        """
            --- Interactive Style Section --- 
        """
        style.map(
            "TButton",
            background=[("active", bg_button_color_FOCUSED)],
            relief=[("active", "solid")],
        )
        style.map("TEntry", lightcolor=[("focus", "blue")])

        # Seccion URL
        ttk.Label(self, text="URL").grid(row=0, column=0)
        self.urlTP = ttk.Entry(self, width=50)
        self.urlTP.grid(row=0, column=1)

        # Seccion RUTA
        ttk.Label(self, text="Ruta de descarga / Download path").grid(row=1, column=0)
        self.rutaT = ttk.Label(
            self, text=os.getcwd()
        )  # Por defecto, mostrara la ruta del AGYD
        self.rutaT.grid(row=1, column=1)
        self.pathB = ttk.Button(self, text="Buscar / Browse", command=self.path_finder)
        self.pathB.grid(row=1, column=2)

        # -- Botones defaults

        # Label de los presets
        ttk.Label(self, text="Presets para descarga / Download Preset").grid(
            row=2, column=0
        )

        # Seccion Audio Default Preset
        self.audio_default_button = ttk.Button(
            self, text="Audio Default Preset", command=self.audio_default
        )
        self.audio_default_button.grid(row=2, column=1)

        # Seccion Video Default Preset
        self.video_default_button = ttk.Button(
            self, text="Video Default Preset", command=self.video_default
        )
        self.video_default_button.grid(row=2, column=2)

        # Seccion Feedback User what_is_downloading
        self.preset_selected = ttk.Label(self, text="Preset selected / Preset elegido")
        self.preset_selected.grid(row=3, column=0)

        # Seccion Feedback User what_is_downloading
        self.what_is_downloading = ttk.Label(self, text="Audio")
        self.what_is_downloading.grid(row=3, column=1)

        # Seccion SUBMIT
        self.submit = ttk.Button(
            self, text="Descargar / Download", command=self.down
        )  # sin parentesis pq si no se considera un llamado injectado
        self.submit.grid(row=4, column=1)

        # Temp Reminder
        self.reminder = ttk.Label(
            self,
            text="--------------------------------------------------------->\n"
            + "(ENG: While downloading, wait for this boy to be static :3)\n"
            + "(ESP:Durante descargas, espera a que la barra este estatica :3)",
        )
        self.reminder.grid(row=5, column=0)

        # Seccion BARRA DE PROGRESO
        self.progress = ttk.Progressbar(self, length=200, mode="indeterminate")
        self.progress.grid(row=5, column=1)

        # LABELS FOR DOWNLOAD FEEDBACK
        self.speed = ttk.Label(
            self,
            text="ENG: Download speed, percentage and estimated time\n"
            + "ESP: Velocidad de descarga, porcentaje y tiempo estimado",
        )
        self.speed.grid(row=5, column=2)

        """
            Context Menu
            
            Thanks to Delrius Euphoria from stack overflow
            Answer Associated: https://stackoverflow.com/a/66514657
        """
        # Se declara el menu contextual con ayuda de Tkinter
        self.menu = tk.Menu(self, tearoff=0)
        # Se añaden las opciones de dicho menu contextual
        self.menu.add_command(label="Paste / Pegar", command=self.contextM_paste)
        self.menu.add_command(label="Copy / Copiar", command=self.contextM_copy)
        # Se asocia los comportamientos ocurridos con el menu contextual
        # A la bandeja de texto
        self.urlTP.bind("<Button-3>", self.popup)

    """
        -----------------------
            Behavior
        Fuctions for AGYD GUI
        -----------------------
    """

    # -- Function associated with the download button
    def down(self):
        """
        Se declaran los procedimientos por hilos por ser tareas tardadas,
        lo que previene que el GUI del AGYD se congele
        """

        # Seteo del hilo de descarga
        global trhead_download
        trhead_download = Thread(
            target=download,
            args=(
                self.urlTP.get(),
                self.download_config[
                    "ruta"
                ],  # SI NO se coloca ruta se usa la del programa
                self.download_config["is_video"],
                self.download_config["formato"],
                self.download_config["calidad_general"],
                self.speed,
            ),
        )

        # Seteo del hilo de la barra de progreso
        global thread_progress
        thread_progress = Thread(
            target=self.check_progress,
        )  # Se declara el hilo a usar para la descarga, previniendo de que el GUI se congele

        # Arranque de hilos
        # No se declaran en self pq son hinerentes de la funcion "down" en la que estan
        trhead_download.start()
        thread_progress.start()

    # -- Path desired function
    def path_finder(self):
        # Declaramos la ruta elejida para guardarla
        ruta_elejida = ""
        # Guardamos la ruta en la variable al usar "filedialog"
        ruta_elejida = filedialog.askdirectory(title="Elija la ruta de descarga")
        # Si se elije una ruta
        if ruta_elejida != "":
            self.rutaT.config(text=ruta_elejida)
            self.download_config.update(ruta=ruta_elejida)
        else:  # Si NO se elije una ruta
            # Reescribimos la ruta, tomando la locacion de ejecucion del AGYD
            ruta_elejida = os.getcwd()
            self.rutaT.config(text=ruta_elejida)
            self.download_config.update(ruta=ruta_elejida)

    # -- DEFAULTS PRESET FUNCTIONS
    # Default Audio Preset
    def audio_default(self):
        self.download_config.update(formato="mp3")
        self.download_config.update(is_video=0)
        self.what_is_downloading.config(text="Audio")

    # Default Video Preset
    def video_default(self):
        self.download_config.update(formato="mp4")
        self.download_config.update(is_video=1)
        self.what_is_downloading.config(text="Video")

    # -- PROGRESS BAR BEHAVIOR
    # Fuction used on thread declaration on down() fuction from Submmit Button
    def check_progress(self):
        self.start_progress()
        trhead_download.join()
        self.stop_progress()

    # Start "Animation" for progress bar
    def start_progress(self):
        self.progress.start()
        self.progress.state = "disabled"
        self.progress.state = "normal"

    # Stop "Animation" for progress bar
    def stop_progress(self):
        self.progress.stop()
        self.progress.state = "normal"
        self.progress.state = "disabled"

    """
        Context Menu Behavior
    """

    def popup(self, event):
        try:
            self.menu.tk_popup(
                event.x_root, event.y_root
            )  # Pop the menu up in the given coordinates
        finally:
            self.menu.grab_release()

    def contextM_paste(self):
        # Se toma lo que este en el porta papeles
        clipboard = root.clipboard_get()
        # Se limpia el campo de texto
        self.urlTP.delete(0, tk.END)
        # Se pega en el campo de texto el lo que este en el porta papeles
        self.urlTP.insert("end", clipboard)

    def contextM_copy(self):
        # Se guarda el texto que haya en la bandeja de texto
        text_being_in_entry = self.urlTP.get()
        # Se limpia el porta papeles
        root.clipboard_clear()
        # Se copia al porta papeles el texto que habia en la bandeja
        root.clipboard_append(text_being_in_entry)


# Se define la forma de proceder inicial al llamar al front
if __name__ == "__main__":
    # Se declara al root como empleador de los modulos de tkinter
    root = tk.Tk()

    # Se llama a la clase para crear el objeto de ventana,
    # y se empaquetan los parametros de heredara la ventana
    window(root).pack(side="top", fill="both", expand=True)

    # Se usa una verison extremadamente simplificada para centrar la ventana
    root.eval("tk::PlaceWindow . center")

    root.mainloop()
