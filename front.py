# Importaciones externas
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog
from threading import Thread, Event
import os
import sys

# Importaciones internas
from down import download

import json
from PIL import Image


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

        # Tratado de lenguaje del usuario
        self.os_language = os.getenv("LANG")
        if self.os_language != None:
            # Si el lenguaje es algun español
            if "es" in self.os_language:
                self.os_factor = "es"
            # Si el lenguaje es algun ingles
            elif "en" in self.os_language:
                self.os_factor = "en"
            # Cualquier idioma que no tenga traduccion directa, se usa el ingles
            else:
                self.os_factor = "en"
        else:
            self.os_factor = "en"
            
        # Cargado del JSON
        with open(self.resource_path("langs.json"), "r") as file:
            self.data = json.load(file)

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

        """
            Se crea una lista para control posterior con los labels
            
            Diseño manejado:
                Todo Label estatico (ej. el template de descarga pide
                el lenguaje cada que se llama a su generacion 07/03/2026)
                
                Cada adicion al diccionario, necesita que previamente se sume
                1 al id, de otra manera, puede sobre escribir datos ya
                registrados
                
                Todo label de dicho tipo maneja un id, y contiene una
                doble dimension de datos, como si se manejase un json.codecs 
        """
        self.labels_in_tkikter = {}
        self.ids = 0

        # Se renderiza el contenido de la seccion del url y ruta de descarga
        self.template_url_section()

        # Se renderiza el contenido de la seccion preferencias de descarga
        self.template_download_pref()

        # Seccion SUBMIT
        self.submit = ctk.CTkButton(
            self,
            text=self.data["button_download"][self.os_factor],
            command=self.down,
            width=168,
            height=43,
        )  # sin parentesis pq si no se considera un llamado injectado
        self.submit.place(x=162, y=386)
        self.ids = self.ids + 1
        self.labels_in_tkikter[self.ids] = {
            "widget": self.submit,
            "lang": "button_download",
        }

        # Se cargan los menus para el Tkinter
        self.template_tk_menus(parent)

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

        self.stop_signal = Event()

        widgets_download_info = self.template_downloading_info()

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
                self.filename,
                self.label_image,
                self.stop_signal,
            ),
        )
        self.wait_to_kill_progress_bar(self.stop_signal, widgets_download_info)

        # Arranque de hilos
        # No se declaran en self pq son hinerentes de la funcion "down" en la que estan
        trhead_download.start()

    # Using the submodule of "threading" module, we use a "signal" to know
    # when the thread associated is done, there for, we can do any change
    def wait_to_kill_progress_bar(self, stop_signal, widgets_download_info):
        # If the thread is done, we do any inside here
        if stop_signal.is_set():
            print("Done! Updating UI now.")
            for widget in widgets_download_info:
                widget.destroy()
        # If not, we wait and cast again this function
        else:
            # a delay of 100ms is done just to keep the GUI chill
            self.parent.after(
                100, self.wait_to_kill_progress_bar, stop_signal, widgets_download_info
            )

    """
        TEMPLATES
    """

    # Base template for downloads feedback
    def template_downloading_info(self):
        # Guardaremos en una lista los widgets de dicho template
        # para poder elinarlos al terminar la descarga
        widgets_download_info = []

        self.canva3 = ctk.CTkCanvas(
            self,
            bg=self.color_bg_to_canvas_label,
            width=435,
            height=147,
            highlightthickness=0,
            borderwidth=0,
            bd=6,
            relief="solid",
        )
        self.canva3.place(x=22, y=446)
        widgets_download_info.append(self.canva3)

        # Cargo la imagen ya con placeholder
        self.img = Image.open("img.png")
        # Redimenciono al deseado
        self.img = self.img.resize((135, 83), Image.LANCZOS)
        # Se carga como un elemento para tkinter
        self.python_image = ctk.CTkImage(
            light_image=self.img, dark_image=self.img, size=(135, 83)
        )

        # Lo defino y presento como un Label, parece que es la unica forma de presentar imagenes
        self.label_image = ctk.CTkLabel(self.canva3, image=self.python_image, text="")
        self.label_image.place(x=43, y=10)
        widgets_download_info.append(self.label_image)

        # LABELS FOR DOWNLOAD FEEDBACK
        self.filename = ctk.CTkLabel(
            self.canva3,
            text=self.data["filename"][self.os_factor],
            justify="left",
            width=50,
            anchor="w",
            wraplength=350,
        )
        self.filename.place(x=21, y=103)
        widgets_download_info.append(self.filename)

        # Seccion BARRA DE PROGRESO
        self.progress = ttk.Progressbar(
            self.canva3,
            length=200,
        )
        self.progress.place(x=214, y=22)
        widgets_download_info.append(self.progress)

        # LABELS FOR DOWNLOAD FEEDBACK
        self.speed = ctk.CTkLabel(
            self.canva3,
            text=self.data["label_speed_pre_download"][self.os_factor],
            justify="center",
            width=205,
        )
        self.speed.place(x=217, y=58)
        widgets_download_info.append(self.speed)

        return widgets_download_info

    # Template for URL section
    def template_url_section(self):
        self.canva1 = ctk.CTkCanvas(
            self,
            bg=self.color_bg_to_canvas_label,
            width=460,
            height=177,
            highlightthickness=0,
            borderwidth=0,
        )
        self.canva1.place(x=9, y=20)

        # Seccion URL
        self.label_URL = ctk.CTkLabel(self.canva1, text="URL")
        self.label_URL.place(x=15, y=6)

        # Seccion entrada de texto para el URL al procesar por el AGYD
        self.urlTP = ctk.CTkEntry(self.canva1, width=429, height=43)
        self.urlTP.place(x=17, y=37)

        # Seccion RUTA
        self.label_path = ctk.CTkLabel(
            self.canva1,
            text=self.data["ruta_descarga"][self.os_factor],
            anchor="center",
            width=460,
            height=24,
        )
        self.label_path.place(x=0, y=98)
        self.ids = self.ids + 1
        self.labels_in_tkikter[self.ids] = {
            "widget": self.label_path,
            "lang": "ruta_descarga",
        }

        # Seccion del boton para decidir la ruta de descarga
        self.pathB = ctk.CTkButton(
            self.canva1,
            text=self.data["button_path"][self.os_factor],
            command=self.path_finder,
            width=157,
            height=31,
        )
        self.pathB.place(x=17, y=134)
        self.ids = self.ids + 1
        self.labels_in_tkikter[self.ids] = {
            "widget": self.pathB,
            "lang": "button_path",
        }

        # Seccion del label que muestra la rita de descarga
        # Por defecto, mostrara la ruta del AGYD
        self.rutaT = ctk.CTkLabel(
            self.canva1,
            text=os.getcwd(),
            width=275,
            height=44,
        )
        self.rutaT.place(x=180, y=128)

    # Template for download pref section
    def template_download_pref(self):
        self.canva2 = ctk.CTkCanvas(
            self,
            bg=self.color_bg_to_canvas_label,
            width=460,
            height=165,
            highlightthickness=0,
            borderwidth=0,
        )
        self.canva2.place(x=10, y=208)

        # -- Botones defaults
        # Label de los presets
        self.label_preset = ctk.CTkLabel(
            self.canva2,
            text=self.data["label_preset"][self.os_factor],
            anchor="center",
            width=460,
            height=24,
        )
        self.label_preset.place(x=0, y=10)
        self.ids = self.ids + 1
        self.labels_in_tkikter[self.ids] = {
            "widget": self.label_preset,
            "lang": "label_preset",
        }

        # Seccion Audio Default Preset
        self.audio_default_button = ctk.CTkButton(
            self.canva2,
            text=self.data["button_preset_audio"][self.os_factor],
            command=self.audio_default,
            width=201,
            height=54,
        )
        self.audio_default_button.place(x=17, y=44)
        self.ids = self.ids + 1
        self.labels_in_tkikter[self.ids] = {
            "widget": self.audio_default_button,
            "lang": "button_preset_audio",
        }

        # Seccion Video Default Preset
        self.video_default_button = ctk.CTkButton(
            self.canva2,
            text=self.data["button_preset_video"][self.os_factor],
            command=self.video_default,
            width=201,
            height=54,
        )
        self.video_default_button.place(x=247, y=44)
        self.ids = self.ids + 1
        self.labels_in_tkikter[self.ids] = {
            "widget": self.video_default_button,
            "lang": "button_preset_video",
        }

        # Seccion Feedback User what_is_downloading
        self.preset_selected = ctk.CTkLabel(
            self.canva2,
            text=self.data["label_preset_elegido"][self.os_factor],
            justify="center",
            width=327,
            height=38,
        )
        self.preset_selected.place(x=0, y=117)
        self.ids = self.ids + 1
        self.labels_in_tkikter[self.ids] = {
            "widget": self.preset_selected,
            "lang": "label_preset_elegido",
        }

        # Seccion Feedback User what_is_downloading
        self.what_is_downloading = ctk.CTkLabel(self.canva2, text="Audio")
        self.what_is_downloading.place(x=327, y=124)

    # Template on the menus
    def template_tk_menus(self, parent):
        """
        Top Menu
        """
        # Se crea la variable asociada al
        self.menu_bar = tk.Menu(parent)

        # Se añade la opcion asociada al switch del menu oscuro y diurno
        self.menu_bar.add_command(
            label=self.data["menubar_dark_light"][self.os_factor],
            command=self.change_theme,
        )

        self.menu_bar.add_command(
            label="English / Español",
            command=self.change_language,
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
            label=self.data["context_menu_option_paste"][self.os_factor],
            command=self.contextM_paste,
        )
        self.context_menu.add_command(
            label=self.data["context_menu_option_copy"][self.os_factor],
            command=self.contextM_copy,
        )
        # Se asocia los comportamientos ocurridos con el menu contextual
        # A la bandeja de texto
        self.urlTP.bind("<Button-3>", self.popup)

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
            try:
                self.canva3.config(bg=self.color_bg_to_canvas_label)
            except:
                print("Canva for download info no avaleble")
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
            try:
                self.canva3.config(bg=self.color_bg_to_canvas_label)
            except:
                print("Canva for download info no avaleble")

    def change_language(self):
        # Si el negativo no es el principal, no quedara negativo al ser 0, obviamente
        if self.os_factor == "es":
            self.os_factor = "en"
        else:
            self.os_factor = "es"

        # Pasamos por cada widget del tkinter registrado y lo modificamos
        # Por lo que si, esta seccion de codigo sirve para muchas otras cosas
        for widget in self.labels_in_tkikter.values():
            current_widget = widget["widget"]
            current_lang = widget["lang"]

            current_widget.configure(
                text=self.data[current_lang][self.os_factor],
            )

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
