import pandas as pd
import requests
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from io import BytesIO

# Variables globales
cartera_df = None
vencimientos_df = None

# Enlace directo de Google Drive para descargar el archivo en formato Excel
drive_link = "https://docs.google.com/spreadsheets/d/1-ph_TSfZQL2PFHlmuR--T2_C32JP9TJQ/export?format=xlsx"

# Función para descargar y cargar los datos desde Google Drive
def cargar_datos():
    global cartera_df, vencimientos_df
    try:
        print("Descargando archivo desde Google Drive...")  # Depuración
        response = requests.get(drive_link)
        response.raise_for_status()  # Verifica que la descarga fue exitosa

        # Leer el archivo Excel en memoria
        excel_data = BytesIO(response.content)
        xls = pd.ExcelFile(excel_data)

        # Listar las hojas disponibles
        print(f"Hojas disponibles: {xls.sheet_names}")  # Depuración

        # Cargar las hojas específicas en DataFrames
        cartera_df = pd.read_excel(xls, sheet_name="cartera")
        vencimientos_df = pd.read_excel(xls, sheet_name="vencimientos")

        # Imprimir las columnas disponibles en ambas hojas
        print(f"Columnas en 'cartera': {list(cartera_df.columns)}")  # Depuración
        print(f"Columnas en 'vencimientos': {list(vencimientos_df.columns)}")  # Depuración

        # Unir los DataFrames usando las columnas correctas
        merged_df = pd.merge(cartera_df, vencimientos_df, 
                             left_on="CODIGO_SAIDS", right_on="SAIDS")

        print("Datos cargados correctamente.")  # Depuración
        mostrar_vencimientos(merged_df)  # Mostrar los datos en la tabla
    except Exception as e:
        print(f"Error al cargar datos: {e}")  # Depuración
        messagebox.showerror("Error", f"Error al cargar datos: {e}")

# Función para mostrar los vencimientos en la tabla
def mostrar_vencimientos(merged_df):
    # Limpiar la tabla antes de mostrar nuevos datos
    for row in tree.get_children():
        tree.delete(row)

    # Obtener la fecha actual y el año en curso
    hoy = datetime.now()
    current_year = hoy.year

    # Filtrar y mostrar solo los vencimientos futuros más cercanos en esta gestión
    for codigo, grupo in merged_df.groupby("CODIGO_SAIDS"):
        # Filtrar las fechas futuras y que sean del año actual (2024)
        fechas_futuras = grupo[grupo["Vencimiento"].dt.year == current_year]
        fechas_futuras = fechas_futuras[fechas_futuras["Vencimiento"] >= hoy]

        # Si hay fechas futuras, mostramos solo la más cercana
        if not fechas_futuras.empty:
            fecha_mas_cercana = fechas_futuras["Vencimiento"].min()
            denominacion = grupo.iloc[0]["DENOMINACION_SEGUN_POA"]

            # Calcular los días restantes
            dias_restantes = calcular_dias_restantes(fecha_mas_cercana)

            # Insertar los datos en la tabla
            tree.insert(
                "", "end",
                values=(denominacion, fecha_mas_cercana.date(), dias_restantes)
            )

# Función para calcular los días restantes hasta el vencimiento
def calcular_dias_restantes(fecha_vencimiento):
    hoy = datetime.now()
    diferencia = (fecha_vencimiento - hoy).days
    return diferencia if diferencia >= 0 else "Vencido"



# Función para mostrar un gráfico de ejemplo
def mostrar_grafico():
    try:
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(["Proyecto A", "Proyecto B"], [30, 20], color="#198754")
        ax.set_title("Vencimientos Próximos")
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack()
    except Exception as e:
        print(f"Error al mostrar gráfico: {e}")
        messagebox.showerror("Error", f"Error al mostrar gráfico: {e}")

# Crear la ventana principal
app = ttk.Window(themename="superhero")
app.title("PizarraCP - Dashboard")
app.geometry("800x600")

# Encabezado
header = ttk.Label(app, text="UNIDAD DE CRÉDITO PÚBLICO", font=("Arial", 24, "bold"))
header.pack(pady=10)

# Sección de botones
frame_botones = ttk.Frame(app)
frame_botones.pack(pady=10)

btn_actualizar = ttk.Button(
    frame_botones, text="Actualizar", command=cargar_datos, bootstyle=INFO
)
btn_actualizar.grid(row=0, column=0, padx=10)

# Tabla para mostrar los datos
frame_tabla = ttk.Frame(app)
frame_tabla.pack(fill=BOTH, expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame_tabla, columns=("Denominacion", "Vencimiento", "Dias Restantes"), show="headings")
tree.heading("Denominacion", text="Denominación")
tree.heading("Vencimiento", text="Vencimiento")
tree.heading("Dias Restantes", text="Días Restantes")
tree.pack(fill=BOTH, expand=True)

# Sección para el gráfico
frame_grafico = ttk.Frame(app)
frame_grafico.pack(fill=BOTH, expand=True, padx=10, pady=10)

# Mostrar gráfico al iniciar
mostrar_grafico()

# Cargar los datos automáticamente al iniciar
print("Cargando datos al iniciar...")  # Depuración
cargar_datos()

# Iniciar la aplicación
print("Iniciando la interfaz...")  # Depuración
app.mainloop()
