import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import serial.tools.list_ports as ConectedPorts
import serial
import time
import threading

isConectado = False 
PuertosDisponibles = []
arduino = None
def listarPuertos():
    ports = []

    for port in ConectedPorts.comports():
        ports.append(port.name)

    print(ports)
    return ports

def actualizarPuertos():
    listaConexion.delete(0, END)
    listaConexion.current()
    puertos = ConectedPorts.comports()
    try:
        listaConexion["values"]=[puerto.device for puerto in puertos]
        listaConexion.current(0)
    except:
        print("No hay dispositivos Conectados")

def conectar():
    global isConectado
    global arduino
    port = listaConexion.get()
    baudrate = 115200
    arduino = serial.Serial(port, baudrate)
    
    print(f"Conectado a {port} a {baudrate} baudios")
    if isConectado == False:
        isConectado = True
        update_console()

def read_serial_data():
    """
    Lee los datos del puerto serial y los muestra en la consola de la GUI.
    """
    global arduino
    try:
        data = arduino.readline().decode('utf-8').strip()
        #consola.insert(tk.END, data + '\n')
        print(data)
    except:
        print("No pudo leer")

def update_console():
    """
    Actualiza la consola de la GUI cada 100 milisegundos.
    """
    global isConectado
    if isConectado == True:
        threading.Thread(target=arduino_handler, daemon=True).start()

def enviarDato(dato):
    """Dato debe llegar en formato Byte"""
    global arduino
    arduino.write(dato)       

def arduino_handler():
    global arduino
    while True:
        data = arduino.readline().decode('utf-8').strip()
        print(data)

def cambiarMuestra():
    global isConectado
    global inMuestras
    if isConectado == True:
        enviarDato(b'C')
        tiempo = inMuestras.get()
        time.sleep(0.2)
        enviarDato(tiempo.encode())

#Antes de iniciar la interfaz mando a actualizar los puertos
#actualizarPuertos()
raiz = tk.Tk()
raiz.geometry("840x420") #Configurar tamaño
raiz.resizable(0,0)
frameTitulo = Frame(raiz)#pack()
frameTitulo.pack(fill="x", side="top")
frameTitulo.config(height=100)
title = ttk.Label(frameTitulo, text="SENSOR SISMOMETRO", font=("Helvetica", 40)).pack(anchor="center", padx=50)

body = Frame(raiz)#pack(side="top", fill="both")
body.pack(padx=10, side="left", fill="both", expand=1, anchor="nw")

frameHerramientas = Frame(body)
frameHerramientas.pack(fill="x")

frameConexion = Frame(frameHerramientas, height=50)#.place(x=50, y=100)#pack(fill="x", expand=1)
frameConexion.pack(padx=10, pady=10, side="left", expand = 1, anchor="center")

listaConexion = ttk.Combobox(frameConexion, values=PuertosDisponibles, state="readonly")#.pack(side="left", expand=1)
listaConexion.pack(padx=5, side="left")
#listaConexion.after(5000, actualizarPuertos)
botonRefresh = ttk.Button(frameConexion, text="Actualizar", command=actualizarPuertos)
botonRefresh.pack(side="left")
botonConectar = ttk.Button(frameConexion, text="Conectar", command=lambda:conectar())#
botonConectar.pack(side="left", padx=10)


frameBotones = Frame(frameHerramientas, height=50)
frameBotones.pack(side="left", anchor="center", expand = 1)
botonIniciar = ttk.Button(frameBotones, text="Iniciar", command=lambda:enviarDato(b'S'))#
botonIniciar.pack(side="left", padx=1)
botonDetener = ttk.Button(frameBotones, text="Detener", command=lambda:enviarDato(b'T'))#
botonDetener.pack(side="left", padx= 1)
labelMuestras = Label(frameBotones, text="Tiempo muestreo (ms): ").pack(side="left")
inMuestras = ttk.Spinbox(frameBotones, from_ = 5, to=1500, justify="center", width=10, command=cambiarMuestra)
inMuestras.pack(side="left")
botonGuardar = ttk.Button(frameBotones, text="Guardar Excel").pack(side="left")
#inMuestras.bind("<<increment>>", cambiarMuestra)
#inMuestras.bind("<<Decrement>>", cambiarMuestra)

frameConsola = Frame(body, background="black")
frameConsola.pack(side="top", fill="x", ipadx=20, ipady=20)
consola = scrolledtext.ScrolledText(frameConsola)
consola.config(background="black", foreground="white")
consola.pack(fill="x", expand=1)
inMuestras.set(100)
#update_console()
raiz.mainloop()
