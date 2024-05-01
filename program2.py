import os # Importa el módulo os para interactuar con el sistema operativo.
import tkinter as tk # Importa el módulo tkinter para crear la interfaz gráfica de usuario (GUI).
from tkinter import * # Importa todas las clases y funciones de tkinter.
from tkinter import ttk # Importa ttk de tkinter para usar widgets con estilo.
from tkinter import scrolledtext # Importa scrolledtext de tkinter para usar áreas de texto con barras de desplazamiento.
import serial.tools.list_ports as ConectedPorts # Importa list_ports de serial.tools para listar los puertos serie disponibles.
import serial # Importa el módulo serial para la comunicación serie.
import time # Importa el módulo time para funciones relacionadas con el tiempo.
import threading # Importa el módulo threading para usar hilos.
import pandas as pd # Importa pandas para manipular y analizar datos.
from datetime import datetime # Importa datetime de datetime para trabajar con fechas y horas.
from tkinter import messagebox # Importa messagebox de tkinter para mostrar cuadros de mensaje.

isConectado = False  # Inicializa isConectado como False. Esta variable indica si el dispositivo está conectado.
PuertosDisponibles = [] # Inicializa PuertosDisponibles como una lista vacía. Esta lista almacenará los nombres de los puertos disponibles.
arduino = None # Inicializa arduino como None. Esta variable almacenará el objeto de conexión serie.
datos = [] # Inicializa datos como una lista vacía. Esta lista almacenará los datos leídos del puerto serie.
flagExtarerData = -1 # Inicializa flagExtarerData como -1. Esta variable se utiliza como una bandera para indicar cuándo se deben extraer los datos.

def listarPuertos(): # Define la función listarPuertos.
    ports = [] # Inicializa ports como una lista vacía.

    for port in ConectedPorts.comports(): # Itera sobre cada puerto en los puertos serie disponibles.
        ports.append(port.name) # Añade el nombre del puerto a la lista de puertos.

    print(ports) # Imprime la lista de puertos.
    return ports # Devuelve la lista de puertos.

def actualizarPuertos(): # Define la función actualizarPuertos.
    listaConexion.delete(0, END) # Borra todos los elementos del widget listaConexion.
    listaConexion.current() # Establece el elemento actual del widget listaConexion.
    puertos = ConectedPorts.comports() # Obtiene los puertos serie disponibles.
    try:
        listaConexion["values"]=[puerto.device for puerto in puertos] # Establece los valores del widget listaConexion a los nombres de los puertos serie disponibles.
        listaConexion.current(0) # Establece el elemento actual del widget listaConexion al primer puerto serie disponible.
    except:
        print("No hay dispositivos Conectados") # Imprime un mensaje si no hay dispositivos conectados.

def conectar(): # Define la función conectar.
    global isConectado # Declara isConectado como una variable global.
    global arduino # Declara arduino como una variable global.
    port = listaConexion.get() # Obtiene el puerto seleccionado del widget listaConexion.
    baudrate = 115200 # Establece la tasa de baudios a 115200.
    arduino = serial.Serial(port, baudrate) # Crea un objeto de conexión serie con el puerto y la tasa de baudios especificados.
    
    print(f"Conectado a {port} a {baudrate} baudios") # Imprime un mensaje indicando a qué puerto se ha conectado y a qué tasa de baudios.
    if isConectado == False: # Si no está conectado...
        isConectado = True # Establece isConectado como True.
        update_console() # Llama a la función update_console.

def read_serial_data(): # Define la función read_serial_data.
    """
    Lee los datos del puerto serial y los muestra en la consola de la GUI.
    """
    global arduino # Declara arduino como una variable global.
    try:
        data = arduino.readline().decode('utf-8').strip() # Lee una línea de datos del puerto serie, la decodifica como UTF-8 y elimina los espacios en blanco al principio y al final.
        #consola.insert(tk.END, data + '\n') # Inserta los datos leídos en el widget consola.
        print(data) # Imprime los datos leídos.
    except:
        print("No pudo leer") # Imprime un mensaje si no pudo leer los datos.

def update_console(): # Define la función update_console.
    """
    Actualiza la consola de la GUI cada 100 milisegundos.
    """
    global isConectado # Declara isConectado como una variable global.
    if isConectado == True: # Si está conectado...
        threading.Thread(target=arduino_handler, daemon=True).start() # Inicia un nuevo hilo que ejecuta la función arduino_handler.

