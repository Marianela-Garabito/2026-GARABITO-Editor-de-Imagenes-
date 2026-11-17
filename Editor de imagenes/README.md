Editor de Imágenes desarrollado en Python como proyecto de Programación II.

Permite abrir, modificar, transformar y guardar imágenes mediante una interfaz gráfica.

|Funciones principales
- Abrir y guardar imágenes.
- Girar y voltear imágenes.
- Convertir imágenes a escala de grises y blanco y negro.
- Aplicar filtros.
- Modificar brillo, contraste y saturación.
- Recortar imágenes.
- Deshacer y rehacer modificaciones.
- Enviar imágenes por correo electrónico.
- Vista previa antes de confirmar los cambios.

|Tecnologías utilizadas
- Python
- Tkinter
- Pillow
- SMTP para el envío de correos

|Descargar el proyecto
Descargar o copiar los archivos del proyecto en una carpeta de la computadora.

La carpeta debe contener:

- editor_imagenes.py
- requirements.txt
- README.md

|Instalar las dependencias
1. Abrir la carpeta donde se encuentra el proyecto.
2. Hacer clic en la barra de direcciones del Explorador de archivos.
3. Escribir cmd y presionar Enter.
4. En la ventana de comandos, ejecutar:

   python -m pip install -r requirements.txt

5. Esperar a que finalice la instalación.

Este comando instala las bibliotecas externas necesarias para ejecutar el programa.

|Ejecutar el programa
Desde la misma ventana de CMD, escribir:

   python editor_imagenes.py

Presionar Enter para iniciar el editor de imágenes.

|Configurar el envío de correos

Para utilizar la función de envío por Gmail:

1. Tener una cuenta de Google.
2. Activar la verificación en dos pasos.
3. Crear una contraseña de aplicación desde la configuración de seguridad de Google, si la cuenta cumple los requisitos.
4. Abrir la función "Enviar por correo" del editor.
5. Introducir la dirección de Gmail, la contraseña de aplicación y el correo del destinatario.

La contraseña de aplicación debe ser propia de cada usuario. No se debe compartir con otras personas.

|Solución de problemas
- Si aparece un error relacionado con PIL, ejecutar nuevamente la instalación de las dependencias.
- Si no se pueden enviar correos, comprobar que la conexión a Internet, los datos de Gmail y la contraseña de aplicación sean correctos.
- Si Windows no reproduce sonidos, comprobar el volumen y la configuración de audio.
