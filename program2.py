import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import serial.tools.list_ports as ConectedPorts
import serial
import time
import threading
import pandas as pd
from datetime import datetime
from tkinter import messagebox

isConectado = False 
PuertosDisponibles = []
arduino = None
datos = []
flagExtarerData = -1

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
    global flagExtarerData
    if dato == b'S':
        datos.clear()
        flagExtarerData = 1
    elif dato == b'T':
        flagExtarerData = 0
    arduino.write(dato)    

def arduino_handler():
    global arduino
    global flagExtarerData
    while True:
        data = arduino.readline().decode('utf-8').strip()

        if flagExtarerData == 1:
            datos.append(data.split(','))
        consola.insert(tk.END, data+"\n")
        consola.see("end")
        print(data)

def cambiarMuestra():
    global isConectado
    global inMuestras
    if isConectado == True:
        enviarDato(b'C')
        tiempo = inMuestras.get()
        time.sleep(0.2)
        enviarDato(tiempo.encode())

def guardarArchivo():

    if flagExtarerData == 0 and isConectado == 1:
        df = pd.DataFrame(datos, columns=['Tiempo', 'Acel1', 'Acel2'])
        # Obtener la fecha y hora actual
        ahora = datetime.now()
        
        # Formatear la fecha y hora como una cadena
        ahora_str = ahora.strftime('%Y-%m-%d_%H-%M-%S')

        # Crear el nombre del archivo con la fecha y hora
        nombre_archivo = f'datos_arduino_{ahora_str}.xlsx'

        # Guardar el DataFrame en un archivo .xlsx
        df.to_excel(nombre_archivo, index=False)

        messagebox.showinfo("Guardar", f"Archivo Guardado correctamente {nombre_archivo}")


#Antes de iniciar la interfaz mando a actualizar los puertos
#actualizarPuertos()
raiz = tk.Tk()
raiz.title("TecnoBot Sensor Sismometro")
if "nt" == os.name:
    raiz.wm_iconbitmap(bitmap = "logo.ico")
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
botonGuardar = ttk.Button(frameBotones, text="Guardar Excel", command=guardarArchivo).pack(side="left")



frameConsola = Frame(body, background="black")
frameConsola.pack(side="top", fill="x", ipadx=20, ipady=20)
consola = scrolledtext.ScrolledText(frameConsola)
consola.config(background="black", foreground="white", autoseparators=True )
consola.pack(fill="x", expand=1)
inMuestras.set(100)
#update_console()
raiz.mainloop()