def enviarDato(dato): # Define la función enviarDato.
    """Dato debe llegar en formato Byte"""
    global arduino # Declara arduino como una variable global.
    global flagExtarerData # Declara flagExtarerData como una variable global.
    if dato == b'S': # Si el dato es 'S'...
        datos.clear() # Borra todos los elementos de la lista datos.
        flagExtarerData = 1 # Establece flagExtarerData como 1.
    elif dato == b'T': # Si el dato es 'T'...
        flagExtarerData = 0 # Establece flagExtarerData como 0.
    arduino.write(dato) # Escribe el dato en el puerto serie.

def arduino_handler(): # Define la función arduino_handler.
    global arduino # Declara arduino como una variable global.
    global flagExtarerData # Declara flagExtarerData como una variable global.
    while True: # Mientras sea cierto...
        data = arduino.readline().decode('utf-8').strip() # Lee una línea de datos del puerto serie, la decodifica como UTF-8 y elimina los espacios en blanco al principio y al final.

        if flagExtarerData == 1: # Si flagExtarerData es 1...
            datos.append(data.split(',')) # Divide los datos por comas y añade los elementos resultantes a la lista datos.
        consola.insert(tk.END, data+"\n") # Inserta los datos leídos en el widget consola.
        consola.see("end") # Hace que el widget consola se desplace hasta el final.
        print(data) # Imprime los datos leídos.

def cambiarMuestra(): # Define la función cambiarMuestra.
    global isConectado # Declara isConectado como una variable global.
    global inMuestras # Declara inMuestras como una variable global.
    if isConectado == True: # Si está conectado...
        enviarDato(b'C') # Llama a la función enviarDato con 'C'.
        tiempo = inMuestras.get() # Obtiene el valor del widget inMuestras.
        time.sleep(0.2) # Duerme durante 0.2 segundos.
        enviarDato(tiempo.encode()) # Llama a la función enviarDato con el tiempo codificado.

def guardarArchivo(): # Define la función guardarArchivo.

    if flagExtarerData == 0 and isConectado == 1: # Si flagExtarerData es 0 y está conectado...
        df = pd.DataFrame(datos, columns=['Tiempo', 'Acel1', 'Acel2']) # Crea un DataFrame con los datos y las columnas especificadas.
        # Obtener la fecha y hora actual
        ahora = datetime.now() # Obtiene la fecha y hora actuales.
        
        # Formatear la fecha y hora como una cadena
        ahora_str = ahora.strftime('%Y-%m-%d_%H-%M-%S') # Formatea la fecha y hora actuales como una cadena.

        # Crear el nombre del archivo con la fecha y hora
        nombre_archivo = f'datos_arduino_{ahora_str}.xlsx' # Crea el nombre del archivo con la fecha y hora actuales.

        # Guardar el DataFrame en un archivo .xlsx
        df.to_excel(nombre_archivo, index=False) # Guarda el DataFrame en un archivo .xlsx.

        messagebox.showinfo("Guardar", f"Archivo Guardado correctamente {nombre_archivo}") # Muestra un cuadro de mensaje con la información de que el archivo se ha guardado correctamente.

#Antes de iniciar la interfaz mando a actualizar los puertos
#actualizarPuertos()
raiz = tk.Tk() # Crea la raíz de la GUI.
raiz.title("TecnoBot Sensor Sismometro") # Establece el título de la GUI.
if "nt" == os.name: # Si el sistema operativo es Windows...
    raiz.wm_iconbitmap(bitmap = "logo.ico") # Establece el icono de la GUI.
raiz.geometry("840x420") # Establece el tamaño de la GUI.
raiz.resizable(0,0) # Hace que la GUI no sea redimensionable.
frameTitulo = Frame(raiz) # Crea un Titulo

frameTitulo.pack(fill="x", side="top")
frameTitulo.config(height=100)
title = ttk.Label(frameTitulo, text="SENSOR SISMOMETRO", font=("Helvetica", 40)).pack(anchor="center", padx=50)

