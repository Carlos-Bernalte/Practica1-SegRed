# Seguridad en redes

	Practica 1: Alice y Bob
	


# Alice y Bob: ¿Qué hacen?
Una vez descargados los archivos desde el campus virtual, damos permisos de ejecución con 'chmod' para comprobar su funcionalidad. A simple vista, no parece ocurrir nada en pantalla, ejecutamos '$file alice' para obtener mas información pero no vemos nada relevante a simple vista.

El siguiente pensamiento es intentar averiguar el funcionamiento mediante ingeniería inversa, para esto descargamos el programa "GHidra", un programa que nos permite averiguar más sobre los archivos. Usamos la opción "CodeBrowser" de Ghidra para intentar ver el código fuente de los programas, conseguimos ver el código fuente del ambos ejecutables pero no comprendemos el funcionamiento exacto del programa debido a que las variables que se muestran no son nada descriptivas.
![Captura de Pantalla de Ghidra cuando analizas Alice](https://github.com/Carlos-Bernalte/Practica1/blob/master/doc/CapturaGHidra.PNG)

Decidimos entonces ejecutar ambos programas con Wireshark abierto para comprobar si hay comunicación entre ellos. Rápidamente podemos comprobar que uno de los programas, en este caso Alice, se conecta a "gitlab" mediante una petición DNS, y "gitlab" responde con una IP en la que se lleva a cabo una sesión TLS v1.3 donde "gitlab" manda información a Alice.
![Captura de wireshark del tráfico entre Alice y Gitlab](https://github.com/Carlos-Bernalte/Practica1/blob/master/doc/WiresharkAlice.PNG)
Una vez la comunicación termina, Alice comienza a enviar información a Bob a través de su puerto 12345, esta información esta encriptada lo que no permite su lectura rápida. Usando la herramienta "Seguir Flujo TCP" de wireshark podemos ver toda la información enviada, a la que Bob responde con "OK" constantemente.

Después de usar múltiples herramientas online para intentar desencriptar la información comprobamos que se trata de un cifrado Cesar con rotación 8, 





## Suplantando a bob

Asumiendo que, la única manera de saber que ocurre entre Alice y Gitlab seria mediante un proxy, decidimos intentar suplantar a Bob para entender mejor el funcionamiento y su interacción. Usando la interfaz loopback(127.0.0.1) y el puerto 12345 Alice comenzará a enviar información a nuestro programa, que hemos llamado Bobby.
Bobby descargará todo lo que reciba en un fichero.txt aplicando la desencriptación correspondiente a ROT-8. En el último paquete tcp se recibe "FinDeLaTransmisión" esta señal hará que Bobby deje de ejecutarse, terminando la conexión, como Alice y Bob deben ejecutarse a la vez para funcionar, Alice también dejara de funcionar.

##  El mensaje y funcionamiento.

Una vez aplicada la desencriptación podemos ver que se trata del texto correspondiente al Quijote de Miguel de Cervantes. 

En cuanto al funcionamiento, dado que no podemos interceptar la conexion entre Alice y Gitlab por que usan TLS v1.3, deducimos que Alice obtiene el texto del Quijote de Gitlab, y una vez recibido se lo reenvía a Bob mediante la interfaz loopback. 
![Diagrama mostrando el funcionamiento e interacción entre los programas y gitlab](https://github.com/Carlos-Bernalte/Practica1/blob/master/doc/comuni.drawio.png)
