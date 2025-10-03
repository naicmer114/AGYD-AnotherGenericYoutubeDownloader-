from yt_dlp import YoutubeDL
from ffmpeg import *
calidadL = ["Baja", "Alta"]
audioC = ["worstaudio", "bestaudio"]
videoC = ["worst", "best"]

def to_quality(calidad):
    for i in range(2):
            print(i)
            if calidadL[i] == calidad:   
                print(calidad + " Es igual a " + calidadL[i])
                print("calidad actual: " + calidad)
                return int(i)
                
def download(url, ruta, video, formato, calidad):
    cal_vid = videoC[1] # la calidad del video siempre sera la maxima
    if formato != "": # Para audio no predeterminado
        calidad = audioC[to_quality(calidad)]
    else: # Para video
        if(video == 1):
            formato = "mp4"
            conf_global = int(to_quality(calidad))
            calidad = audioC[conf_global]
            cal_vid = videoC[conf_global]
        else: # Predeterminado
            formato = "m4a"
    ydl_opts = {
    'format': formato+'/'+calidad+'/'+cal_vid,
    'outtmpl': ruta+'/Track: %(playlist_index)s - %(title)s.%(ext)s', #%(uploader)s - %(album)s - 
    'quiet': True, # Desactiva el output a consola
    'writethumbnail': True, # Se baja la portada
    'postprocessors': [  # Extract audio using ffmpeg
        {'key': 'FFmpegExtractAudio', # Separacion de audio del video para posprocesado 
         'preferredcodec': formato}, # Codec de audio/video a usar
        {'key': 'FFmpegMetadata'}, # Se incorpora la metadata de la cancion. Se hace primero ya que la portada se pierde al reescribir la metadata, mas no al revez
        {'key': 'EmbedThumbnail'}, # Se incorpora la portada al archivo
    ]
    }
    print("> Descargando")
    print(ydl_opts)
    print("-----------------------------")
    YoutubeDL(ydl_opts).download(url) # Usando el metodo YoutubeDL y dandole las configuraciones previas como parametros, se emplea su comportameniento de descargar (Download) dandole el url del video / playlist
    #print("> Finalizado -- wwwww --")
    #print("> Finalizado --  ///  --")
    #print("> Finalizado   wwwwwww  ")