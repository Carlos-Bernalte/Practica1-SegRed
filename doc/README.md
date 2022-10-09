


# Practica 1 - Seguridad en Redes


## Objetivo de la práctica

Averiguar el comportamiento de los programas **bob** y **alice** documentando todos los descubrimientos, avances e inconvenientes que vayan surgiendo.

## Primera fase de reconocimiento
En un principio intuíamos que eran dos ejecutables y gracias a la llamada al sistema `file` (que nos devuelve información respecto al tipo de archivo que es) lo verificamos junto al lenguaje de programación en el que fueron escritos.
```
$file alice
alice: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, Go 
BuildID=DKp9zbG5ZJznUelFDxTu/bUKt63Upb1jeKyAV24Io/xnXKp2aCyEh472PlF7p-/_GWCUHJZwx77fiyIEMtb, stripped
```
También tuvimos que darles permisos de ejecución
```
$ sudo chmod +x alice 
$ sudo chmod +x bob
```
A partir de aquí estuvimos jugando con su comportamiento cuando se ejecutaban,  como por ejemplo escribiendo en la terminal y nos dimos cuenta de que si ejecutábamos ambos a la vez y a alguno de los dos abortábamos su ejecución, el otro también finalizaba asumiendo así que había alguna comunicación entre ambos.

Decidimos entonces ejecutar ambos programas y escuchar con Wireshark para comprobar esa posible comunicación entre ellos. Rápidamente, podemos verificar que uno de los programas, en este caso Alice, se conecta a "GitLab" mediante una petición DNS, y "GitLab" responde con una IP en la que se lleva a cabo una sesión TLS v1.3 donde "GitLab" manda información a Alice.

 
![Captura de Wireshark del tráfico entre Alice y GitLab](https://github.com/Carlos-Bernalte/Practica1/blob/master/doc/WiresharkAlice.PNG)

Una vez la comunicación termina, Alice comienza a enviar información a Bob a través de su puerto **12345** (este puerto supimos que lo estaba ocupando alice gracias al comando `lsof`). Esta información que nos llegaba no podía ser interpretada de manera natural, por lo que dimos por sentado que estaba  codificada. Mientras que las respuestas de bob eran claros ''OK''. 


 `
 $ lsof -i -P -n| grep alice
 `

## Solución

Una idea que tuvimos fue sacar mediante webs que analizaban textos cifrados, posibles candidatos al algoritmo de cifrado que utiliza alice. Para ello teníamos que sacar muestras (los datos de los paquetes en Wireshark), el problema era que cuando quisimos exportar toda la conversación en el formato adecuado se demoraba demasiado, más de lo que tomaba realizar la conversación entera entre alice y bob. Pensando en ello decidimos implementar nuestro propio bob (**bobby**) el cual se encargaría en un principio de exportarnos toda la conversación y luego posteriormente descifrarla, también hubiésemos averiguado el algoritmo.

### Bobby
Viendo el comportamiento anteriormente mencionado en el que **alice** permanece a la escucha en el puerto **12345** y la función de **bob** es conectarse y recibir pues implementamos en Python el siguiente código (muestra de codigo simplificado sin tratamiento de excepciones):
```python
def  intentar_conexion():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('localhost', 12345))
		return s
	except  Exception  as e:
		print('Conectando...')
		return  None
		
def  main():  
	while  True:
		s =  intentar_conexion()
		if s:
			break
		time.sleep(1)
	while  True:
		data = s.recv(1024)
		datadesencriptado =  desencriptar(data.decode('raw_unicode_escape')
		if datadesencriptado ==  'FinDeLaTransmision':
			print('Fin de la comunicación')
			break
		escribir_archivo(datadesencriptado)
		s.send('OK'.encode())
	s.close()
```

Bob y descargará todo lo que reciba en un fichero bobby.txt aplicando el descifrado correspondiente. Recibirá en bucle En el último paquete TCP se recibe "*FinDeLaTransmisión*" esta señal hará que Bobby deje de ejecutarse, terminando la conexión, como Alice y Bob deben ejecutarse a la vez para funcionar, Alice también dejara de funcionar.
### Descubrir el cifrado
Ya que teníamos toda la conversación en texto plano, pasamos  a efectuar pruebas de análisis de texto cifrado en webs distintas, como por ejemplo [esta](https://web.archive.org/web/20120624074941/http://home.comcast.net/~acabion/refscore.html) que nos daba posibles candidatos de algoritmos, además de estadísticas acerca del texto analizado, o [dcode.fr](https://www.dcode.fr/cipher-identifier) que fue la que utilizamos al final puesto que también nos permitía decodificar con muchos  algoritmos en la propia página.
La manera de obtenerlo fue quedarnos con los algoritmos que más se repitiesen y probarlos con muestras de texto. 

La mayoría de los algoritmos que nos salían eran de rotación/desplazamiento y al final nos decantamos por el **ROT Cipher** con un valor de 8 de desplazamiento que era el valor que más cosas verosímiles nos daba. 

Una vez implementado la función en nuestro código **bobby** descubrimos que se trataba del  Quijote de Miguel de Cervantes.
```python
def  desencriptar(mensaje):
	'''Desencripta el mensaje'''
	mensaje_desencriptado =  ''
	for letra in mensaje:
		mensaje_desencriptado +=  chr(ord(letra)  -  8)
	return mensaje_desencriptado
```

## Diagrama de comunicaciones entre alice y bob

![Diagrama mostrando el funcionamiento e interacción entre los programas y GitLab](https://github.com/Carlos-Bernalte/Practica1/blob/master/doc/comuni.drawio.png)
## Ideas desechadas
La primera idea que tuvimos más vaga fue sacar el código fuente de alice y bob (mediante ingeniería inversa) para saber en qué estaba siendo codificada. Para esto descargamos el programa "GHidra", un programa que nos permite averiguar más sobre los archivos. Usamos la opción "CodeBrowser" de GHidra para intentar ver el código fuente de los programas, conseguimos ver el código fuente del ambos ejecutables, pero no comprendemos el funcionamiento exacto del programa debido a que las variables que se muestran no son nada descriptivas.

![Captura de Pantalla de GHidra cuando analizas Alice](https://github.com/Carlos-Bernalte/Practica1/blob/master/doc/CapturaGHidra.PNG)

También estuvimos revisando las primeras trazas en la conversación entre alice y bob para probar si salía alguna pista oculta, lo único que nos intrigaba era la comunicación al principio de alice con GitLab e intentamos implementar un Man In The Middle  configurando un proxy para que la información pasara por ahí y con la herramienta BurpSuit interceptarla. No conseguimos terminar de implementarla, puesto que empleaban TLS v1.3. De todo esto deducimos que Alice obtenía el texto del Quijote de GitLab, y una vez recibido se lo reenvía a Bob codificado.

## Enlaces
https://www.dcode.fr/cipher-identifier
https://www.dcode.fr/rot-cipher
https://web.archive.org/web/20120624074941/http://home.comcast.net/~acabion/refscore.html

Authors
:  [Carlos Bernalte García-Junco](https://github.com/Carlos-Bernalte)
:  [Angel García Collado](https://github.com/theangelogarci)
