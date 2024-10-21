from tkinter import messagebox

# Función para mostrar un mensaje de error
def mostrar_error(mensaje):
    messagebox.showerror("Error", mensaje)

# Función para mostrar un mensaje de éxito
def mostrar_exito(mensaje):
    messagebox.showinfo("Éxito", mensaje)
