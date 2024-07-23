import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from functools import partial

def main():
    global root, tree, search_entry, asistencia_filter_var, asis_entry
    
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Aplicación Tkinter")
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("%dx%d" % (width, height))

    # Crear el marco principal
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Crear un sub-marco para contener los filtros y botones
    top_frame = ttk.Frame(main_frame)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # Botón para añadir nuevo usuario
    plus_button = ttk.Button(top_frame, text="+", command=nuevo_usuario)
    plus_button.pack(side=tk.LEFT, padx=5)

    # Etiqueta y entrada para buscar códigos o nombres
    search_label = ttk.Label(top_frame, text="Buscar por Código o Nombre:")
    search_label.pack(side=tk.LEFT, padx=5)

    search_entry = ttk.Entry(top_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    search_button = ttk.Button(top_frame, text="Buscar", command=buscar_codigo_o_nombre)
    search_button.pack(side=tk.LEFT, padx=5)

    # Filtro de asistencia
    asistencia_filter_var = tk.IntVar(value=0)  # Inicializar con 0 (Mostrar todos)

    asistencia_frame = ttk.Frame(top_frame)
    asistencia_frame.pack(side=tk.LEFT, padx=10)

    # Radio buttons para filtrar por asistencia
    todos_radio = ttk.Radiobutton(asistencia_frame, text="Mostrar Todos", variable=asistencia_filter_var, value=0, command=actualizar_filtro_asistencia)
    todos_radio.pack(side=tk.LEFT, padx=5)

    asistido_radio = ttk.Radiobutton(asistencia_frame, text="Asistido", variable=asistencia_filter_var, value=1, command=actualizar_filtro_asistencia)
    asistido_radio.pack(side=tk.LEFT, padx=5)

    no_asistido_radio = ttk.Radiobutton(asistencia_frame, text="Sin Asistir", variable=asistencia_filter_var, value=2, command=actualizar_filtro_asistencia)
    no_asistido_radio.pack(side=tk.LEFT, padx=5)

    asis_button = ttk.Button(top_frame, text="✔", command=partial(registrar_asistencia, True))
    asis_button.pack(side=tk.LEFT, padx=5)
    notasis_button = ttk.Button(top_frame, text="X", command=partial(registrar_asistencia, False))
    notasis_button.pack(side=tk.LEFT, padx=5)

    delete_button = ttk.Button(top_frame, text="Eliminar Invitado", command=eliminar_invitado)
    delete_button.pack(side=tk.LEFT, padx=5)


    asis_label = ttk.Label(top_frame, text="Asistencia por código:")
    asis_label.pack(side=tk.LEFT, padx=5)

    asis_entry = ttk.Entry(top_frame)
    asis_entry.pack(side=tk.LEFT, padx=5)
    asis_entry.bind("<Return>", lambda event: registrar_asistencia_por_codigo())
    
    # Crear la tabla para mostrar los datos del JSON
    tree = ttk.Treeview(main_frame, columns=("Codigo", "Nombre"), show="headings")
    tree.heading("Codigo", text="Código")
    tree.heading("Nombre", text="Nombre")

    # Aplicar los estilos a las filas
    tree.tag_configure("asistido", background="#7FFFD4", foreground="black")
    tree.tag_configure("noasistido", background="#A9A9A9", foreground="black")

    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Cargar y mostrar los datos del JSON
    cargar_datos_json()

    root.mainloop()

def eliminar_invitado():
    """Elimina el usuario seleccionado del archivo JSON y actualiza la tabla."""
    selected_item = tree.selection()
    if not selected_item:
        return  # Si no hay un item seleccionado, no hacer nada

    # Obtener el código del usuario seleccionado
    item_id = selected_item[0]  # Obtener el primer item seleccionado
    item_values = tree.item(item_id, "values")
    codigo = item_values[0]

    # Leer el archivo JSON
    json_file = "data/registros.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            registros = json.load(f)

        # Eliminar el usuario de la lista de registros
        registros = [registro for registro in registros if registro["Codigo"] != codigo]

        # Guardar los cambios en el archivo JSON
        with open(json_file, "w") as f:
            json.dump(registros, f, indent=4)

    # Actualizar la tabla
    cargar_datos_json()

def cargar_datos_json(filter_text=None):
    """Carga datos del archivo JSON y los muestra en la tabla."""
    json_file = "data/registros.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            registros = json.load(f)
        # Limpiar la tabla antes de cargar nuevos datos
        for item in tree.get_children():
            tree.delete(item)

        # Filtrar registros si se proporciona un texto de búsqueda
        if filter_text:
            registros = [
                registro for registro in registros
                if filter_text.lower() in registro["Codigo"].lower() or filter_text.lower() in registro["Nombre"].lower()
            ]

        # Filtrar registros según la selección de asistencia
        asistencia_filter = asistencia_filter_var.get()
        if asistencia_filter == 1:  # Mostrar solo asistidos
            registros = [registro for registro in registros if registro["Asistencia"]]
        elif asistencia_filter == 2:  # Mostrar solo no asistidos
            registros = [registro for registro in registros if not registro["Asistencia"]]

        # Insertar cada registro en la tabla con estilo basado en la asistencia
        for registro in registros:
            estilo = "asistido" if registro["Asistencia"] else "noasistido"
            tree.insert("", "end", values=(registro["Codigo"], registro["Nombre"]), tags=(estilo,))

def nuevo_usuario():
    global new_guest_window, codigo_entry, nombre_entry, asistencia_var

    if 'new_guest_window' in globals() and new_guest_window.winfo_exists():
        new_guest_window.lift()  # Llevar la ventana al frente si ya existe
        return

    new_guest_window = tk.Toplevel(root)
    new_guest_window.title("Nuevo Invitado")
    new_guest_window.geometry("600x400")

    label = ttk.Label(new_guest_window, text="Agrega un nuevo invitado:")
    label.pack(pady=20)

    codigo_label = ttk.Label(new_guest_window, text="Ingresa el código:")
    codigo_label.pack(pady=5)
    codigo_entry = ttk.Entry(new_guest_window)
    codigo_entry.pack(pady=5)
    codigo_entry.bind("<Return>", lambda event: guardar_json())  # Asociar Enter con guardar_json

    nombre_label = ttk.Label(new_guest_window, text="Ingresa el nombre:")
    nombre_label.pack(pady=5)
    nombre_entry = ttk.Entry(new_guest_window)
    nombre_entry.pack(pady=5)
    nombre_entry.bind("<Return>", lambda event: guardar_json())  # Asociar Enter con guardar_json

    accept_button = ttk.Button(new_guest_window, text="Aceptar", command=guardar_json)
    accept_button.pack(pady=10)
    close_button = ttk.Button(new_guest_window, text="Cerrar", command=new_guest_window.destroy)
    close_button.pack(pady=5)
    clean_button = ttk.Button(new_guest_window, text="Limpiar", command=clear_text)
    clean_button.pack(pady=10)

def registrar_asistencia_por_codigo():
    codigo = asis_entry.get()
    flag = False
    json_file = "data/registros.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            registros = json.load(f)

        for registro in registros:
            if registro["Codigo"] == codigo:
                registro["Asistencia"] = True  # Cambiar el estado de asistencia
                flag = True

        if flag:
            # Guardar los cambios de nuevo en el archivo JSON
            with open(json_file, "w") as f:
                json.dump(registros, f, indent=4)
            mostrar_mensaje_exito("Se guardó su asistencia correctamente", root)
        else:
            messagebox.showerror("Error", "El código no existe")
        
    asis_entry.delete(0, tk.END)
    # Actualizar la tabla
    cargar_datos_json()

def registrar_asistencia(valor):
    """Registra o actualiza la asistencia del usuario seleccionado."""
    selected_item = tree.selection()
    if not selected_item:
        return  # Si no hay un item seleccionado, no hacer nada

    item_id = selected_item[0]  # Obtener el primer item seleccionado
    item_values = tree.item(item_id, "values")
    codigo = item_values[0]

    # Leer el archivo JSON y buscar el registro correspondiente
    json_file = "data/registros.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            registros = json.load(f)

        for registro in registros:
            if registro["Codigo"] == codigo:
                registro["Asistencia"] = valor  # Cambiar el estado de asistencia

        # Guardar los cambios de nuevo en el archivo JSON
        with open(json_file, "w") as f:
            json.dump(registros, f, indent=4)

    # Actualizar la tabla
    cargar_datos_json()

def clear_text():
    """Limpia las entradas de texto."""
    codigo_entry.delete(0, 'end')
    nombre_entry.delete(0, 'end')

def guardar_json():
    """Guarda los datos ingresados en el archivo JSON."""
    codigo = codigo_entry.get()
    nombre = nombre_entry.get()

    if not codigo or not nombre:
        messagebox.showerror("Error", "Por favor, complete todos los campos antes de guardar.")
        new_guest_window.lift()
        return
    
    datos = {
        "Codigo": codigo,
        "Nombre": nombre,
        "Asistencia": False
    }
    json_file = "data/registros.json"
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            registros = json.load(f)
    else:
        registros = []
    registros.append(datos)
    with open(json_file, "w") as f:
        json.dump(registros, f, indent=4)
    
    # Limpiar entradas después de guardar
    codigo_entry.delete(0, tk.END)
    nombre_entry.delete(0, tk.END)

    # Actualizar la tabla con el nuevo registro
    cargar_datos_json()
    
    mostrar_mensaje_exito("El invitado ha sido agregado exitosamente.", new_guest_window)

def mostrar_mensaje_exito(mensaje, window):
    # Crear un Label para mostrar el mensaje
    label_mensaje = tk.Label(window, text=mensaje, bg='lightgreen', fg='black', font=("Arial", 12))
    label_mensaje.pack(pady=10)

    # Hacer que el mensaje desaparezca después de 3 segundos
    new_guest_window.after(3000, label_mensaje.destroy)

def buscar_codigo_o_nombre():
    """Busca un registro por código o nombre y actualiza la tabla."""
    filter_text = search_entry.get()
    cargar_datos_json(filter_text=filter_text)

def actualizar_filtro_asistencia():
    """Actualiza la tabla en función del filtro de asistencia seleccionado."""
    cargar_datos_json()

main()
