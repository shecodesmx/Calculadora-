import customtkinter as ctk
import math
import re
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_main":      "#1a1a2e",
    "bg_display":   "#0d0d1a",
    "bg_history":   "#12122a",
    "bg_frame":     "#16213e",
    "btn_number":   "#1e2a4a",
    "btn_op":       "#0f3460",
    "btn_special":  "#533483",
    "btn_equals":   "#e94560",
    "btn_number_h": "#2a3a62",
    "btn_op_h":     "#1a4a80",
    "btn_special_h":"#6a45a0",
    "btn_equals_h": "#ff6b7a",
    "text_main":    "#e8eaf6",
    "text_dim":     "#7986cb",
    "text_accent":  "#e94560",
    "text_history": "#9fa8da",
    "text_small":   "#546e7a",
}

class HistorialPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color=COLORS["bg_history"],
                         corner_radius=16,
                         **kwargs)

        self._titulo = ctk.CTkLabel(
            self,
            text="Historial",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_dim"],
        )
        self._titulo.pack(pady=(14, 4), padx=14, anchor="w")

        sep = ctk.CTkFrame(self, height=1, fg_color=COLORS["btn_op"], corner_radius=0)
        sep.pack(fill="x", padx=14, pady=(0, 8))

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["btn_op"],
            scrollbar_button_hover_color=COLORS["btn_op_h"],
        )
        self._scroll.pack(fill="both", expand=True, padx=6, pady=(0, 10))

        self._btn_clear = ctk.CTkButton(
            self,
            text="Limpiar",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["btn_special"],
            hover_color=COLORS["btn_special_h"],
            corner_radius=8,
            command=self.limpiar,
        )
        self._btn_clear.pack(pady=(0, 12), padx=14, fill="x")

        self._entradas = []

    def agregar(self, expresion: str, resultado: str):
        marca = datetime.now().strftime("%H:%M")

        frame = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_frame"], corner_radius=8)
        frame.pack(fill="x", padx=4, pady=3)

        ctk.CTkLabel(
            frame,
            text=expresion,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_history"],
            anchor="e",
            wraplength=140,
        ).pack(fill="x", padx=10, pady=(6, 0))

        ctk.CTkLabel(
            frame,
            text=f"= {resultado}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_main"],
            anchor="e",
        ).pack(fill="x", padx=10, pady=(0, 2))

        ctk.CTkLabel(
            frame,
            text=marca,
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_small"],
            anchor="e",
        ).pack(fill="x", padx=10, pady=(0, 5))

        self._entradas.append(frame)
        self._scroll._parent_canvas.yview_moveto(1.0)

    def limpiar(self):
        for widget in self._entradas:
            widget.destroy()
        self._entradas.clear()

class Pantalla(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color=COLORS["bg_display"],
                         corner_radius=14,
                         **kwargs)

        self._lbl_expr = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_dim"],
            anchor="e",
        )
        self._lbl_expr.pack(fill="x", padx=20, pady=(18, 0))

        self._lbl_valor = ctk.CTkLabel(
            self,
            text="0",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color=COLORS["text_main"],
            anchor="e",
        )
        self._lbl_valor.pack(fill="x", padx=20, pady=(0, 16))

    def set_valor(self, texto: str):
        if len(texto) > 14:
            try:
                num = float(texto)
                texto = f"{num:.6g}"
            except ValueError:
                texto = texto[-14:]
        self._lbl_valor.configure(text=texto)

    def set_expresion(self, texto: str):
        self._lbl_expr.configure(text=texto)

    def set_error(self, msg: str = "Error"):
        self._lbl_valor.configure(text=msg, text_color=COLORS["text_accent"])

    def reset_color(self):
        self._lbl_valor.configure(text_color=COLORS["text_main"])

class BotonCalc(ctk.CTkButton):
    def __init__(self, master, texto, color, hover, callback, span=1, **kwargs):
        super().__init__(
            master,
            text=texto,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=color,
            hover_color=hover,
            text_color=COLORS["text_main"],
            corner_radius=12,
            height=58,
            command=lambda: callback(texto),
            **kwargs,
        )
        self._span = span

