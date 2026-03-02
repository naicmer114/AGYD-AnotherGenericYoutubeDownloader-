# Importaciones externas
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog
from threading import Thread
import os
import sys

# Importaciones internas
from down import download


class window(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        # --- Inicializacion de datos ---
        """
        -----------------------
        Diccionario de configuracion para down.py, ergo, ydl_opts
        Orden en download(): url, ruta, video, formato, calidad
        -----------------------
        """
        self.download_configure = {
            # La ruta tomara por defecto el donde se este ejecutando AGYD
            "ruta": os.getcwd(),
            "is_video": 0,
            "formato": "mp3",
            "calidad_general": 1,
            #'video_calidad': 1,
            #'audio_calidad': 1,
        }

        """
            --- PRE TKINTER WIDGETS --- 
        """
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Se establece el titulo de la ventana
        parent.title("AGYD")
        parent.geometry("480x640")
        parent.resizable(False, False)   

        # Thanks to theme use to: a13xe (https://github.com/a13xe)
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        self.apariencia_de_sistema = ctk.get_appearance_mode()
        ctk.set_default_color_theme(self.resource_path("violet.json"))

        # Se establece el icono de la ventana
        parent.iconbitmap(self.resource_path("AGYD_logo.ico"))

        # CANVAS COLOR SECTION
        self.color_list = ["#F0F0F0", "#0F0F0F"]
        self.mode = 0 if ctk.get_appearance_mode() == "Light" else 1
        self.color_bg_to_canvas_label = self.color_list[self.mode]

        self.canva1 = ctk.CTkCanvas(
            self,
            bg=self.color_bg_to_canvas_label,
            width=460,
            height=177,
            highlightthickness=0,
            borderwidth=0,
        )
        self.canva1.place(x=9, y=20)

        self.canva2 = ctk.CTkCanvas(
            self,
            bg=self.color_bg_to_canvas_label,
            width=460,
            height=165,
            highlightthickness=0,
            borderwidth=0,
        )
        self.canva2.place(x=9, y=219)

        self.canva3 = ctk.CTkCanvas(
            self,
            bg=self.color_bg_to_canvas_label,
            width=460,
            height=228,
            highlightthickness=0,
            borderwidth=0,
        )
        self.canva3.place(x=9, y=403)

        # Seccion URL
        ctk.CTkLabel(self, text="URL").place(x=24, y=31)
        self.urlTP = ctk.CTkEntry(self, width=429, height=43)
        self.urlTP.place(x=26, y=62)

        # Seccion RUTA
        ctk.CTkLabel(
            self,
            text="Ruta de descarga / Download path",
            anchor="center",
            width=460,
            height=24,
        ).place(x=9, y=123)
        self.pathB = ctk.CTkButton(
            self,
            text="Buscar / Browse",
            command=self.path_finder,
            width=157,
            height=31,
        )
        self.pathB.place(x=26, y=159)

        self.rutaT = ctk.CTkLabel(
            self,
            text=os.getcwd(),
            width=275,
            height=44,
        )  # Por defecto, mostrara la ruta del AGYD
        self.rutaT.place(x=189, y=153)

        # -- Botones defaults

        # Label de los presets
        ctk.CTkLabel(
            self,
            text="Presets para descarga / Download Preset",
            anchor="center",
            width=460,
            height=24,
        ).place(x=9, y=229)

        # Seccion Audio Default Preset
        self.audio_default_button = ctk.CTkButton(
            self,
            text="Audio Default Preset",
            command=self.audio_default,
            width=201,
            height=54,
        )
        self.audio_default_button.place(x=26, y=263)

        # Seccion Video Default Preset
        self.video_default_button = ctk.CTkButton(
            self,
            text="Video Default Preset",
            command=self.video_default,
            width=201,
            height=54,
        )
        self.video_default_button.place(x=256, y=263)

        # Seccion Feedback User what_is_downloading
        self.preset_selected = ctk.CTkLabel(
            self,
            text="Preset selected / Preset elegido",
            justify="center",
            width=327,
            height=38,
        )
        self.preset_selected.place(x=9, y=336)

        # Seccion Feedback User what_is_downloading
        self.what_is_downloading = ctk.CTkLabel(self, text="Audio")
        self.what_is_downloading.place(x=336, y=343)

        # Seccion SUBMIT
        self.submit = ctk.CTkButton(
            self,
            text="Descargar / Download",
            command=self.down,
            width=168,
            height=43,
        )  # sin parentesis pq si no se considera un llamado injectado
        self.submit.place(x=161, y=423)

        # Seccion BARRA DE PROGRESO
        self.progress = ttk.Progressbar(
            self,
            length=300,
        )
        self.progress.place(x=94, y=485)

        # LABELS FOR DOWNLOAD FEEDBACK
        self.speed = ctk.CTkLabel(
            self,
            text="ESP: Velocidad de descarga, porcentaje y tiempo estimado\n"
            + "ENG: Download speed, percentage and estimated time",
            justify="center",
            width=425,
            height=52,
        )
        self.speed.place(x=32, y=510)

        # Temporal Reminder
        self.reminder = ctk.CTkLabel(
            self,
            text="(ESP: Recibiras una notificacion cuando la descarga termine.\n Dura mas para listas de reproduccion)\n"
            + "(ENG: You will recive an notification when it ends.\n It takes longer for playlists)",
            justify="center",
            width=425,
            height=52,
        )
        self.reminder.place(x=32, y=563)

        """
            Top Menu
        """
        # Se crea la variable asociada al
        self.menu_bar = tk.Menu(parent)
        # Se añade la opcion asociada al switch del menu oscuro y diurno
        self.menu_bar.add_command(
            label="Dark Mode / Light Mode", command=self.change_theme
        )
        parent.config(menu=self.menu_bar)  # Se añade como menu a la ventana en si

        """
            Context Menu
            
            Thanks to Delrius Euphoria from stack overflow
            Answer Associated: https://stackoverflow.com/a/66514657
        """
        # Se declara el menu contextual con ayuda de Tkinter
        self.context_menu = tk.Menu(self, tearoff=0)
        # Se añaden las opciones de dicho menu contextual
        self.context_menu.add_command(
            label="Paste / Pegar", command=self.contextM_paste
        )
        self.context_menu.add_command(label="Copy / Copiar", command=self.contextM_copy)
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
                self.download_configure[
                    "ruta"
                ],  # SI NO se coloca ruta se usa la del programa
                self.download_configure["is_video"],
                self.download_configure["formato"],
                self.download_configure["calidad_general"],
                self.speed,
                self.progress,
            ),
        )

        # Arranque de hilos
        # No se declaran en self pq son hinerentes de la funcion "down" en la que estan
        trhead_download.start()

    # -- Path desired function
    def path_finder(self):
        # Declaramos la ruta elejida para guardarla
        ruta_elejida = ""
        # Guardamos la ruta en la variable al usar "filedialog"
        ruta_elejida = filedialog.askdirectory(title="Elija la ruta de descarga")
        # Si se elije una ruta
        if ruta_elejida != "":
            self.rutaT.configure(text=ruta_elejida)
            self.download_configure.update(ruta=ruta_elejida)
        else:  # Si NO se elije una ruta
            # Reescribimos la ruta, tomando la locacion de ejecucion del AGYD
            ruta_elejida = os.getcwd()
            self.rutaT.configure(text=ruta_elejida)
            self.download_configure.update(ruta=ruta_elejida)

    # -- DEFAULTS PRESET FUNCTIONS
    # Default Audio Preset
    def audio_default(self):
        self.download_configure.update(formato="mp3")
        self.download_configure.update(is_video=0)
        self.what_is_downloading.configure(text="Audio")

    # Default Video Preset
    def video_default(self):
        self.download_configure.update(formato="mp4")
        self.download_configure.update(is_video=1)
        self.what_is_downloading.configure(text="Video")

    """
        Context Menu Behavior
    """

    def popup(self, event):
        try:
            # Intentamos inicializar el menu contextual en la posicion
            # relativa de donde se realizo el click drecho
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Si se pudo realizar lo anterior, entonces se muestran las opciones
            self.context_menu.grab_release()

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

    # All theme related changes
    def change_theme(self):
        # If the theme dark mode
        if self.apariencia_de_sistema == "Dark":
            # Change general theme
            ctk.set_appearance_mode("Light")
            # Redifine the current theme
            self.apariencia_de_sistema = ctk.get_appearance_mode()

            # Change color for canvas to light colors
            self.color_bg_to_canvas_label = self.color_list[0]
            # Individual changing of the canvas color
            self.canva1.config(bg=self.color_bg_to_canvas_label)
            self.canva2.config(bg=self.color_bg_to_canvas_label)
            self.canva3.config(bg=self.color_bg_to_canvas_label)
        # If the theme light mode
        else:
            # Change general theme
            ctk.set_appearance_mode("Dark")
            # Redifine the current theme
            self.apariencia_de_sistema = ctk.get_appearance_mode()

            # Change color for canvas to dark colors
            self.color_bg_to_canvas_label = self.color_list[1]
            # Individual changing of the canvas color
            self.canva1.config(bg=self.color_bg_to_canvas_label)
            self.canva2.config(bg=self.color_bg_to_canvas_label)
            self.canva3.config(bg=self.color_bg_to_canvas_label)
    # Search resources function
    def resource_path(self, name):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, name)
        return os.path.join(os.path.abspath("."), name)


# Se define la forma de proceder inicial al llamar al front
if __name__ == "__main__":
    # Se declara al root como empleador de los modulos de tkinter
    root = ctk.CTk()

    # Se llama a la clase para crear el objeto de ventana,
    # y se empaquetan los parametros de heredara la ventana
    window(root).pack(side="top", fill="both", expand=True)

    # Se usa una verison extremadamente simplificada para centrar la ventana
    root.eval("tk::PlaceWindow . center")

    root.mainloop()