body = Frame(raiz) # Crea un nuevo marco llamado 'body' en la raíz de la GUI.
body.pack(padx=10, side="left", fill="both", expand=1, anchor="nw") # Empaqueta el marco 'body' con un padding de 10, alineado a la izquierda, llenando tanto el ancho como el alto.

frameHerramientas = Frame(body) # Crea un marco para las herramientas dentro del marco 'body'.
frameHerramientas.pack(fill="x") # Empaqueta el marco 'frameHerramientas' llenando el ancho.

frameConexion = Frame(frameHerramientas, height=50) # Crea un marco para la conexión dentro del marco de herramientas.
frameConexion.pack(padx=10, pady=10, side="left", expand = 1, anchor="center") # Empaqueta el marco 'frameConexion' con un padding de 10, alineado a la izquierda, expandiéndose para llenar el espacio disponible.

listaConexion = ttk.Combobox(frameConexion, values=PuertosDisponibles, state="readonly") # Crea un cuadro combinado para seleccionar entre los puertos disponibles.
listaConexion.pack(padx=5, side="left") # Empaqueta el cuadro combinado 'listaConexion' con un padding de 5, alineado a la izquierda.

botonRefresh = ttk.Button(frameConexion, text="Actualizar", command=actualizarPuertos) # Crea un botón para actualizar la lista de puertos disponibles.
botonRefresh.pack(side="left") # Empaqueta el botón 'botonRefresh' alineado a la izquierda.

botonConectar = ttk.Button(frameConexion, text="Conectar", command=lambda:conectar()) # Crea un botón para conectar al puerto seleccionado.
botonConectar.pack(side="left", padx=10) # Empaqueta el botón 'botonConectar' alineado a la izquierda con un padding de 10.

frameBotones = Frame(frameHerramientas, height=50) # Crea un marco para los botones dentro del marco de herramientas.
frameBotones.pack(side="left", anchor="center", expand = 1) # Empaqueta el marco 'frameBotones' alineado a la izquierda, centrado y expandiéndose para llenar el espacio disponible.

botonIniciar = ttk.Button(frameBotones, text="Iniciar", command=lambda:enviarDato(b'S')) # Crea un botón para iniciar la recopilación de datos.
botonIniciar.pack(side="left", padx=1) # Empaqueta el botón 'botonIniciar' alineado a la izquierda con un padding de 1.

botonDetener = ttk.Button(frameBotones, text="Detener", command=lambda:enviarDato(b'T')) # Crea un botón para detener la recopilación de datos.
botonDetener.pack(side="left", padx= 1) # Empaqueta el botón 'botonDetener' alineado a la izquierda con un padding de 1.

labelMuestras = Label(frameBotones, text="Tiempo muestreo (ms): ").pack(side="left") # Crea una etiqueta para el tiempo de muestreo y la empaqueta alineada a la izquierda.

inMuestras = ttk.Spinbox(frameBotones, from_ = 5, to=1500, justify="center", width=10, command=cambiarMuestra) # Crea un cuadro de entrada para ajustar el tiempo de muestreo.
inMuestras.pack(side="left") # Empaqueta el cuadro de entrada 'inMuestras' alineado a la izquierda.

botonGuardar = ttk.Button(frameBotones, text="Guardar Excel", command=guardarArchivo).pack(side="left") # Crea un botón para guardar los datos recogidos en un archivo Excel y lo empaqueta alineado a la izquierda.

frameConsola = Frame(body, background="black") # Crea un marco para la consola dentro del marco 'body'.
frameConsola.pack(side="top", fill="x", ipadx=20, ipady=20) # Empaqueta el marco 'frameConsola' en la parte superior, llenando el ancho y con un padding interno de 20.

consola = scrolledtext.ScrolledText(frameConsola) # Crea un área de texto desplazable para la consola.
consola.config(background="black", foreground="white", autoseparators=True ) # Configura el área de texto desplazable 'consola' con un fondo negro, texto blanco y separadores automáticos.
consola.pack(fill="x", expand=1) # Empaqueta el área de texto desplazable 'consola' llenando el ancho y expandiéndose para llenar el espacio disponible.

inMuestras.set(100) # Establece el valor inicial del cuadro de entrada 'inMuestras' en 100.

raiz.mainloop() # Inicia el bucle principal de la GUI, que espera eventos del usuario.
