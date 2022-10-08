#!/usr/bin/env python3
'''
    autor: Carlos Bernalte & Angel García
    fecha: 2022-10-08
    descripción: Suplantar el comportamiento de un del ejecutable 'bob' para
    que se comunique con el 'alice' y saque el mensaje oculto codificado en ROT-8.
'''
import socket
import sys
import time

def desencriptar(mensaje):
    '''Desencripta el mensaje'''
    mensaje_desencriptado = ''
    for letra in mensaje:
        mensaje_desencriptado += chr(ord(letra) - 8)
    return mensaje_desencriptado


def intentar_conexion():
    '''Intenta conectarse al servidor'''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 12345))
        return s
    except Exception as e:
        print('Conectando...')
        return None

def escribir_archivo(mensaje):
    '''Escribe el mensaje en un archivo de texto'''
    with open('bobby.txt', 'a') as archivo:
        archivo.write(mensaje)

def main():
    '''Borrar el contenido del archivo de texto en caso de que ya exista'''
    with open('bobby.txt', 'w') as archivo:
        archivo.truncate()

    '''Función principal'''
    try:
        while True:
            s = intentar_conexion()
            if s:
                break
            time.sleep(1)
        while True:
            data = s.recv(1024)

            datadesencriptado = desencriptar(data.decode('raw_unicode_escape'))

            if datadesencriptado == 'FinDeLaTransmision':
                print('Fin de la comunicación') 
                break

            escribir_archivo(datadesencriptado)
            s.send('OK'.encode())

    except BrokenPipeError:
        print('Conexión terminada por el servidor')
        s.close()
        sys.exit(0)
    finally:
        s.close()
    
if __name__ == '__main__':
    try:
        main() 
    except KeyboardInterrupt as e:
        print('Saliendo...')
        sys.exit(0)
