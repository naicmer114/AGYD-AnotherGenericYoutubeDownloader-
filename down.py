from yt_dlp import YoutubeDL
# https://music.youtube.com/watch?v=00v5Y_n9JN8&si=U1Ey5H8gaTGeNQNi
calidadL = ['Baja', 'Alta']
audio = ["worstaudio", "bestaudio"]
#video = ["worst", "best"]

def download(url, ruta, video, formato, calidad):
    if formato != "":
        for i in range(2):
            print(i)
            if calidadL[i] == calidad:   
                print(calidad + " Es igual a " + calidadL[i])
                calidad = audio[i]
                print("calidad actual: " + calidad)
                break
    else:
        if(video == 1):
            formato = "mp4"
            calidad = "bestaudio"
        else:
            formato = "mp3"
    ydl_opts = {
    'format': formato+'/'+calidad+'/best',
    #'format': 'm4a/bestaudio/best', # Se declara el formato y se especifica la calidad del audio
    'outtmpl': ruta+'/Track: %(playlist_index)s - %(title)s.%(ext)s', #%(uploader)s - %(album)s - 
    'quiet': False, # Desactiva el output a consola
    'writethumbnail': True, # Se baja la portada
    'postprocessors': [  # Extract audio using ffmpeg
        {'key': 'FFmpegExtractAudio',
         'preferredcodec': formato},
        
        {'key': 'FFmpegMetadata'}, # Se incorpora la metadata de la cancion. Se hace primero ya que la portada se pierde al reescribir la metadata, mas no al revez
        {'key': 'EmbedThumbnail'}, # Se incorpora la portada al archivo
    ]
    #'dump_single_json': True debugin de toda la metadata
    #'noplaylist': False para controlar si se trabaja con playlists
    }
    print("> Descargando")
    print(ydl_opts)
    print("-----------------------------")
    YoutubeDL(ydl_opts).download(url) # Usando el metodo YoutubeDL y dandole las configuraciones previas como parametros, se emplea su comportameniento de descargar (Download) dandole el url del video / playlist
    print("> Finalizado -- wwwww --")
    print("> Finalizado --  ///  --")
    print("> Finalizado   wwwwwww  ")