class Calculadora(ctk.CTk):
    def __init__(self):
        super().__init__()

        self._expresion = ""
        self._nuevo_num = True
        self._ultimo_res = ""
        self._modo_cientifico = False

        self.title("Calculadora")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])
        self._centrar_ventana(740, 560)

        self.attributes("-alpha", 0.0)

        self._construir_ui()
        self._vincular_teclado()
        self.after(50, self._animar_apertura)

    def _construir_ui(self):
        raiz = ctk.CTkFrame(self, fg_color="transparent")
        raiz.pack(fill="both", expand=True, padx=16, pady=16)

        col_izq = ctk.CTkFrame(raiz, fg_color="transparent")
        col_izq.pack(side="left", fill="both", expand=True)

        self._construir_barra(col_izq)

        self._pantalla = Pantalla(col_izq)
        self._pantalla.pack(fill="x", padx=0, pady=(8, 12))

        frame_botones = ctk.CTkFrame(col_izq,
                                     fg_color=COLORS["bg_frame"],
                                     corner_radius=16)
        frame_botones.pack(fill="both", expand=True)
        self._construir_botones(frame_botones)

        self._panel_historial = HistorialPanel(raiz, width=180)
        self._panel_historial.pack(side="right", fill="both",
                                   padx=(12, 0), expand=False)

    def _construir_barra(self, parent):
        barra = ctk.CTkFrame(parent, fg_color="transparent")
        barra.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(
            barra,
            text="Calculadora",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["text_dim"],
        ).pack(side="left")

        self._badge_modo = ctk.CTkLabel(
            barra,
            text="⊕ Científico",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_small"],
            cursor="hand2",
        )
        self._badge_modo.pack(side="right", padx=4)
        self._badge_modo.bind("<Button-1>", self._toggle_modo)

    def _construir_botones(self, parent):
        for c in range(4):
            parent.columnconfigure(c, weight=1)
        for r in range(5):
            parent.rowconfigure(r, weight=1)

        N = COLORS["btn_number"]
        NH = COLORS["btn_number_h"]
        O = COLORS["btn_op"]
        OH = COLORS["btn_op_h"]
        S = COLORS["btn_special"]
        SH = COLORS["btn_special_h"]
        E = COLORS["btn_equals"]
        EH = COLORS["btn_equals_h"]

        botones = [
            ("C",  S, SH, 0, 0, 1),
            ("⌫",  S, SH, 0, 1, 1),
            ("%",  O, OH, 0, 2, 1),
            ("÷",  O, OH, 0, 3, 1),
            ("7",  N, NH, 1, 0, 1),
            ("8",  N, NH, 1, 1, 1),
            ("9",  N, NH, 1, 2, 1),
            ("×",  O, OH, 1, 3, 1),
            ("4",  N, NH, 2, 0, 1),
            ("5",  N, NH, 2, 1, 1),
            ("6",  N, NH, 2, 2, 1),
            ("−",  O, OH, 2, 3, 1),
            ("1",  N, NH, 3, 0, 1),
            ("2",  N, NH, 3, 1, 1),
            ("3",  N, NH, 3, 2, 1),
            ("+",  O, OH, 3, 3, 1),
            ("±",  N, NH, 4, 0, 1),
            ("0",  N, NH, 4, 1, 1),
            (".",  N, NH, 4, 2, 1),
            ("=",  E, EH, 4, 3, 1),
        ]

        for txt, color, hover, fila, col, span in botones:
            btn = BotonCalc(
                parent,
                texto=txt,
                color=color,
                hover=hover,
                callback=self._manejar_boton,
                span=span,
            )
            btn.grid(
                row=fila, column=col,
                columnspan=span,
                padx=6, pady=6,
                sticky="nsew",
            )

    def _manejar_boton(self, valor: str):
        self._pantalla.reset_color()

        if valor == "C":
            self._limpiar_todo()
        elif valor == "⌫":
            self._borrar_ultimo()
        elif valor == "=":
            self._calcular()
        elif valor == "±":
            self._invertir_signo()
        elif valor == "%":
            self._aplicar_porcentaje()
        elif valor in ("÷", "×", "−", "+"):
            self._ingresar_operador(valor)
        elif valor == ".":
            self._ingresar_decimal()
        else:
            self._ingresar_digito(valor)

    def _ingresar_digito(self, digito: str):
        if self._nuevo_num:
            self._expresion = digito
            self._nuevo_num = False
        else:
            if self._expresion == "0":
                self._expresion = digito
            else:
                self._expresion += digito
        self._pantalla.set_valor(self._expresion)

    def _ingresar_decimal(self):
        if self._nuevo_num:
            self._expresion = "0."
            self._nuevo_num = False
        elif "." not in self._expresion.split()[-1]:
            self._expresion += "."
        self._pantalla.set_valor(self._expresion)

    def _ingresar_operador(self, op: str):
        if self._expresion == "" and self._ultimo_res:
            self._expresion = self._ultimo_res

        if self._expresion:
            self._expresion += f" {op} "
            self._pantalla.set_expresion(self._expresion)
            self._pantalla.set_valor(op)
            self._nuevo_num = False

    def _calcular(self):
        if not self._expresion or self._expresion.endswith((" ÷ ", " × ", " − ", " + ")):
            return

        expr_display = self._expresion

        try:
            expr_python = (
                self._expresion
                .replace("÷", "/")
                .replace("×", "*")
                .replace("−", "-")
            )

            if not re.match(r'^[\d\s\+\-\*/\.\(\)]+$', expr_python):
                raise ValueError("Expresión inválida")

            resultado = eval(expr_python)

            if isinstance(resultado, float):
                if resultado.is_integer():
                    resultado_str = str(int(resultado))
                else:
                    resultado_str = f"{resultado:.10g}"
            else:
                resultado_str = str(resultado)

            self._panel_historial.agregar(expr_display, resultado_str)

            self._pantalla.set_expresion(f"{expr_display} =")
            self._pantalla.set_valor(resultado_str)

            self._ultimo_res = resultado_str
            self._expresion = resultado_str
            self._nuevo_num = True

        except ZeroDivisionError:
            self._pantalla.set_error("÷ 0  Error")
            self._limpiar_todo()
        except Exception:
            self._pantalla.set_error("Error")
            self._limpiar_todo()

    def _limpiar_todo(self):
        self._expresion = ""
        self._nuevo_num = True
        self._ultimo_res = ""
        self._pantalla.set_valor("0")
        self._pantalla.set_expresion("")
        self._pantalla.reset_color()

    def _borrar_ultimo(self):
        if self._expresion and not self._nuevo_num:
            self._expresion = self._expresion[:-1].rstrip()
            self._pantalla.set_valor(self._expresion if self._expresion else "0")
            if not self._expresion:
                self._nuevo_num = True

    def _invertir_signo(self):
        if self._expresion and self._expresion not in ("", "0"):
            try:
                val = float(self._expresion)
                val = -val
                self._expresion = f"{val:g}"
                self._pantalla.set_valor(self._expresion)
            except ValueError:
                pass

    def _aplicar_porcentaje(self):
        try:
            val = float(self._expresion)
            val /= 100
            self._expresion = f"{val:g}"
            self._pantalla.set_valor(self._expresion)
        except ValueError:
            pass

    def _vincular_teclado(self):
        mapa = {
            "<Return>":    lambda e: self._manejar_boton("="),
            "<KP_Enter>":  lambda e: self._manejar_boton("="),
            "<BackSpace>": lambda e: self._manejar_boton("⌫"),
            "<Escape>":    lambda e: self._manejar_boton("C"),
            "<period>":    lambda e: self._manejar_boton("."),
            "<KP_Decimal>":lambda e: self._manejar_boton("."),
            "<plus>":      lambda e: self._manejar_boton("+"),
            "<minus>":     lambda e: self._manejar_boton("−"),
            "<asterisk>":  lambda e: self._manejar_boton("×"),
            "<slash>":     lambda e: self._manejar_boton("÷"),
            "<percent>":   lambda e: self._manejar_boton("%"),
        }

        for tecla, accion in mapa.items():
            self.bind(tecla, accion)

        for i in range(10):
            self.bind(str(i), lambda e, d=str(i): self._manejar_boton(d))
            self.bind(f"<KP_{i}>", lambda e, d=str(i): self._manejar_boton(d))

    def _toggle_modo(self, event=None):
        self._modo_cientifico = not self._modo_cientifico
        if self._modo_cientifico:
            self._badge_modo.configure(
                text="⊖ Básico",
                text_color=COLORS["text_accent"]
            )
        else:
            self._badge_modo.configure(
                text="⊕ Científico",
                text_color=COLORS["text_small"]
            )

    def _centrar_ventana(self, ancho: int, alto: int):
        self.update_idletasks()
        w_pantalla = self.winfo_screenwidth()
        h_pantalla = self.winfo_screenheight()
        x = (w_pantalla - ancho) // 2
        y = (h_pantalla - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _animar_apertura(self, alpha: float = 0.0):
        alpha = min(alpha + 0.06, 1.0)
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(16, self._animar_apertura, alpha)

if __name__ == "__main__":
    app = Calculadora()
    app.mainloop()