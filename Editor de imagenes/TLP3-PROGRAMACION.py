
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance
from io import BytesIO
from email.message import EmailMessage
import smtplib
import winsound
import re

# Programa
class EditorImagenes:
     # Ventana
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Editor de Imágenes")
        self.ventana.geometry("1100x750")

        # Variables
        self.imagen = None# Almacena la imagen
        self.propuesta = None
        self.historial = []# Almacena imágenes anteriores para deshacer cambios
        self.rehacer_historial = []# Almacena imágenes anteriores para rehacer cambios
        self.foto = None
        self.seleccion_inicio = None
        self.rectangulo = None
        self.factor = 1
        self.offset_x = 0
        self.offset_y = 0

        self.crear_interfaz()

    # INTERFAZ

    def crear_interfaz(self):
        # Panel lateral
        contenedor = tk.Frame(self.ventana)
        contenedor.pack(side="left", fill="y", padx=10, pady=10)
        
        # Barra desplazable
        lienzo = tk.Canvas(
            contenedor, width=210, height=680,
            highlightthickness=0
        )
        barra = tk.Scrollbar(
            contenedor, orient="vertical", command=lienzo.yview
        )

        self.panel = tk.Frame(lienzo)
        ventana_panel = lienzo.create_window(
            (0, 0), window=self.panel, anchor="nw"
        )

        self.panel.bind(
            "<Configure>",
            lambda e: lienzo.configure(scrollregion=lienzo.bbox("all"))
        )
        lienzo.bind(
            "<Configure>",
            lambda e: lienzo.itemconfigure(ventana_panel, width=e.width)
        )
        lienzo.configure(yscrollcommand=barra.set)

        lienzo.pack(side="left", fill="y", expand=True)
        barra.pack(side="right", fill="y")

        # Botones
        self.boton_seccion("ARCHIVO")# Titulo
        self.boton("Abrir imagen", self.abrir)
        self.boton("Guardar imagen", self.guardar)

        self.boton_seccion("TRANSFORMACIONES")# Titulo
        self.boton("Girar izquierda", lambda: self.transformar(Image.Transpose.ROTATE_90))
        self.boton("Girar derecha", lambda: self.transformar(Image.Transpose.ROTATE_270))
        self.boton("Voltear horizontal", lambda: self.transformar(Image.Transpose.FLIP_LEFT_RIGHT))
        self.boton("Voltear vertical", lambda: self.transformar(Image.Transpose.FLIP_TOP_BOTTOM))
        self.boton("Escala de grises", self.grises)
        self.boton("Blanco y negro", self.blanco_negro)

        self.boton_seccion("FILTROS")# Titulo
        self.boton("Desenfoque", lambda: self.filtrar(ImageFilter.BLUR))
        self.boton("Nitidez", lambda: self.filtrar(ImageFilter.SHARPEN))
        self.boton("Bordes", lambda: self.filtrar(ImageFilter.FIND_EDGES))
        self.boton("Negativo", self.negativo)

        self.boton_seccion("AJUSTES")# Titulo
        self.crear_ajuste("Brillo", "brillo")
        self.crear_ajuste("Contraste", "contraste")
        self.crear_ajuste("Saturación", "saturacion")
        self.boton("Aplicar ajustes", self.aplicar_ajustes)

        self.boton_seccion("OTRAS FUNCIONES")# Titulo
        self.boton("Recortar imagen", self.activar_recorte)
        self.boton("Deshacer", self.deshacer)
        self.boton("Rehacer", self.rehacer)
        self.boton("Enviar por correo", self.correo)

        self.area = tk.Canvas(self.ventana, bg="#333333")
        self.area.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.area.bind("<Configure>", lambda e: self.mostrar())
        self.area.bind("<ButtonPress-1>", self.iniciar_recorte)
        self.area.bind("<B1-Motion>", self.dibujar_recorte)
        self.area.bind("<ButtonRelease-1>", self.terminar_recorte)

    def boton_seccion(self, texto):
        tk.Label(
            self.panel, text=texto,
            font=("Arial", 10, "bold")
        ).pack(pady=(12, 4))

    def boton(self, texto, funcion):
        tk.Button(
            self.panel, text=texto,
            command=funcion, width=22
        ).pack(pady=2)

    def crear_ajuste(self, texto, nombre):
        tk.Label(self.panel, text=texto).pack(pady=(5, 0))

        escala = tk.Scale(
            self.panel, from_=0, to=2,
            resolution=0.1, orient="horizontal",
            length=170
        )
        escala.set(1)
        escala.pack()

        setattr(self, nombre, escala)

    # IMAGEN

    def abrir(self):
        ruta = filedialog.askopenfilename(#Seleccion de imagen
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )

        if ruta:
            try:
                imagen = Image.open(ruta).convert("RGB")# Abre el explorador de archivos
                self.imagen = imagen
                self.historial.clear()
                self.rehacer_historial.clear()
                self.mostrar()
            except Exception as error:
                messagebox.showerror("Error", str(error))

    def guardar(self):
        if self.imagen is None:
            messagebox.showwarning("Aviso", "Primero abre una imagen.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPG", "*.jpg"),
                ("BMP", "*.bmp")
            ]
        )

        if ruta:
            try:
                self.imagen.save(ruta)
                messagebox.showinfo("Correcto", "Imagen guardada.")
            except Exception as error:
                messagebox.showerror("Error", str(error))

    def mostrar(self):
        if self.imagen is None:
            return

        imagen = self.imagen.copy()
        ancho, alto = self.area.winfo_width(), self.area.winfo_height()

        if ancho < 20 or alto < 20:
            return

        imagen.thumbnail((ancho - 20, alto - 20))

        self.factor = imagen.width / self.imagen.width
        self.offset_x = (ancho - imagen.width) / 2
        self.offset_y = (alto - imagen.height) / 2

        self.foto = ImageTk.PhotoImage(imagen)
        self.area.delete("all")
        self.area.create_image(
            self.offset_x, self.offset_y,
            image=self.foto, anchor="nw"
        )

    # VISTA PREVIA Y CONFIRMACIÓN

    def previsualizar(self, nueva):
        if self.imagen is None:
            return

        self.propuesta = nueva

        ventana = tk.Toplevel(self.ventana)
        ventana.title("Vista previa")
        ventana.geometry("700x430")

        tk.Label(ventana, text="Imagen original").grid(row=0, column=0)
        tk.Label(ventana, text="Imagen modificada").grid(row=0, column=1)

        original = self.imagen.copy()
        modificada = nueva.copy()
        original.thumbnail((320, 300))
        modificada.thumbnail((320, 300))

        foto_original = ImageTk.PhotoImage(original)
        foto_nueva = ImageTk.PhotoImage(modificada)

        etiqueta1 = tk.Label(ventana, image=foto_original)
        etiqueta1.image = foto_original
        etiqueta1.grid(row=1, column=0, padx=10, pady=10)

        etiqueta2 = tk.Label(ventana, image=foto_nueva)
        etiqueta2.image = foto_nueva
        etiqueta2.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(
            ventana, text="Confirmar",
            command=lambda: self.confirmar(ventana)
        ).grid(row=2, column=0, pady=10)

        tk.Button(
            ventana, text="Cancelar",
            command=ventana.destroy
        ).grid(row=2, column=1, pady=10)

    def confirmar(self, ventana):
        if self.propuesta is not None:
            self.historial.append(self.imagen.copy())
            self.rehacer_historial.clear()
            self.imagen = self.propuesta
            self.propuesta = None
            self.mostrar()

            try:
                winsound.Beep(1000, 300)
            except RuntimeError:
                pass

        ventana.destroy()

    # TRANSFORMACIONES

    def transformar(self, operacion):
        if self.imagen is not None:
            self.previsualizar(self.imagen.transpose(operacion))

    def grises(self):
        if self.imagen is not None:
            self.previsualizar(ImageOps.grayscale(self.imagen).convert("RGB"))

    def blanco_negro(self):
        if self.imagen is not None:
            nueva = ImageOps.grayscale(self.imagen).point(
                lambda p: 255 if p > 128 else 0
            )
            self.previsualizar(nueva.convert("RGB"))

    def negativo(self):
        if self.imagen is not None:
            self.previsualizar(ImageOps.invert(self.imagen))

    # FILTROS Y AJUSTES

    def filtrar(self, filtro):
        if self.imagen is not None:
            self.previsualizar(self.imagen.filter(filtro))

    def aplicar_ajustes(self):
        if self.imagen is None:
            return

        nueva = self.imagen.copy()
        nueva = ImageEnhance.Brightness(nueva).enhance(self.brillo.get())
        nueva = ImageEnhance.Contrast(nueva).enhance(self.contraste.get())
        nueva = ImageEnhance.Color(nueva).enhance(self.saturacion.get())

        self.previsualizar(nueva)

    # RECORTE

    def activar_recorte(self):
        if self.imagen is None:
            messagebox.showwarning("Aviso", "Primero abre una imagen.")
            return

        messagebox.showinfo(
            "Recortar",
            "Arrastra el mouse sobre la imagen para seleccionar el área."
        )

    def iniciar_recorte(self, evento):
        if self.imagen is None:
            return

        self.seleccion_inicio = (evento.x, evento.y)

        if self.rectangulo:
            self.area.delete(self.rectangulo)

        self.rectangulo = self.area.create_rectangle(
            evento.x, evento.y, evento.x, evento.y,
            outline="yellow", width=2
        )

    def dibujar_recorte(self, evento):
        if self.seleccion_inicio and self.rectangulo:
            x, y = self.seleccion_inicio
            self.area.coords(self.rectangulo, x, y, evento.x, evento.y)

    def terminar_recorte(self, evento):
        if self.imagen is None or self.seleccion_inicio is None:
            return

        x1, y1 = self.seleccion_inicio
        x2, y2 = evento.x, evento.y
        self.seleccion_inicio = None

        izquierda = int((min(x1, x2) - self.offset_x) / self.factor)
        superior = int((min(y1, y2) - self.offset_y) / self.factor)
        derecha = int((max(x1, x2) - self.offset_x) / self.factor)
        inferior = int((max(y1, y2) - self.offset_y) / self.factor)

        izquierda = max(0, izquierda)
        superior = max(0, superior)
        derecha = min(self.imagen.width, derecha)
        inferior = min(self.imagen.height, inferior)

        if derecha > izquierda and inferior > superior:
            self.previsualizar(
                self.imagen.crop((izquierda, superior, derecha, inferior))
            )

        if self.rectangulo:
            self.area.delete(self.rectangulo)
            self.rectangulo = None

    # DESHACER Y REHACER

    def deshacer(self):
        if self.historial:
            self.rehacer_historial.append(self.imagen.copy())
            self.imagen = self.historial.pop()
            self.mostrar()

    def rehacer(self):
        if self.rehacer_historial:
            self.historial.append(self.imagen.copy())
            self.imagen = self.rehacer_historial.pop()
            self.mostrar()

    # ENVÍO DE CORREO

    def correo(self):
        if self.imagen is None:
            messagebox.showwarning("Aviso", "Primero abre una imagen.")
            return

        ventana = tk.Toplevel(self.ventana)
        ventana.title("Enviar imagen por Gmail")
        ventana.geometry("430x540")
        ventana.resizable(False, False)

        tk.Label(ventana, text="Correo del destinatario:").pack(pady=(10, 0))
        destinatario = tk.Entry(ventana, width=48)
        destinatario.pack()

        tk.Label(ventana, text="Tu dirección de Gmail:").pack(pady=(10, 0))
        remitente = tk.Entry(ventana, width=48)
        remitente.pack()

        tk.Label(ventana, text="Contraseña de aplicación:").pack(pady=(10, 0))
        clave = tk.Entry(ventana, width=48, show="*")
        clave.pack()

        tk.Label(ventana, text="Asunto:").pack(pady=(10, 0))
        asunto = tk.Entry(ventana, width=48)
        asunto.insert(0, "Imagen enviada desde el Editor de Imágenes")
        asunto.pack()

        tk.Label(ventana, text="Mensaje:").pack(pady=(10, 0))
        mensaje = tk.Text(ventana, width=48, height=9)
        mensaje.insert("1.0", "Te envío la imagen editada.")
        mensaje.pack()

        def enviar():
            destino = destinatario.get().strip()
            origen = remitente.get().strip()
            contrasena = clave.get().strip()
            titulo = asunto.get().strip()
            texto = mensaje.get("1.0", "end-1c").strip()

            patron = r"^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$"

            if not destino or not origen or not contrasena:
                messagebox.showwarning(
                    "Aviso", "Completa los datos del correo."
                )
                return

            if not re.match(patron, destino) or not re.match(patron, origen):
                messagebox.showwarning(
                    "Aviso", "Revisa las direcciones de correo."
                )
                return

            try:
                archivo = BytesIO()
                self.imagen.save(archivo, format="PNG")

                if len(archivo.getvalue()) > 16 * 1024 * 1024:
                    archivo = BytesIO()
                    self.imagen.save(
                        archivo, format="JPEG", quality=75, optimize=True
                    )

                    if len(archivo.getvalue()) > 16 * 1024 * 1024:
                        messagebox.showerror(
                            "Error",
                            "La imagen sigue siendo demasiado grande."
                        )
                        return

                    messagebox.showwarning(
                        "Aviso",
                        "La imagen se comprimió para poder enviarla."
                    )

                correo = EmailMessage()
                correo["Subject"] = titulo or "Imagen editada"
                correo["From"] = origen
                correo["To"] = destino
                correo.set_content(texto or "Te envío la imagen editada.")

                es_png = archivo.getvalue().startswith(b"\x89PNG")

                correo.add_attachment(
                    archivo.getvalue(),
                    maintype="image",
                    subtype="png" if es_png else "jpeg",
                    filename="imagen.png" if es_png else "imagen.jpg"
                )

                with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as servidor:
                    servidor.starttls()
                    servidor.login(origen, contrasena)
                    servidor.send_message(correo)

                messagebox.showinfo(
                    "Correcto", "El correo se envió correctamente."
                )
                ventana.destroy()

            except smtplib.SMTPAuthenticationError:
                messagebox.showerror(
                    "Error",
                    "Gmail rechazó la contraseña. "
                    "Verifica que sea una contraseña de aplicación."
                )
            except Exception as error:
                messagebox.showerror(
                    "Error al enviar",
                    f"No se pudo enviar el correo:\n{error}"
                )

        tk.Button(
            ventana,
            text="ENVIAR CORREO",
            command=enviar,
            bg="#2196F3",
            fg="white",
            width=25,
            height=2
        ).pack(pady=15)


ventana = tk.Tk()
app = EditorImagenes(ventana)
ventana.mainloop()
