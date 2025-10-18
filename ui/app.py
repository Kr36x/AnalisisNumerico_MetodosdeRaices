import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import math

from analisisNumerico_app.core.functions import make_func, eval_scalar
from analisisNumerico_app.core.derivative import numeric_derivative
from analisisNumerico_app.core.newton import newton_with_log
from analisisNumerico_app.core.fixed_point import fixed_point_with_log
from analisisNumerico_app.core.bisection import bisection_with_log


METHODS = ["Newton-Raphson", "Punto Fijo", "Bisección"]


class NewtonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Análisis Numérico — Métodos de Raíces - by @Kr_36x")
        self.geometry("900x600")
        self.minsize(880, 560)
        self._create_menu()
        self._create_widgets()
        self._apply_style()
        self._toggle_inputs()  # inicializa visibilidad

    # ---------- Menú ----------
    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exportar tabla a CSV...", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Ejemplo rápido", command=self._fill_example)
        help_menu.add_command(label="Acerca de", command=self._show_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.config(menu=menubar)

    # ---------- Widgets ----------
    def _create_widgets(self):
        frm_top = ttk.Frame(self, padding=12)
        frm_top.pack(fill="x")

        # Configuración de columnas (4 columnas uniformes)
        for c in range(4):
            frm_top.columnconfigure(c, weight=1, uniform="form")

        # Método
        ttk.Label(frm_top, text="Método:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 8))
        self.var_method = tk.StringVar(value=METHODS[0])
        self.cmb_method = ttk.Combobox(
            frm_top, values=METHODS, textvariable=self.var_method, state="readonly", width=22
        )
        self.cmb_method.grid(row=0, column=1, sticky="we", pady=(0, 8))
        self.cmb_method.bind("<<ComboboxSelected>>", lambda e: self._toggle_inputs())

        # Botón calcular (alineado extremo derecho)
        ttk.Button(frm_top, text="Calcular", command=self._run_method)\
            .grid(row=0, column=3, sticky="e", pady=(0, 8))

        # ---- Campos (labels + entries) en posiciones consistentes ----
        # f(x)
        self.var_fx = tk.StringVar(value="cos(x) - x")
        self.lbl_fx, self.ent_fx = self._labeled_entry(frm_top, "f(x):", self.var_fx, row=1, entry_span=3)

        # f'(x) (Newton)
        self.var_dfx = tk.StringVar(value="")
        self.lbl_dfx, self.ent_dfx = self._labeled_entry(frm_top, "f'(x) (opcional):", self.var_dfx, row=2, entry_span=3)

        # g(x) (Punto Fijo)
        self.var_gx = tk.StringVar(value="")
        self.lbl_gx, self.ent_gx = self._labeled_entry(frm_top, "g(x):", self.var_gx, row=3, entry_span=3)

        # --- Punto Fijo: usar intervalo en lugar de P0 ---
        self.var_use_interval = tk.BooleanVar(value=False)
        self.chk_use_interval = ttk.Checkbutton(
            frm_top, text="Punto Fijo: usar intervalo [a,b]", variable=self.var_use_interval,
            command=self._toggle_inputs
        )
        self.chk_use_interval.grid(row=4, column=0, columnspan=2, sticky="w", pady=4)

        # P0 (Newton / Punto Fijo)
        self.var_p0 = tk.StringVar(value="pi/4")
        self.lbl_p0, self.ent_p0 = self._labeled_entry(frm_top, "P₀:", self.var_p0, row=5, entry_span=1)

       # a y b (Bisección o Punto Fijo con intervalo)
        self.var_a = tk.StringVar(value="0.2")
        self.var_b = tk.StringVar(value="0.3")
        self.lbl_a = ttk.Label(frm_top, text="a:")
        self.lbl_a.grid(row=6, column=0, sticky="w", padx=(0, 8), pady=4)
        self.ent_a = ttk.Entry(frm_top, textvariable=self.var_a)
        self.ent_a.grid(row=6, column=1, sticky="we", pady=4)

        self.lbl_b = ttk.Label(frm_top, text="b:")
        self.lbl_b.grid(row=6, column=2, sticky="w", padx=(16, 8), pady=4)
        self.ent_b = ttk.Entry(frm_top, textvariable=self.var_b)
        self.ent_b.grid(row=6, column=3, sticky="we", pady=4)
        
        # Tolerancia (10^-n)
        ttk.Label(frm_top, text="Tolerancia (10^-n):")\
            .grid(row=7, column=0, sticky="e", padx=(0, 8), pady=(8, 4))
        self.var_tol_exp = tk.StringVar(value="7")
        ttk.Entry(frm_top, textvariable=self.var_tol_exp)\
            .grid(row=7 , column=1, sticky="we", pady=(8, 4))

        # Máx. iteraciones
        ttk.Label(frm_top, text="Máx. iteraciones:")\
            .grid(row=7, column=2, sticky="e", padx=(16, 8), pady=(8, 4))
        self.var_maxiter = tk.StringVar(value="50")
        ttk.Entry(frm_top, textvariable=self.var_maxiter)\
            .grid(row=7, column=3, sticky="we", pady=(8, 4))

        ttk.Separator(self).pack(fill="x", pady=6)

        # Tabla
        frm_table = ttk.Frame(self, padding=(12, 0, 12, 12))
        frm_table.pack(fill="both", expand=True)

        columns = ("iter", "Pn", "fPn", "error")
        self.tree = ttk.Treeview(frm_table, columns=columns, show="headings", height=14)
        self.tree.heading("iter", text="Iter")
        self.tree.heading("Pn", text="Pn")
        self.tree.heading("fPn", text="f(Pn)")
        self.tree.heading("error", text="Error")
        self.tree.column("iter", anchor="center", width=60, stretch=False)
        self.tree.column("Pn", anchor="w")
        self.tree.column("fPn", anchor="w")
        self.tree.column("error", anchor="w")

        vsb = ttk.Scrollbar(frm_table, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frm_table.rowconfigure(0, weight=1)
        frm_table.columnconfigure(0, weight=1)

        # Status
        frm_status = ttk.Frame(self, padding=(12, 0, 12, 12))
        frm_status.pack(fill="x")
        self.lbl_result = ttk.Label(frm_status, text="Resultado: —")
        self.lbl_result.pack(side="left")

        

    def _labeled_entry(self, parent, label_text, var, row, entry_span=3):
        """Crea (label, entry) con label en col0 y entry en col1..(1+entry_span-1)."""
        lbl = ttk.Label(parent, text=label_text)
        lbl.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        ent = ttk.Entry(parent, textvariable=var)
        ent.grid(row=row, column=1, columnspan=entry_span, sticky="we", pady=4)
        return lbl, ent

    def _apply_style(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Treeview", rowheight=24)

    def _toggle_inputs(self):
        m = self.var_method.get()

        fx = (self.lbl_fx, self.ent_fx)
        dfx = (self.lbl_dfx, self.ent_dfx)
        gx  = (self.lbl_gx, self.ent_gx)
        p0  = (self.lbl_p0, self.ent_p0)
        a_pair = (self.lbl_a, self.ent_a)
        b_pair = (self.lbl_b, self.ent_b)

        if m == "Newton-Raphson":
            self._show_widgets([fx, dfx, p0])
            self._hide_widgets([gx, a_pair, b_pair])
            self.chk_use_interval.grid_remove()

        elif m == "Punto Fijo":
            self._show_widgets([gx])
            self.chk_use_interval.grid()

            if self.var_use_interval.get():
                # Con intervalo: mostrar a, b y también P0 (opcional)
                self._show_widgets([a_pair, b_pair, p0])
                self._hide_widgets([fx, dfx])
            else:
                # Sin intervalo: sólo P0
                self._show_widgets([p0])
                self._hide_widgets([a_pair, b_pair, fx, dfx])

        else:  # Bisección
            self.chk_use_interval.grid_remove()
            self._show_widgets([fx, a_pair, b_pair])
            self._hide_widgets([dfx, gx, p0])



    def _show_widgets(self, pairs):
        for lbl, ent in pairs:
            lbl.grid()
            ent.grid()

    def _hide_widgets(self, pairs):
        for lbl, ent in pairs:
            lbl.grid_remove()
            ent.grid_remove()

    def _clear_table(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)

    # ---------- Lógica: ejecuta el método seleccionado ----------
    def _run_method(self):
        # tolerancia y max_iter
        try:
            n = int(self.var_tol_exp.get())
            if n < 0:
                raise ValueError
            tol = 10.0 ** (-n)
        except Exception:
            messagebox.showerror("Error", "Tolerancia: ingresa un exponente entero n ≥ 0 (10^-n).")
            return

        try:
            max_iter = int(self.var_maxiter.get())
        except ValueError:
            messagebox.showerror("Error", "Máx. iteraciones debe ser entero.")
            return

        method = self.var_method.get()
        self._clear_table()

        try:
            if method == "Newton-Raphson":
                # f(x), f'(x) (opcional), P0
                f = make_func(self.var_fx.get())
                df = make_func(self.var_dfx.get()) if self.var_dfx.get().strip() else numeric_derivative(f)
                P0 = eval_scalar(self.var_p0.get())
                Pn, log = newton_with_log(f, df, P0, tol=tol, max_iter=max_iter)

            elif method == "Punto Fijo":
                g = make_func(self.var_gx.get())

                if self.var_use_interval.get():
                    # Leer intervalo
                    a = eval_scalar(self.var_a.get())
                    b = eval_scalar(self.var_b.get())
                    if a > b:
                        a, b = b, a

                    # Determinar P0:
                    p0_text = self.var_p0.get().strip()
                    if p0_text == "":
                        P0 = (a + b) / 2.0
                    else:
                        P0 = eval_scalar(p0_text)
                        # Validar que caiga en [a,b]
                        if not (min(a, b) <= P0 <= max(a, b)):
                            # Opción 1: ajustar al centro y avisar
                            messagebox.showinfo(
                                "Aviso Punto Fijo",
                                f"P₀={P0} está fuera del intervalo [{a}, {b}]. "
                                "Se ajustará al punto medio."
                            )
                            P0 = (a + b) / 2.0

                    # (Opcional) chequeos informativos
                    try:
                        ga, gb = g(a), g(b)
                        if not (a <= ga <= b) or not (a <= gb <= b):
                            messagebox.showinfo(
                                "Aviso Punto Fijo",
                                "g(x) podría no mapear [a,b] dentro de sí mismo."
                            )
                    except Exception:
                        pass

                    try:
                        gp = numeric_derivative(g)
                        c = (a + b) / 2.0
                        if abs(gp(c)) >= 1:
                            messagebox.showinfo(    
                                "Aviso Punto Fijo",
                                "|g'(c)| ≥ 1 en el centro; la convergencia puede ser lenta o no darse."
                            )
                    except Exception:
                        pass

                else:
                    # Sin intervalo → usar P0 directo
                    P0 = eval_scalar(self.var_p0.get())

                Pn, log = fixed_point_with_log(g, P0, tol=tol, max_iter=max_iter)

                # Para la tabla: fPn como g(Pn)-Pn (indicador de "casi raíz")
                import math as _math
                for r in log:
                    try:
                        r["fPn"] = g(r["Pn"]) - r["Pn"]
                    except Exception:
                        r["fPn"] = _math.nan

            else:  # Bisección
                # f(x), a, b
                f = make_func(self.var_fx.get())
                a = eval_scalar(self.var_a.get())
                b = eval_scalar(self.var_b.get())
                Pn, log = bisection_with_log(f, a, b, tol=tol, max_iter=max_iter)

            # Poblar tabla
            for row in log:
                self.tree.insert("", "end", values=(
                    row["iter"],    
                    f"{row['Pn']:.10f}",
                    f"{row['fPn']:.10e}" if not (row["fPn"] != row["fPn"]) else "NaN",  # NaN check
                    f"{row['error']:.10e}",
                ))

            # Resultado
            last_err = log[-1]["error"] if log else float("nan")
            last_f = log[-1]["fPn"] if log else float("nan")
            msg = "Convergencia" if (not math.isnan(last_err) and last_err < tol) else "Finalizado"
            self.lbl_result.config(
                text=f"Método: {method} | P*: {Pn:.10f} | f(P*)={last_f:.3e} | err={last_err:.3e} | tol={tol:.1e} | {msg}"
            )

        except Exception as e:
            messagebox.showerror("Error en cálculo", str(e))

    # ---------- Utilidades ----------
    def _export_csv(self):
        if not self.tree.get_children():
            messagebox.showinfo("Exportar CSV", "No hay datos en la tabla.")
            return
        path = filedialog.asksaveasfilename(
            title="Guardar tabla como CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Iter", "Pn", "f(Pn)", "Error"])
                for iid in self.tree.get_children():
                    w.writerow(self.tree.item(iid, "values"))
            messagebox.showinfo("Exportar CSV", "Tabla exportada correctamente.")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    def _fill_example(self):
        m = self.var_method.get()
        if m == "Newton-Raphson":
            self.var_fx.set("cos(x) - x")
            self.var_dfx.set("")
            self.var_p0.set("pi/4")
            self.var_tol_exp.set("7")
            self.var_maxiter.set("20")
        elif m == "Punto Fijo":
            # Un g(x) que converja: x = cos(x)  → g(x)=cos(x)
            self.var_gx.set("cos(x)")
            self.var_p0.set("pi/4")
            self.var_tol_exp.set("7")
            self.var_maxiter.set("50")
        else:  # Bisección
            self.var_fx.set("x**3 - x - 1")
            self.var_a.set("1")
            self.var_b.set("2")
            self.var_tol_exp.set("6")
            self.var_maxiter.set("60")
        messagebox.showinfo("Ejemplo", f"Ejemplo cargado para {m}.")

    def _show_about(self):
        messagebox.showinfo(
            "Acerca de",
            "Análisis Numérico — Métodos de raíces:\n"
            "• Newton-Raphson, Punto Fijo, Bisección.\n"
            "• Tol = 10^-n (ingresa n). P₀, a, b aceptan expresiones: pi/4, 1/3, sqrt(2)/2.\n"
            "• Exporta resultados a CSV."
        )
