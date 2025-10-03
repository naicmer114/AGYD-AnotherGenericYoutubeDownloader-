from tkinter import Tk
from tkinter import Label
from tkinter import ttk
from tkinter import IntVar
from tkinter import Checkbutton
from tkinter import Button
from tkinter import Entry
from tkinter import filedialog
from down import download
# AnotherGenericYoutubeDownloader (AGYD)
# si no se coloca ruta se usa la del programa, si no se declara play list solo se baja una
def res(): # existe para ser llamado por el submit y diversos tratos
    pre_formato = "" # precacheo para:
    if (video.get() == 0): # que si el boton de "video" no esta maracado entonces tomo en cuenta el formato de audio, si no entonces significa que es un video, por lo que paso el formato vacio para que al momento de la descarga se detecte que es un video (logica interna)
        pre_formato = formato.get()

    download(urlTP.get(), rutaT.cget("text"), video.get(),pre_formato, calidad.get())
    pre_formato=""
    #se hace video.get() a una variable a pesar de no ser el objeto ya que IntVar() es la forma en la que "es en lo q esta progamado Tkinter", asi q accedes al comportamiento del objeto al designarle un destino explisito

def path_finder():
    rutaT.config(text= filedialog.askdirectory(
        title = "Elija la ruta de descarga"        
        )
    ) # config es como para reescribir los parametros, q loco

main = Tk()
main.title('AGYD')
Label(main, text = "URL").grid(row=0)
Label(main, text = "Video").grid(row=1)
Label(main, text = "DEF: Audio").grid(row=1, column=2)
Label(main, text = "Formato").grid(row=2)
Label(main, text = "DEF: m4a (Audio) / mp4 (Video)").grid(row=2, column=2)
Label(main, text = "Ruta").grid(row=3)
rutaT = Label(main, text = "/././.")
rutaT.grid(row=3,column=2) # se coloca aparte pq si no es como si no tuviera ubicacion, entonces su ubicacion relativa queda como "None", por lo q no hay sujeto
Label(main, text = "Calidad").grid(row=4)
Label(main, text = "DEF: Alta").grid(row=4, column=2)

formato = ttk.Combobox(main, values = ['m4a'], state = 'readonly') # Podria ser el codec
formato.grid(row=2, column = 1)
calidad = ttk.Combobox(main, values = ['Alta','Baja'], state = 'readonly')
calidad.grid(row=4, column = 1)

video = IntVar()# Container
videoC = Checkbutton(main, text = '',variable = video)
videoC.grid(row = 1, column = 1) # Presentacion

pathB = Button(main, text = "Buscar", command = path_finder).grid(row = 3, column = 1)

urlTP = Entry(main)
urlTP.grid(row = 0, column=1)

submit = Button(main, text = "Descargar", command = res) # sin parentesis pq si no se considera un llamado injectado
submit.grid(row = 5)

main.mainloop()