'''Que se conecte al puerto 12345 y reciva el mensaje encriptado y lo desencripte hasta que se reciba el mensaje "FIN"'''

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
    '''Función principal'''
    try:

        s = intentar_conexion()
        while s is None:
            time.sleep(1)
            s = intentar_conexion()

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
