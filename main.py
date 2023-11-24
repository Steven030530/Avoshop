import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import time
import warnings
warnings.simplefilter('ignore')
class TiendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("APP Avoshop")

        # Conexión a Google Sheets
        ruta_cred = os.path.abspath(os.path.join(os.getcwd(),'..')) + '/tienda-avocado-59578ea68206.json'
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.credenciales = ServiceAccountCredentials.from_json_keyfile_name(ruta_cred, self.scope)
        self.cliente = gspread.authorize(self.credenciales)
        self.hoja = self.cliente.open('Avoshop').sheet1
        # Variables
        self.opciones_combobox = ['Verde Pinton', 'Avocado']
        self.inventario_verde = self.cliente.open('Avoshop').worksheet('Inventario_Verde_Pinton')
        valores_verde = self.inventario_verde.get_all_values()
        self.productos_verde = {fila[0]: float(fila[2])*1000 for fila in valores_verde[1:]}
        self.inventario_avocado = self.cliente.open('Avoshop').worksheet('Inventario_Avocado')
        valores_avo = self.inventario_avocado.get_all_values()   
        self.productos_avo = {fila[0]: float(fila[2])*1000 for fila in valores_avo[1:]}
        self.ventas_worksheet = self.cliente.open('Avoshop').worksheet('Ventas')
        self.metodo_pago = tk.StringVar()
        # Interfaz de usuario
        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Configuración de la interfaz, como etiquetas, listboxes, botones, etc.
        
        # Centrar la ventana en la pantalla
        ancho_ventana = 800
        alto_ventana = 700

        # Obtener las dimensiones de la pantalla
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()

        # Calcular la posición para centrar la ventana
        x = (ancho_pantalla - ancho_ventana) // 2
        y = (alto_pantalla - alto_ventana) // 2

        # Establecer la geometría de la ventana
        self.root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
        self.root.resizable(False, False)
        titulo_label = tk.Label(self.root, text="Bienvenido al Avoshop", font=('Times New Roman', 26, 'bold'))
        titulo_label.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        # Etiqueta del vendedor
        etiqueta_vend = tk.Label(self.root, text='Elige una Tienda:', font=('Times New Roman',14))
        etiqueta_vend.pack(side=tk.TOP, padx=10, pady=5)
        # Combox Vendedor
        self.opcion_seleccionada = tk.StringVar()
        combobox = ttk.Combobox(self.root, textvariable=self.opcion_seleccionada, values=self.opciones_combobox,
                                font=('Times New Roman', 14, 'bold'),width=20,justify='center')
        combobox.pack(side=tk.TOP, padx=10, pady=10)
        combobox.bind("<<ComboboxSelected>>", self.actualizar_combobox_productos)
        #Etiqueta del producto
        etiqueta_prod = tk.Label(self.root, text='Elige un Producto:', font=('Times New Roman', 14))
        etiqueta_prod.pack(side=tk.TOP, padx=10, pady=5)
        # Combobox de productos
        self.combobox_productos = ttk.Combobox(self.root, state='readonly', font=('Times New Roman', 14, 'bold'),width=20,justify='center')
        self.combobox_productos.pack(side=tk.TOP, padx=10, pady=10)
        self.combobox_productos.bind("<<ComboboxSelected>>", self.mostrar_opcion_cantidad)
        #Etiqueta del cantidad
        etiqueta_prod = tk.Label(self.root, text='Cantidad:', font=('Times New Roman', 14))
        etiqueta_prod.pack(side=tk.TOP, padx=10, pady=5)
        # Entrada de cantidad
        self.entry_cantidad = tk.Entry(self.root, font=('Times New Roman', 14, 'bold'),width=10,justify="center")
        self.entry_cantidad.pack(side=tk.TOP, padx=10, pady=10)
        # Botón para calcular
        btn_calcular = tk.Button(self.root, text="Calcular", command=self.calcular_valor,bg="lightblue",font=('Times New Roman',14),width=10,height=1,pady=10)
        btn_calcular.pack(side=tk.TOP, padx=10, pady=10)
        #Resultados
        self.etiqueta_resultado = tk.Label(self.root, text='', font=('Times New Roman', 14))
        self.etiqueta_resultado.pack(side=tk.TOP, padx=10, pady=5)
         # Botón para registrar la venta
        btn_registrar_venta = tk.Button(self.root, text="Registrar Venta", command=self.solicitar_metodo_pago,bg="darkgreen",fg="white",width=20,height=3,font=('Times New Roman',14))
        btn_registrar_venta.pack(side=tk.LEFT, padx=100, pady=10)
        # Botón para cancelar la venta
        btn_cancelar_venta = tk.Button(self.root, text="Cancelar Venta", command=self.cancelar_venta,bg="darkred",fg="white",width=20,height=3,font=('Times New Roman',14))
        btn_cancelar_venta.pack(side=tk.RIGHT, padx=100, pady=10)

    def actualizar_combobox_productos(self, event):
        seleccion_vendedor = self.opcion_seleccionada.get()
        if seleccion_vendedor == 'Verde Pinton':
            productos = list(self.productos_verde.keys())
        elif seleccion_vendedor == 'Avocado':
            productos = list(self.productos_avo.keys())
        else:
            productos = []

        self.combobox_productos['values'] = productos

    def mostrar_opcion_cantidad(self, event):
        # Mostrar la opción de ingresar la cantidad después de seleccionar el producto
        self.entry_cantidad.delete(0, tk.END)
        self.etiqueta_resultado.config(text='')

    def calcular_valor(self):
        seleccion_vendedor = self.opcion_seleccionada.get()
        seleccion_producto = self.combobox_productos.get()
        cantidad = self.entry_cantidad.get()
        try:
            cantidad = float(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida.")
            return
        if seleccion_vendedor == 'Verde Pinton':
            precio_producto = self.productos_verde[seleccion_producto]
            
        elif seleccion_vendedor == 'Avocado':
            precio_producto = self.productos_avo[seleccion_producto]
            
        else:
            messagebox.showerror("Error", "Seleccione un vendedor válido.")
            return

        valor_total = cantidad * precio_producto
        self.etiqueta_resultado.config(text=f"Valor total a pagar: ${valor_total:,.0f}",font=('Times New Roman', 20, 'bold'),pady=10)
    
    def solicitar_metodo_pago(self):
        # Preguntar al usuario con qué método de pago desea realizar la venta
        opciones_metodo_pago = ['Efectivo', 'Transferencia']
        metodo_pago = simpledialog.askstring("Método de Pago", "¿Con qué método de pago desea realizar la venta?",
                                             parent=self.root, initialvalue='Efectivo')

        # Almacenar el método de pago en la variable
        if metodo_pago:
            self.metodo_pago.set(metodo_pago)
            # Llamar a la función para registrar la venta
            self.registrar_venta()

    def registrar_venta(self):
        # Obtener los datos necesarios
        seleccion_vendedor = self.opcion_seleccionada.get()
        seleccion_producto = self.combobox_productos.get()
        cantidad = self.entry_cantidad.get()
        fecha = datetime.now().strftime('%d/%m/%Y')
        metodo_pago = self.metodo_pago.get()
        try:
            cantidad = float(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida.")
            return

        if seleccion_vendedor == 'Verde Pinton':
            precio_producto = self.productos_verde[seleccion_producto]
        elif seleccion_vendedor == 'Avocado':
            precio_producto = self.productos_avo[seleccion_producto]
        else:
            messagebox.showerror("Error", "Seleccione un vendedor válido.")
            return

        valor_total = cantidad * precio_producto

        # Registrar la venta en la worksheet de ventas
        nueva_venta = [fecha,seleccion_producto,cantidad,precio_producto,valor_total,metodo_pago,seleccion_vendedor]
        self.ventas_worksheet.append_row(nueva_venta)

        # Reiniciar la interfaz
        self.opcion_seleccionada.set('')
        self.combobox_productos.set('')
        self.entry_cantidad.delete(0, tk.END)
        self.etiqueta_resultado.config(text='')

        messagebox.showinfo("Venta Registrada", "La venta ha sido registrada exitosamente.")

    def cancelar_venta(self):
        # Reiniciar la interfaz
        self.opcion_seleccionada.set('')
        self.combobox_productos.set('')
        self.entry_cantidad.delete(0, tk.END)
        self.etiqueta_resultado.config(text='')

if __name__ == "__main__":
    root = tk.Tk()
    app = TiendaApp(root)
    root.mainloop()
    