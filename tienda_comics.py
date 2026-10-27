# -*- coding: utf-8 -*-
"""
Usuarios de prueba:
    admin     / admin123   (Administrador)
    vendedor  / venta123   (Vendedor)
ARC 301
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass, field
from datetime import datetime

IVA = 0.16
NOMBRE_TIENDA = "VIÑETA & TINTA"
FORMATOS = ("Tapa blanda", "Pasta dura")
GENEROS = ("Superhéroes", "Manga", "Ciencia ficción", "Fantasía", "Terror",
           "Autobiográfico", "Aventura", "Novela gráfica", "Policiaco")

# Paleta
C_AMARILLO = "#ffd23f"
C_ROJO = "#e63946"
C_AZUL = "#1d3557"
C_FONDO = "#f7f3e8"


def money(valor):
    return f"${valor:,.2f}"


# ======================================================================
#  MODELOS (programación orientada a objetos)
# ======================================================================
@dataclass
class Producto:
    id: int
    titulo: str
    autor: str
    genero: str
    editorial: str
    formato: str
    stock: int
    precio: float


@dataclass
class Cliente:
    id: int
    nombre: str
    telefono: str = ""
    correo: str = ""


@dataclass
class Usuario:
    usuario: str
    clave: str
    nombre: str
    rol: str  # "Administrador" o "Vendedor"


@dataclass
class LineaVenta:
    producto_id: int
    titulo: str
    cantidad: int
    precio_unitario: float

    @property
    def importe(self):
        return self.cantidad * self.precio_unitario


@dataclass
class Venta:
    folio: int
    fecha: datetime
    cliente: Cliente
    vendedor: Usuario
    lineas: list = field(default_factory=list)

    # Los precios de los artículos YA incluyen IVA: el total es la suma de
    # los importes y el subtotal/IVA se desglosan a partir de él.
    @property
    def total(self):
        return sum(l.importe for l in self.lineas)

    @property
    def subtotal(self):
        return self.total / (1 + IVA)

    @property
    def iva(self):
        return self.subtotal * IVA

    def ticket_texto(self):
        w = 46
        linea = "=" * w
        guion = "-" * w
        out = [linea,
               NOMBRE_TIENDA.center(w),
               "Librería y Tienda de Cómics".center(w),
               linea,
               f"Folio:    {self.folio:05d}",
               f"Fecha:    {self.fecha:%d/%m/%Y %H:%M}",
               f"Cliente:  {self.cliente.nombre}",
               f"Atendió:  {self.vendedor.nombre}",
               guion,
               "Producto".ljust(w),
               f"{'Cant':<6}{'P. Unit. c/IVA':>14}{'Importe':>26}"[:w],
               guion]
        for l in self.lineas:
            out.append(l.titulo[:w])
            detalle = f"{l.cantidad:<6}{money(l.precio_unitario):>14}"
            out.append(detalle + money(l.importe).rjust(w - len(detalle)))
        out += [guion,
                f"{'Subtotal:':<30}{money(self.subtotal):>16}",
                f"{'IVA (16%, incluido):':<30}{money(self.iva):>16}",
                f"{'TOTAL:':<30}{money(self.total):>16}",
                linea,
                "¡Gracias por tu compra!".center(w),
                "Este ticket es un comprobante digital".center(w),
                linea]
        return "\n".join(out)


# ======================================================================
#  "BASE DE DATOS" EN MEMORIA
# ======================================================================
class Tienda:
    def __init__(self):
        self.usuarios = {
            "admin": Usuario("admin", "admin123", "Administrador General", "Administrador"),
            "vendedor": Usuario("vendedor", "venta123", "Vendedor de Mostrador", "Vendedor"),
        }
        self.productos = {}
        self.clientes = {}
        self.ventas = []
        self._sig_producto = 1
        self._sig_cliente = 1
        self._sig_folio = 1
        self._cargar_datos_iniciales()

    # ---- autenticación
    def autenticar(self, usuario, clave):
        u = self.usuarios.get(usuario.strip().lower())
        return u if u and u.clave == clave else None

    # ---- productos
    def agregar_producto(self, titulo, autor, genero, editorial, formato, stock, precio):
        p = Producto(self._sig_producto, titulo, autor, genero, editorial, formato, stock, precio)
        self.productos[p.id] = p
        self._sig_producto += 1
        return p

    # ---- clientes
    def agregar_cliente(self, nombre, telefono="", correo=""):
        c = Cliente(self._sig_cliente, nombre, telefono, correo)
        self.clientes[c.id] = c
        self._sig_cliente += 1
        return c

    # ---- ventas
    def registrar_venta(self, cliente, vendedor, carrito):
        """carrito: {id_producto: cantidad}. Descuenta inventario y crea la venta."""
        lineas = []
        for pid, cant in carrito.items():
            p = self.productos[pid]
            if cant > p.stock:
                raise ValueError(f"Stock insuficiente de «{p.titulo}» (quedan {p.stock}).")
            lineas.append(LineaVenta(pid, p.titulo, cant, p.precio))
        for l in lineas:
            self.productos[l.producto_id].stock -= l.cantidad
        venta = Venta(self._sig_folio, datetime.now(), cliente, vendedor, lineas)
        self._sig_folio += 1
        self.ventas.append(venta)
        return venta

    def _cargar_datos_iniciales(self):
        self.agregar_cliente("Público general")
        self.agregar_cliente("Ana Torres", "771 123 4567", "ana.torres@correo.com")
        self.agregar_cliente("Luis Hernández", "771 234 5678", "luis.hdz@correo.com")
        self.agregar_cliente("Mariana Cruz", "771 345 6789", "mariana.cruz@correo.com")
        datos = [
            ("Watchmen", "Alan Moore / Dave Gibbons", "Superhéroes", "DC Comics", "Pasta dura", 8, 650),
            ("Maus", "Art Spiegelman", "Autobiográfico", "Pantheon Books", "Tapa blanda", 10, 420),
            ("The Sandman: Preludios", "Neil Gaiman", "Fantasía", "Vertigo", "Tapa blanda", 12, 390),
            ("Akira Vol. 1", "Katsuhiro Otomo", "Manga", "Kodansha", "Tapa blanda", 9, 340),
            ("Batman: El regreso del Caballero Oscuro", "Frank Miller", "Superhéroes", "DC Comics", "Pasta dura", 6, 580),
            ("Persépolis", "Marjane Satrapi", "Autobiográfico", "L'Association", "Tapa blanda", 7, 360),
            ("V de Vendetta", "Alan Moore / David Lloyd", "Ciencia ficción", "DC Comics", "Tapa blanda", 8, 410),
            ("Berserk Vol. 1", "Kentaro Miura", "Manga", "Dark Horse", "Tapa blanda", 11, 320),
            ("Saga Vol. 1", "Brian K. Vaughan / Fiona Staples", "Ciencia ficción", "Image Comics", "Tapa blanda", 10, 370),
            ("One Piece Vol. 1", "Eiichiro Oda", "Aventura", "Shueisha", "Tapa blanda", 15, 180),
            ("Hellboy: Semilla de destrucción", "Mike Mignola", "Terror", "Dark Horse", "Pasta dura", 5, 520),
            ("Spider-Man: Azul", "Jeph Loeb / Tim Sale", "Superhéroes", "Marvel", "Pasta dura", 4, 480),
        ]
        for d in datos:
            self.agregar_producto(*d)


# ======================================================================
#  UTILIDADES DE INTERFAZ
# ======================================================================
def crear_tabla(parent, columnas, alto=12):
    """columnas: lista de (nombre, ancho, anchor). Devuelve (frame, tree)."""
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=[c[0] for c in columnas], show="headings",
                        height=alto, selectmode="browse")
    for nombre, ancho, anchor in columnas:
        tree.heading(nombre, text=nombre)
        tree.column(nombre, width=ancho, anchor=anchor)
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    tree.tag_configure("par", background="#fffaf0")
    tree.tag_configure("impar", background="#fdeec7")
    tree.tag_configure("bajo", foreground=C_ROJO)
    return frame, tree


def llenar(tree, filas):
    """filas: lista de (iid, valores, tags_extra)."""
    tree.delete(*tree.get_children())
    for i, (iid, valores, extra) in enumerate(filas):
        tags = ("par" if i % 2 == 0 else "impar",) + tuple(extra)
        tree.insert("", "end", iid=str(iid), values=valores, tags=tags)


def mostrar_ticket(master, venta):
    win = tk.Toplevel(master)
    win.title(f"Ticket #{venta.folio:05d}")
    win.configure(bg=C_FONDO)
    win.resizable(False, False)
    txt = tk.Text(win, width=48, height=min(40, 20 + len(venta.lineas) * 2),
                  font=("Courier New", 10), bg="white", relief="flat", padx=8, pady=8)
    txt.insert("1.0", venta.ticket_texto())
    txt.configure(state="disabled")
    txt.pack(padx=12, pady=(12, 6))

    def guardar():
        ruta = filedialog.asksaveasfilename(
            parent=win, defaultextension=".txt", initialfile=f"ticket_{venta.folio:05d}.txt",
            filetypes=[("Texto", "*.txt")])
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(venta.ticket_texto())
            messagebox.showinfo("Ticket", "Ticket guardado.", parent=win)

    barra = ttk.Frame(win)
    barra.pack(pady=(0, 12))
    ttk.Button(barra, text="Guardar .txt", command=guardar).pack(side="left", padx=4)
    ttk.Button(barra, text="Cerrar", command=win.destroy).pack(side="left", padx=4)
    win.transient(master)
    win.grab_set()


# ======================================================================
#  PESTAÑA: PUNTO DE VENTA
# ======================================================================
class TabVenta(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app
        self.carrito = {}  # id_producto -> cantidad

        izq = ttk.LabelFrame(self, text=" Catálogo ", padding=8)
        der = ttk.LabelFrame(self, text=" Venta actual ", padding=8)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 6))
        der.pack(side="left", fill="both", expand=True)

        # --- catálogo
        fb = ttk.Frame(izq)
        fb.pack(fill="x", pady=(0, 6))
        ttk.Label(fb, text="Buscar:").pack(side="left")
        self.busq = tk.StringVar()
        self.busq.trace_add("write", lambda *a: self.cargar_catalogo())
        ttk.Entry(fb, textvariable=self.busq).pack(side="left", fill="x", expand=True, padx=6)

        cols = [("ID", 40, "center"), ("Título", 200, "w"), ("Autor", 140, "w"),
                ("Formato", 85, "center"), ("Stock", 50, "center"), ("Precio c/IVA", 90, "e")]
        f, self.tv_cat = crear_tabla(izq, cols, 14)
        f.pack(fill="both", expand=True)
        self.tv_cat.bind("<Double-1>", lambda e: self.agregar())

        fa = ttk.Frame(izq)
        fa.pack(fill="x", pady=(8, 0))
        ttk.Label(fa, text="Cantidad:").pack(side="left")
        self.cant = tk.IntVar(value=1)
        ttk.Spinbox(fa, from_=1, to=99, width=5, textvariable=self.cant).pack(side="left", padx=6)
        ttk.Button(fa, text="Agregar al carrito  ➜", style="Accion.TButton",
                   command=self.agregar).pack(side="left", padx=6)

        # --- carrito
        fc = ttk.Frame(der)
        fc.pack(fill="x", pady=(0, 6))
        ttk.Label(fc, text="Cliente:").pack(side="left")
        self.cb_cliente = ttk.Combobox(fc, state="readonly", width=30)
        self.cb_cliente.pack(side="left", padx=6)

        cols2 = [("Título", 190, "w"), ("Cant", 45, "center"),
                 ("P. Unit. c/IVA", 100, "e"), ("Importe", 85, "e")]
        f2, self.tv_car = crear_tabla(der, cols2, 10)
        f2.pack(fill="both", expand=True)

        fb2 = ttk.Frame(der)
        fb2.pack(fill="x", pady=6)
        ttk.Button(fb2, text="Quitar seleccionado", command=self.quitar).pack(side="left")
        ttk.Button(fb2, text="Vaciar", command=self.vaciar).pack(side="left", padx=6)

        tot = ttk.Frame(der)
        tot.pack(fill="x", pady=(4, 0))
        self.lbl_sub = self._fila_total(tot, "Subtotal:", 0)
        self.lbl_iva = self._fila_total(tot, "IVA incluido (16%):", 1)
        self.lbl_tot = self._fila_total(tot, "TOTAL:", 2, grande=True)
        ttk.Button(der, text="COBRAR Y GENERAR TICKET", style="Cobrar.TButton",
                   command=self.cobrar).pack(fill="x", pady=(10, 0), ipady=6)

        self.refrescar()

    def _fila_total(self, parent, texto, fila, grande=False):
        fuente = ("Segoe UI", 14, "bold") if grande else ("Segoe UI", 10)
        ttk.Label(parent, text=texto, font=fuente).grid(row=fila, column=0, sticky="w")
        lbl = ttk.Label(parent, text=money(0), font=fuente)
        lbl.grid(row=fila, column=1, sticky="e")
        parent.columnconfigure(1, weight=1)
        return lbl

    # --- lógica
    def refrescar(self):
        self.cargar_catalogo()
        clientes = [f"{c.id} - {c.nombre}" for c in self.app.tienda.clientes.values()]
        actual = self.cb_cliente.get()
        self.cb_cliente["values"] = clientes
        self.cb_cliente.set(actual if actual in clientes else (clientes[0] if clientes else ""))
        # limpiar del carrito productos que ya no existan
        for pid in list(self.carrito):
            if pid not in self.app.tienda.productos:
                del self.carrito[pid]
        self.actualizar_carrito()

    def cargar_catalogo(self):
        q = self.busq.get().strip().lower()
        filas = []
        for p in self.app.tienda.productos.values():
            if q and q not in f"{p.titulo} {p.autor} {p.genero} {p.editorial}".lower():
                continue
            filas.append((p.id, (p.id, p.titulo, p.autor, p.formato, p.stock, money(p.precio)),
                          ["bajo"] if p.stock <= 3 else []))
        llenar(self.tv_cat, filas)

    def agregar(self):
        sel = self.tv_cat.selection()
        if not sel:
            messagebox.showwarning("Venta", "Selecciona un producto del catálogo.")
            return
        try:
            n = int(self.cant.get())
            if n < 1:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showwarning("Venta", "La cantidad debe ser un entero mayor a 0.")
            return
        p = self.app.tienda.productos[int(sel[0])]
        if self.carrito.get(p.id, 0) + n > p.stock:
            messagebox.showwarning("Venta", f"Stock insuficiente: solo hay {p.stock} de «{p.titulo}».")
            return
        self.carrito[p.id] = self.carrito.get(p.id, 0) + n
        self.actualizar_carrito()

    def quitar(self):
        sel = self.tv_car.selection()
        if sel:
            self.carrito.pop(int(sel[0]), None)
            self.actualizar_carrito()

    def vaciar(self):
        self.carrito.clear()
        self.actualizar_carrito()

    def actualizar_carrito(self):
        filas, subtotal = [], 0.0
        for pid, cant in self.carrito.items():
            p = self.app.tienda.productos[pid]
            imp = cant * p.precio
            subtotal += imp
            filas.append((pid, (p.titulo, cant, money(p.precio), money(imp)), []))
        llenar(self.tv_car, filas)
        total = subtotal  # suma de importes (precios ya con IVA)
        base = total / (1 + IVA)
        self.lbl_sub.config(text=money(base))
        self.lbl_iva.config(text=money(base * IVA))
        self.lbl_tot.config(text=money(total))

    def cobrar(self):
        if not self.carrito:
            messagebox.showwarning("Venta", "El carrito está vacío.")
            return
        if not self.cb_cliente.get():
            messagebox.showwarning("Venta", "Selecciona un cliente.")
            return
        cliente = self.app.tienda.clientes[int(self.cb_cliente.get().split(" - ")[0])]
        if not messagebox.askyesno("Confirmar", f"¿Cobrar la venta a {cliente.nombre}?"):
            return
        try:
            venta = self.app.tienda.registrar_venta(cliente, self.app.usuario, dict(self.carrito))
        except ValueError as err:
            messagebox.showerror("Venta", str(err))
            return
        self.carrito.clear()
        self.app.refrescar_todo()
        mostrar_ticket(self.app, venta)


# ======================================================================
#  PESTAÑA: INVENTARIO
# ======================================================================
class TabInventario(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app
        self.editable = app.usuario.rol == "Administrador"
        self.id_sel = None

        fb = ttk.Frame(self)
        fb.pack(fill="x", pady=(0, 6))
        ttk.Label(fb, text="Buscar (ID, título, autor, género, editorial):").pack(side="left")
        self.busq = tk.StringVar()
        self.busq.trace_add("write", lambda *a: self.refrescar())
        ttk.Entry(fb, textvariable=self.busq).pack(side="left", fill="x", expand=True, padx=6)

        cols = [("ID", 40, "center"), ("Título", 230, "w"), ("Autor", 170, "w"),
                ("Género", 100, "w"), ("Editorial", 110, "w"), ("Formato", 85, "center"),
                ("Stock", 50, "center"), ("Precio c/IVA", 90, "e")]
        f, self.tv = crear_tabla(self, cols, 12)
        f.pack(fill="both", expand=True)
        self.tv.bind("<<TreeviewSelect>>", self.al_seleccionar)

        if not self.editable:
            ttk.Label(self, text="Solo el Administrador puede modificar el inventario.",
                      foreground=C_ROJO).pack(pady=6)
            return

        form = ttk.LabelFrame(self, text=" Datos del producto ", padding=8)
        form.pack(fill="x", pady=(8, 0))
        self.v = {k: tk.StringVar() for k in
                  ("titulo", "autor", "genero", "editorial", "formato", "stock", "precio")}
        campos = [("Título", "titulo", None), ("Autor", "autor", None),
                  ("Género", "genero", GENEROS), ("Editorial", "editorial", None),
                  ("Formato", "formato", FORMATOS), ("Stock", "stock", None),
                  ("Precio c/IVA ($)", "precio", None)]
        for i, (txt, key, vals) in enumerate(campos):
            r, c = divmod(i, 4)
            ttk.Label(form, text=txt).grid(row=r * 2, column=c, sticky="w", padx=4)
            if vals:
                w = ttk.Combobox(form, textvariable=self.v[key], values=vals,
                                 state="readonly" if key == "formato" else "normal", width=22)
            else:
                w = ttk.Entry(form, textvariable=self.v[key], width=24)
            w.grid(row=r * 2 + 1, column=c, padx=4, pady=(0, 6), sticky="we")

        bar = ttk.Frame(form)
        bar.grid(row=4, column=0, columnspan=4, pady=(4, 0), sticky="w")
        ttk.Button(bar, text="Agregar", style="Accion.TButton", command=self.agregar).pack(side="left", padx=4)
        ttk.Button(bar, text="Guardar cambios", command=self.editar).pack(side="left", padx=4)
        ttk.Button(bar, text="Eliminar", command=self.eliminar).pack(side="left", padx=4)
        ttk.Button(bar, text="Limpiar", command=self.limpiar).pack(side="left", padx=4)
        self.refrescar()

    def refrescar(self):
        q = self.busq.get().strip().lower()
        filas = []
        for p in self.app.tienda.productos.values():
            if q and q not in f"{p.id} {p.titulo} {p.autor} {p.genero} {p.editorial}".lower():
                continue
            filas.append((p.id, (p.id, p.titulo, p.autor, p.genero, p.editorial,
                                 p.formato, p.stock, money(p.precio)),
                          ["bajo"] if p.stock <= 3 else []))
        llenar(self.tv, filas)

    def al_seleccionar(self, _):
        sel = self.tv.selection()
        if not sel or not self.editable:
            return
        p = self.app.tienda.productos[int(sel[0])]
        self.id_sel = p.id
        for k in self.v:
            self.v[k].set(getattr(p, k))

    def limpiar(self):
        self.id_sel = None
        for var in self.v.values():
            var.set("")
        self.tv.selection_remove(self.tv.selection())

    def _leer_form(self):
        d = {k: v.get().strip() for k, v in self.v.items()}
        for k in ("titulo", "autor", "genero", "editorial", "formato"):
            if not d[k]:
                messagebox.showwarning("Inventario", f"El campo «{k}» es obligatorio.")
                return None
        if d["formato"] not in FORMATOS:
            messagebox.showwarning("Inventario", "Elige un formato válido.")
            return None
        try:
            d["stock"] = int(d["stock"])
            d["precio"] = float(d["precio"])
            if d["stock"] < 0 or d["precio"] <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Inventario", "Stock debe ser entero ≥ 0 y precio un número > 0.")
            return None
        return d

    def agregar(self):
        d = self._leer_form()
        if d:
            self.app.tienda.agregar_producto(d["titulo"], d["autor"], d["genero"], d["editorial"],
                                             d["formato"], d["stock"], d["precio"])
            self.limpiar()
            self.app.refrescar_todo()

    def editar(self):
        if self.id_sel is None:
            messagebox.showwarning("Inventario", "Selecciona un producto de la tabla para editarlo.")
            return
        d = self._leer_form()
        if d:
            p = self.app.tienda.productos[self.id_sel]
            for k, val in d.items():
                setattr(p, k, val)
            self.limpiar()
            self.app.refrescar_todo()

    def eliminar(self):
        if self.id_sel is None:
            messagebox.showwarning("Inventario", "Selecciona un producto para eliminarlo.")
            return
        p = self.app.tienda.productos[self.id_sel]
        if messagebox.askyesno("Eliminar", f"¿Eliminar «{p.titulo}» del inventario?"):
            del self.app.tienda.productos[self.id_sel]
            self.limpiar()
            self.app.refrescar_todo()


# ======================================================================
#  PESTAÑA: CLIENTES
# ======================================================================
class TabClientes(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app
        self.id_sel = None

        cols = [("ID", 40, "center"), ("Nombre", 250, "w"),
                ("Teléfono", 130, "w"), ("Correo", 230, "w")]
        f, self.tv = crear_tabla(self, cols, 12)
        f.pack(fill="both", expand=True)
        self.tv.bind("<<TreeviewSelect>>", self.al_seleccionar)

        form = ttk.LabelFrame(self, text=" Datos del cliente ", padding=8)
        form.pack(fill="x", pady=(8, 0))
        self.v = {k: tk.StringVar() for k in ("nombre", "telefono", "correo")}
        for i, (txt, key) in enumerate([("Nombre", "nombre"), ("Teléfono", "telefono"), ("Correo", "correo")]):
            ttk.Label(form, text=txt).grid(row=0, column=i, sticky="w", padx=4)
            ttk.Entry(form, textvariable=self.v[key], width=30).grid(row=1, column=i, padx=4, pady=(0, 6))
        bar = ttk.Frame(form)
        bar.grid(row=2, column=0, columnspan=3, sticky="w")
        ttk.Button(bar, text="Agregar", style="Accion.TButton", command=self.agregar).pack(side="left", padx=4)
        ttk.Button(bar, text="Guardar cambios", command=self.editar).pack(side="left", padx=4)
        if app.usuario.rol == "Administrador":
            ttk.Button(bar, text="Eliminar", command=self.eliminar).pack(side="left", padx=4)
        ttk.Button(bar, text="Limpiar", command=self.limpiar).pack(side="left", padx=4)
        self.refrescar()

    def refrescar(self):
        llenar(self.tv, [(c.id, (c.id, c.nombre, c.telefono, c.correo), [])
                         for c in self.app.tienda.clientes.values()])

    def al_seleccionar(self, _):
        sel = self.tv.selection()
        if sel:
            c = self.app.tienda.clientes[int(sel[0])]
            self.id_sel = c.id
            for k in self.v:
                self.v[k].set(getattr(c, k))

    def limpiar(self):
        self.id_sel = None
        for var in self.v.values():
            var.set("")
        self.tv.selection_remove(self.tv.selection())

    def _leer(self):
        d = {k: v.get().strip() for k, v in self.v.items()}
        if not d["nombre"]:
            messagebox.showwarning("Clientes", "El nombre es obligatorio.")
            return None
        if d["correo"] and ("@" not in d["correo"] or "." not in d["correo"]):
            messagebox.showwarning("Clientes", "El correo no parece válido.")
            return None
        return d

    def agregar(self):
        d = self._leer()
        if d:
            self.app.tienda.agregar_cliente(d["nombre"], d["telefono"], d["correo"])
            self.limpiar()
            self.app.refrescar_todo()

    def editar(self):
        if self.id_sel is None:
            messagebox.showwarning("Clientes", "Selecciona un cliente de la tabla.")
            return
        if self.id_sel == 1:
            messagebox.showinfo("Clientes", "«Público general» no se puede modificar.")
            return
        d = self._leer()
        if d:
            c = self.app.tienda.clientes[self.id_sel]
            c.nombre, c.telefono, c.correo = d["nombre"], d["telefono"], d["correo"]
            self.limpiar()
            self.app.refrescar_todo()

    def eliminar(self):
        if self.id_sel is None:
            messagebox.showwarning("Clientes", "Selecciona un cliente.")
            return
        if self.id_sel == 1:
            messagebox.showinfo("Clientes", "«Público general» no se puede eliminar.")
            return
        c = self.app.tienda.clientes[self.id_sel]
        if messagebox.askyesno("Eliminar", f"¿Eliminar al cliente «{c.nombre}»?"):
            del self.app.tienda.clientes[self.id_sel]
            self.limpiar()
            self.app.refrescar_todo()


# ======================================================================
#  PESTAÑA: HISTORIAL DE VENTAS
# ======================================================================
class TabVentas(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app
        cols = [("Folio", 70, "center"), ("Fecha", 130, "center"), ("Cliente", 200, "w"),
                ("Atendió", 170, "w"), ("Artículos", 70, "center"), ("Total", 100, "e")]
        f, self.tv = crear_tabla(self, cols, 14)
        f.pack(fill="both", expand=True)
        self.tv.bind("<Double-1>", lambda e: self.ver())

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=8)
        ttk.Button(bar, text="Ver ticket", style="Accion.TButton", command=self.ver).pack(side="left")
        self.lbl = ttk.Label(bar, font=("Segoe UI", 11, "bold"))
        self.lbl.pack(side="right")
        self.refrescar()

    def _ventas_visibles(self):
        v = self.app.tienda.ventas
        if self.app.usuario.rol != "Administrador":
            v = [x for x in v if x.vendedor.usuario == self.app.usuario.usuario]
        return sorted(v, key=lambda x: x.folio, reverse=True)

    def refrescar(self):
        ventas = self._ventas_visibles()
        llenar(self.tv, [(v.folio, (f"{v.folio:05d}", f"{v.fecha:%d/%m/%Y %H:%M}", v.cliente.nombre,
                                    v.vendedor.nombre, sum(l.cantidad for l in v.lineas), money(v.total)), [])
                         for v in ventas])
        self.lbl.config(text=f"Ventas: {len(ventas)}   |   Total vendido: {money(sum(v.total for v in ventas))}")

    def ver(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Ventas", "Selecciona una venta.")
            return
        venta = next(v for v in self.app.tienda.ventas if v.folio == int(sel[0]))
        mostrar_ticket(self.app, venta)


# ======================================================================
#  APLICACIÓN PRINCIPAL
# ======================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{NOMBRE_TIENDA} · Punto de venta")
        self.geometry("1100x640")
        self.minsize(980, 600)
        self.configure(bg=C_FONDO)
        self.tienda = Tienda()
        self.usuario = None
        self.tabs = []
        self._estilos()
        self.mostrar_login()

    def _estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=C_FONDO, font=("Segoe UI", 10))
        s.configure("TFrame", background=C_FONDO)
        s.configure("TLabel", background=C_FONDO)
        s.configure("TLabelframe", background=C_FONDO)
        s.configure("TLabelframe.Label", background=C_FONDO, foreground=C_AZUL, font=("Segoe UI", 10, "bold"))
        s.configure("TButton", padding=6)
        s.configure("Accion.TButton", background=C_AZUL, foreground="white", font=("Segoe UI", 10, "bold"))
        s.map("Accion.TButton", background=[("active", "#27497c")])
        s.configure("Cobrar.TButton", background=C_ROJO, foreground="white", font=("Segoe UI", 11, "bold"))
        s.map("Cobrar.TButton", background=[("active", "#c1121f")])
        s.configure("Treeview", rowheight=24, fieldbackground="white")
        s.configure("Treeview.Heading", background=C_AZUL, foreground="white", font=("Segoe UI", 10, "bold"))
        s.map("Treeview", background=[("selected", C_AMARILLO)], foreground=[("selected", "black")])
        s.configure("TNotebook", background=C_FONDO)
        s.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10, "bold"))
        s.map("TNotebook.Tab", background=[("selected", C_AMARILLO)])

    def _limpiar(self):
        for w in self.winfo_children():
            w.destroy()

    # ---- login
    def mostrar_login(self):
        self._limpiar()
        self.usuario = None
        fondo = tk.Frame(self, bg=C_AZUL)
        fondo.pack(fill="both", expand=True)
        tarjeta = tk.Frame(fondo, bg=C_FONDO, padx=40, pady=30,
                           highlightbackground=C_AMARILLO, highlightthickness=4)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(tarjeta, text="POW!", bg=C_FONDO, fg=C_ROJO,
                 font=("Impact", 36)).pack()
        tk.Label(tarjeta, text=NOMBRE_TIENDA, bg=C_FONDO, fg=C_AZUL,
                 font=("Segoe UI", 20, "bold")).pack()
        tk.Label(tarjeta, text="Librería y Tienda de Cómics", bg=C_FONDO,
                 fg="#555").pack(pady=(0, 16))

        tk.Label(tarjeta, text="Usuario", bg=C_FONDO, anchor="w").pack(fill="x")
        self.e_user = ttk.Entry(tarjeta, width=30)
        self.e_user.pack(pady=(0, 8))
        tk.Label(tarjeta, text="Contraseña", bg=C_FONDO, anchor="w").pack(fill="x")
        self.e_pass = ttk.Entry(tarjeta, width=30, show="•")
        self.e_pass.pack(pady=(0, 12))
        ttk.Button(tarjeta, text="Iniciar sesión", style="Accion.TButton",
                   command=self.iniciar_sesion).pack(fill="x", ipady=4)
        tk.Label(tarjeta, text="Prueba: admin / admin123  ·  vendedor / venta123",
                 bg=C_FONDO, fg="#777", font=("Segoe UI", 8)).pack(pady=(12, 0))
        self.e_user.focus()
        self.bind("<Return>", lambda e: self.iniciar_sesion())

    def iniciar_sesion(self):
        if self.usuario is not None:
            return
        u = self.tienda.autenticar(self.e_user.get(), self.e_pass.get())
        if not u:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            self.e_pass.delete(0, "end")
            return
        self.usuario = u
        self.unbind("<Return>")
        self.mostrar_principal()

    # ---- ventana principal
    def mostrar_principal(self):
        self._limpiar()
        barra = tk.Frame(self, bg=C_AMARILLO)
        barra.pack(fill="x")
        tk.Label(barra, text=f"  {NOMBRE_TIENDA}", bg=C_AMARILLO, fg=C_AZUL,
                 font=("Impact", 18)).pack(side="left", pady=6)
        ttk.Button(barra, text="Cerrar sesión", command=self.mostrar_login).pack(side="right", padx=10)
        tk.Label(barra, text=f"{self.usuario.nombre}  ·  {self.usuario.rol}", bg=C_AMARILLO,
                 fg=C_AZUL, font=("Segoe UI", 10, "bold")).pack(side="right", padx=10)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        self.tabs = [
            ("Punto de venta", TabVenta(nb, self)),
            ("Inventario", TabInventario(nb, self)),
            ("Clientes", TabClientes(nb, self)),
            ("Ventas", TabVentas(nb, self)),
        ]
        for nombre, tab in self.tabs:
            nb.add(tab, text=nombre)

    def refrescar_todo(self):
        for _, tab in self.tabs:
            tab.refrescar()


if __name__ == "__main__":
    App().mainloop()