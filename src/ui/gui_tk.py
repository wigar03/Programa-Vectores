"""
Interfaz Gráfica de Escritorio Alternativa (Tkinter / TTK).
UAM - Álgebra Lineal (MTM0120)

Proporciona una interfaz gráfica nativa de escritorio moderna con tema oscuro,
cuadrículas dinámicas para vectores y matrices, y navegación por pestañas.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction
from typing import List

from src.core.arithmetic import format_number, formatear_vector, formatear_matriz
from src.vectores.operaciones import (
    suma_vectores,
    resta_vectores,
    multiplicar_escalar_vector,
    producto_punto,
)
from src.vectores.combinacion_lineal import evaluar_combinacion_lineal
from src.matrices.operaciones import (
    suma_matrices,
    resta_matrices,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
)
from src.ecuaciones.ecuacion_matricial import resolver_ecuacion_matricial
from src.solver.anterior_programa import ejecutar_programa_anterior


class AlgebraLinealTkApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculadora de Álgebra Lineal - Vectores y Matrices (UAM)")
        self.root.geometry("1020x720")
        self.root.minsize(850, 600)

        # Configuración de estilos TTK
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configurar_estilos()

        # Contenedor principal
        self._crear_interfaz()

    def _configurar_estilos(self):
        bg_dark = "#0F172A"
        bg_card = "#1E293B"
        fg_text = "#F8FAFC"
        accent = "#0284C7"

        self.root.configure(bg=bg_dark)
        self.style.configure(".", background=bg_dark, foreground=fg_text, font=("Segoe UI", 10))
        self.style.configure("TNotebook", background=bg_dark, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=bg_card, foreground="#94A3B8", padding=[14, 8], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "#FFFFFF")])
        self.style.configure("Card.TFrame", background=bg_card, relief="flat")
        self.style.configure("TLabel", background=bg_card, foreground=fg_text)
        self.style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), background="#0284C7", foreground="#FFFFFF")

    def _crear_interfaz(self):
        # Header
        header = tk.Frame(self.root, bg="#1E293B", padx=16, pady=12)
        header.pack(fill="x", padx=12, pady=8)

        tk.Label(
            header,
            text="UAM • FIA - Álgebra Lineal (MTM0120)",
            bg="#1E293B",
            fg="#38BDF8",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Calculadora de Vectores en R^n, Combinación Lineal y Matrices",
            bg="#1E293B",
            fg="#F8FAFC",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        btn_prev = tk.Button(
            header,
            text="🚀 Abrir Programa Anterior (Semana #3)",
            bg="#4338CA",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=4,
            command=self._lanzar_programa_anterior,
        )
        btn_prev.pack(side="right", pady=4)

        # Notebook de Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=4)

        # Pestañas
        self.tab_vectores = ttk.Frame(self.notebook)
        self.tab_combinacion = ttk.Frame(self.notebook)
        self.tab_matrices = ttk.Frame(self.notebook)
        self.tab_ecuaciones = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_vectores, text="📐 Vectores en R^n")
        self.notebook.add(self.tab_combinacion, text="🎯 Combinación Lineal")
        self.notebook.add(self.tab_matrices, text="🔢 Matrices Básicas")
        self.notebook.add(self.tab_ecuaciones, text="⚖️ Ax = b")

        self._armar_tab_vectores()
        self._armar_tab_combinacion()
        self._armar_tab_matrices()
        self._armar_tab_ecuaciones()

    def _lanzar_programa_anterior(self):
        exito, msg = ejecutar_programa_anterior()
        if exito:
            messagebox.showinfo("Programa Anterior", msg)
        else:
            messagebox.showwarning("Aviso", msg)

    # 1. Pestaña Vectores
    def _armar_tab_vectores(self):
        f = tk.Frame(self.tab_vectores, bg="#1E293B", padx=16, pady=16)
        f.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(f, text="Ingrese los componentes separados por coma o espacio (soporta fracciones como 1/2):", bg="#1E293B", fg="#94A3B8").pack(anchor="w", pady=4)

        tk.Label(f, text="Vector u:", bg="#1E293B", fg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.ent_u = tk.Entry(f, bg="#0F172A", fg="#38BDF8", insertbackground="white", font=("Consolas", 11), width=45)
        self.ent_u.pack(anchor="w", pady=2)
        self.ent_u.insert(0, "1, 2, -3, 4")

        tk.Label(f, text="Vector v:", bg="#1E293B", fg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.ent_v = tk.Entry(f, bg="#0F172A", fg="#38BDF8", insertbackground="white", font=("Consolas", 11), width=45)
        self.ent_v.pack(anchor="w", pady=2)
        self.ent_v.insert(0, "3, 0, 5, -1")

        tk.Label(f, text="Escalar c:", bg="#1E293B", fg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.ent_c = tk.Entry(f, bg="#0F172A", fg="#38BDF8", insertbackground="white", font=("Consolas", 11), width=15)
        self.ent_c.pack(anchor="w", pady=2)
        self.ent_c.insert(0, "2")

        btns_frame = tk.Frame(f, bg="#1E293B")
        btns_frame.pack(anchor="w", pady=12)

        tk.Button(btns_frame, text="Suma (u + v)", bg="#0284C7", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=lambda: self._calc_vec("suma")).pack(side="left", padx=4)
        tk.Button(btns_frame, text="Resta (u - v)", bg="#0284C7", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=lambda: self._calc_vec("resta")).pack(side="left", padx=4)
        tk.Button(btns_frame, text="Escalar (c · u)", bg="#2563EB", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=lambda: self._calc_vec("escalar")).pack(side="left", padx=4)
        tk.Button(btns_frame, text="Producto Punto (u · v)", bg="#4F46E5", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=lambda: self._calc_vec("punto")).pack(side="left", padx=4)

        self.txt_res_vec = tk.Text(f, bg="#0F172A", fg="#F8FAFC", font=("Consolas", 10), height=10, relief="flat", padx=8, pady=8)
        self.txt_res_vec.pack(fill="both", expand=True, pady=4)

    def _parse_vec(self, text):
        clean = text.replace(",", " ").split()
        return clean

    def _calc_vec(self, op):
        try:
            u = self._parse_vec(self.ent_u.get())
            v = self._parse_vec(self.ent_v.get())
            c = self.ent_c.get().strip()

            self.txt_res_vec.delete("1.0", tk.END)
            if op == "suma":
                r = suma_vectores(u, v)
                self.txt_res_vec.insert(tk.END, f"Suma Vectorial u + v:\nResultado = {formatear_vector(r)}\n\nProcedimiento algebraico: (u + v)_i = u_i + v_i.")
            elif op == "resta":
                r = resta_vectores(u, v)
                self.txt_res_vec.insert(tk.END, f"Resta Vectorial u - v:\nResultado = {formatear_vector(r)}\n\nProcedimiento algebraico: (u - v)_i = u_i - v_i.")
            elif op == "escalar":
                r = multiplicar_escalar_vector(c, u)
                self.txt_res_vec.insert(tk.END, f"Producto por Escalar ({c}) · u:\nResultado = {formatear_vector(r)}\n\nProcedimiento: (c · u)_i = c · u_i.")
            elif op == "punto":
                r = producto_punto(u, v)
                self.txt_res_vec.insert(tk.END, f"Producto Punto Euclídeo u · v:\nResultado = {format_number(r)}\n\nProcedimiento: Sumatoria u_i · v_i.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # 2. Pestaña Combinación Lineal
    def _armar_tab_combinacion(self):
        f = tk.Frame(self.tab_combinacion, bg="#1E293B", padx=16, pady=16)
        f.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(f, text="Ingrese los vectores del conjunto (uno por línea, componentes separados por coma):", bg="#1E293B", fg="#94A3B8").pack(anchor="w", pady=2)
        self.txt_comb_vecs = tk.Text(f, bg="#0F172A", fg="#38BDF8", font=("Consolas", 10), height=5, width=45)
        self.txt_comb_vecs.pack(anchor="w", pady=4)
        self.txt_comb_vecs.insert(tk.END, "1, 2\n3, 4")

        tk.Label(f, text="Vector objetivo b a evaluar:", bg="#1E293B", fg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.ent_comb_b = tk.Entry(f, bg="#0F172A", fg="#38BDF8", insertbackground="white", font=("Consolas", 11), width=45)
        self.ent_comb_b.pack(anchor="w", pady=2)
        self.ent_comb_b.insert(0, "5, 6")

        tk.Button(f, text="🔍 Evaluar Combinación Lineal", bg="#0284C7", fg="white", font=("Segoe UI", 10, "bold"), padx=12, pady=6, command=self._calc_comb).pack(anchor="w", pady=8)

        self.txt_res_comb = tk.Text(f, bg="#0F172A", fg="#F8FAFC", font=("Consolas", 10), height=10, relief="flat", padx=8, pady=8)
        self.txt_res_comb.pack(fill="both", expand=True, pady=4)

    def _calc_comb(self):
        try:
            lineas = [line.strip() for line in self.txt_comb_vecs.get("1.0", tk.END).strip().split("\n") if line.strip()]
            vecs = [self._parse_vec(l) for l in lineas]
            b = self._parse_vec(self.ent_comb_b.get())

            res = evaluar_combinacion_lineal(vecs, b)
            self.txt_res_comb.delete("1.0", tk.END)
            self.txt_res_comb.insert(tk.END, f"--- DICTAMEN: {res.tipo_solucion} ---\n\n")
            self.txt_res_comb.insert(tk.END, f"Fórmula: {res.expresion_algebraica}\n\n")
            self.txt_res_comb.insert(tk.END, f"Justificación teórica:\n{res.justificacion_teorica}\n\n")
            if res.comprobacion_sustitucion:
                self.txt_res_comb.insert(tk.END, "Comprobación:\n" + "\n".join(res.comprobacion_sustitucion))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # 3. Pestaña Matrices
    def _armar_tab_matrices(self):
        f = tk.Frame(self.tab_matrices, bg="#1E293B", padx=16, pady=16)
        f.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(f, text="Matriz A (filas separadas por saltos de línea, columnas por comas):", bg="#1E293B", fg="#94A3B8").pack(anchor="w")
        self.txt_mat_a = tk.Text(f, bg="#0F172A", fg="#38BDF8", font=("Consolas", 10), height=4, width=45)
        self.txt_mat_a.pack(anchor="w", pady=2)
        self.txt_mat_a.insert(tk.END, "1, 2, 3\n4, 5, 6")

        tk.Label(f, text="Matriz B:", bg="#1E293B", fg="#94A3B8").pack(anchor="w")
        self.txt_mat_b = tk.Text(f, bg="#0F172A", fg="#38BDF8", font=("Consolas", 10), height=4, width=45)
        self.txt_mat_b.pack(anchor="w", pady=2)
        self.txt_mat_b.insert(tk.END, "7, 8\n9, 1\n2, 3")

        btns_m = tk.Frame(f, bg="#1E293B")
        btns_m.pack(anchor="w", pady=8)

        tk.Button(btns_m, text="Multiplicar A · B", bg="#0284C7", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=lambda: self._calc_mat("mult")).pack(side="left", padx=4)
        tk.Button(btns_m, text="Sumar A + B", bg="#2563EB", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=lambda: self._calc_mat("suma")).pack(side="left", padx=4)
        tk.Button(btns_m, text="Restar A - B", bg="#2563EB", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=lambda: self._calc_mat("resta")).pack(side="left", padx=4)

        self.txt_res_mat = tk.Text(f, bg="#0F172A", fg="#F8FAFC", font=("Consolas", 10), height=8, relief="flat", padx=8, pady=8)
        self.txt_res_mat.pack(fill="both", expand=True, pady=4)

    def _parse_mat(self, widget):
        lineas = [l.strip() for l in widget.get("1.0", tk.END).strip().split("\n") if l.strip()]
        return [self._parse_vec(l) for l in lineas]

    def _calc_mat(self, op):
        try:
            A = self._parse_mat(self.txt_mat_a)
            B = self._parse_mat(self.txt_mat_b)
            self.txt_res_mat.delete("1.0", tk.END)

            if op == "mult":
                C, pasos = multiplicar_matrices(A, B)
                self.txt_res_mat.insert(tk.END, f"Matriz Producto C = A · B:\n{formatear_matriz(C)}\n\n")
                self.txt_res_mat.insert(tk.END, "Desglose de sumatorias c_ij:\n" + "\n".join(pasos))
            elif op == "suma":
                C = suma_matrices(A, B)
                self.txt_res_mat.insert(tk.END, f"Matriz Suma C = A + B:\n{formatear_matriz(C)}")
            elif op == "resta":
                C = resta_matrices(A, B)
                self.txt_res_mat.insert(tk.END, f"Matriz Resta C = A - B:\n{formatear_matriz(C)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # 4. Pestaña Ax = b
    def _armar_tab_ecuaciones(self):
        f = tk.Frame(self.tab_ecuaciones, bg="#1E293B", padx=16, pady=16)
        f.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(f, text="Matriz de Coeficientes A (m x n):", bg="#1E293B", fg="#94A3B8").pack(anchor="w")
        self.txt_eq_a = tk.Text(f, bg="#0F172A", fg="#38BDF8", font=("Consolas", 10), height=4, width=45)
        self.txt_eq_a.pack(anchor="w", pady=2)
        self.txt_eq_a.insert(tk.END, "1, 1, 1\n0, 2, 5\n2, 5, -1")

        tk.Label(f, text="Vector de Términos Independientes b (m x 1):", bg="#1E293B", fg="#94A3B8").pack(anchor="w")
        self.ent_eq_b = tk.Entry(f, bg="#0F172A", fg="#38BDF8", insertbackground="white", font=("Consolas", 11), width=45)
        self.ent_eq_b.pack(anchor="w", pady=2)
        self.ent_eq_b.insert(0, "6, -4, 27")

        tk.Button(f, text="⚡ Resolver Ax = b con Gauss-Jordan", bg="#0284C7", fg="white", font=("Segoe UI", 10, "bold"), padx=12, pady=6, command=self._calc_eq).pack(anchor="w", pady=8)

        self.txt_res_eq = tk.Text(f, bg="#0F172A", fg="#F8FAFC", font=("Consolas", 10), height=8, relief="flat", padx=8, pady=8)
        self.txt_res_eq.pack(fill="both", expand=True, pady=4)

    def _calc_eq(self):
        try:
            A = self._parse_mat(self.txt_eq_a)
            b = self._parse_vec(self.ent_eq_b.get())

            res = resolver_ecuacion_matricial(A, b)
            self.txt_res_eq.delete("1.0", tk.END)
            self.txt_res_eq.insert(tk.END, f"Clasificación: {res.tipo_sistema}\n{res.descripcion_sistema}\n\n")
            self.txt_res_eq.insert(tk.END, f"Solución: {res.solucion_dict}\n\n")
            if res.verificacion_residual:
                self.txt_res_eq.insert(tk.END, "Verificación:\n" + "\n".join(res.verificacion_residual))
        except Exception as e:
            messagebox.showerror("Error", str(e))


def launch_gui_tk():
    root = tk.Tk()
    app = AlgebraLinealTkApp(root)
    root.mainloop()
