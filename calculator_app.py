import customtkinter as ctk
import math
import json
import os
from datetime import datetime

# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

HISTORY_FILE = "calc_history.json"

# ── Button color palette ───────────────────────────────────────────────────────
CLR_NUM     = ("#2a2a3d", "#3a3a55")   # number buttons  (fg, hover)
CLR_OP      = ("#1e3a5f", "#2a5080")   # operator buttons
CLR_SCI     = ("#1a3a2a", "#236b3e")   # scientific buttons
CLR_EQ      = ("#7c3aed", "#6d28d9")   # equals
CLR_CLEAR   = ("#5f1e1e", "#8b2020")   # clear / delete
CLR_MEM     = ("#3a2a1e", "#6b4a1e")   # memory


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-100:], f, indent=2)   # keep last 100


# ── Main App ───────────────────────────────────────────────────────────────────
class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧮  Calculator  •  Scientific")
        self.geometry("720x620")
        self.minsize(680, 580)
        self.configure(fg_color="#0d0d1a")
        self.resizable(True, True)

        self.expression = ""          # current build string
        self.just_evaluated = False   # flag after pressing =
        self.memory = 0.0
        self.history = load_history()

        self._build_ui()
        self.bind("<Key>", self._on_key)

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Main container: left=calc, right=history
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # ── LEFT: calculator panel ─────────────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color="#13132b", corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        # Expression label (small, shows full expression)
        self.expr_lbl = ctk.CTkLabel(
            left, text="", anchor="e",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color="#52526a",
        )
        self.expr_lbl.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 0))

        # Main display
        self.display = ctk.CTkLabel(
            left, text="0", anchor="e",
            font=ctk.CTkFont(family="Consolas", size=38, weight="bold"),
            text_color="#e4e4f0",
        )
        self.display.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))

        # Separator
        ctk.CTkFrame(left, fg_color="#2d2d42", height=1).grid(
            row=2, column=0, sticky="ew", padx=12)

        # Button grid frame
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        left.rowconfigure(3, weight=1)

        self._build_buttons(btn_frame)

        # ── RIGHT: history panel ───────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="#0a0a18", corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        hist_header = ctk.CTkFrame(right, fg_color="transparent")
        hist_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(16, 4))

        ctk.CTkLabel(
            hist_header, text="History",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#a1a1cc",
        ).pack(side="left")

        ctk.CTkButton(
            hist_header, text="Clear",
            width=54, height=24, corner_radius=6,
            fg_color="transparent", border_width=1,
            border_color="#3f3f5a", hover_color="#2d1515",
            text_color="#71717a", font=ctk.CTkFont(size=11),
            command=self._clear_history,
        ).pack(side="right")

        self.hist_scroll = ctk.CTkScrollableFrame(
            right, fg_color="transparent",
            scrollbar_button_color="#2d2d42",
        )
        self.hist_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self._refresh_history()

    def _make_btn(self, parent, text, row, col,
                  colors=CLR_NUM, rowspan=1, colspan=1,
                  action=None):
        fg, hover = colors
        cmd = action if action else (lambda t=text: self._on_btn(t))
        btn = ctk.CTkButton(
            parent, text=text,
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            fg_color=fg, hover_color=hover,
            corner_radius=8, height=52,
            command=cmd,
        )
        btn.grid(row=row, column=col,
                 rowspan=rowspan, columnspan=colspan,
                 padx=3, pady=3, sticky="nsew")
        return btn

    def _build_buttons(self, f):
        # Configure grid weights
        for c in range(5):
            f.columnconfigure(c, weight=1)
        for r in range(7):
            f.rowconfigure(r, weight=1)

        # Row 0 – Memory
        self._make_btn(f, "MC",  0, 0, CLR_MEM, action=lambda: self._mem("MC"))
        self._make_btn(f, "MR",  0, 1, CLR_MEM, action=lambda: self._mem("MR"))
        self._make_btn(f, "M+",  0, 2, CLR_MEM, action=lambda: self._mem("M+"))
        self._make_btn(f, "M-",  0, 3, CLR_MEM, action=lambda: self._mem("M-"))
        self._make_btn(f, "MS",  0, 4, CLR_MEM, action=lambda: self._mem("MS"))

        # Row 1 – Scientific
        self._make_btn(f, "sin",  1, 0, CLR_SCI, action=lambda: self._sci("sin"))
        self._make_btn(f, "cos",  1, 1, CLR_SCI, action=lambda: self._sci("cos"))
        self._make_btn(f, "tan",  1, 2, CLR_SCI, action=lambda: self._sci("tan"))
        self._make_btn(f, "log",  1, 3, CLR_SCI, action=lambda: self._sci("log"))
        self._make_btn(f, "ln",   1, 4, CLR_SCI, action=lambda: self._sci("ln"))

        # Row 2 – More scientific
        self._make_btn(f, "x²",  2, 0, CLR_SCI, action=lambda: self._sci("x²"))
        self._make_btn(f, "√x",  2, 1, CLR_SCI, action=lambda: self._sci("√x"))
        self._make_btn(f, "xʸ",  2, 2, CLR_SCI, action=lambda: self._append("**"))
        self._make_btn(f, "π",   2, 3, CLR_SCI, action=lambda: self._append(str(math.pi)))
        self._make_btn(f, "e",   2, 4, CLR_SCI, action=lambda: self._append(str(math.e)))

        # Row 3 – Clear / ops
        self._make_btn(f, "AC",  3, 0, CLR_CLEAR, action=self._all_clear)
        self._make_btn(f, "⌫",   3, 1, CLR_CLEAR, action=self._backspace)
        self._make_btn(f, "%",   3, 2, CLR_OP)
        self._make_btn(f, "(",   3, 3, CLR_OP)
        self._make_btn(f, ")",   3, 4, CLR_OP)

        # Row 4 – 7 8 9 ÷
        self._make_btn(f, "7", 4, 0)
        self._make_btn(f, "8", 4, 1)
        self._make_btn(f, "9", 4, 2)
        self._make_btn(f, "÷", 4, 3, CLR_OP, action=lambda: self._append("/"))
        self._make_btn(f, "1/x", 4, 4, CLR_SCI, action=lambda: self._sci("1/x"))

        # Row 5 – 4 5 6 ×
        self._make_btn(f, "4", 5, 0)
        self._make_btn(f, "5", 5, 1)
        self._make_btn(f, "6", 5, 2)
        self._make_btn(f, "×", 5, 3, CLR_OP, action=lambda: self._append("*"))
        self._make_btn(f, "±",  5, 4, CLR_OP,  action=self._negate)

        # Row 6 – 1 2 3 −
        self._make_btn(f, "1", 6, 0)
        self._make_btn(f, "2", 6, 1)
        self._make_btn(f, "3", 6, 2)
        self._make_btn(f, "−", 6, 3, CLR_OP, action=lambda: self._append("-"))
        self._make_btn(f, "=", 6, 4, CLR_EQ,  rowspan=2, action=self._evaluate)

        # Row 7 – 0 . +
        self._make_btn(f, "0", 7, 0, colspan=2)
        self._make_btn(f, ".", 7, 2)
        self._make_btn(f, "+", 7, 3, CLR_OP, action=lambda: self._append("+"))

    # ── Button actions ─────────────────────────────────────────────────────────
    def _on_btn(self, text):
        if text in "0123456789.":
            if self.just_evaluated:
                self.expression = ""
                self.just_evaluated = False
            self._append(text)
        elif text == "%":
            self._append("/100")

    def _append(self, char):
        if self.just_evaluated and char in "+-*//**":
            # continue from result
            self.just_evaluated = False
        elif self.just_evaluated:
            self.expression = ""
            self.just_evaluated = False
        self.expression += char
        self._update_display()

    def _all_clear(self):
        self.expression = ""
        self.just_evaluated = False
        self._update_display(main="0")

    def _backspace(self):
        self.expression = self.expression[:-1]
        self._update_display()

    def _negate(self):
        try:
            val = float(eval(self.expression or "0"))
            self.expression = str(-val)
            self._update_display()
        except Exception:
            pass

    def _sci(self, fn):
        try:
            val = float(eval(self.expression or "0"))
            ops = {
                "sin":  math.sin(math.radians(val)),
                "cos":  math.cos(math.radians(val)),
                "tan":  math.tan(math.radians(val)),
                "log":  math.log10(val),
                "ln":   math.log(val),
                "x²":   val ** 2,
                "√x":   math.sqrt(val),
                "1/x":  1 / val,
            }
            result = ops[fn]
            expr_str = f"{fn}({self._fmt(val)})"
            self._record(expr_str, result)
            self.expression = str(result)
            self.just_evaluated = True
            self._update_display(main=self._fmt(result), expr=expr_str)
        except Exception as ex:
            self._update_display(main="Error", expr=str(ex))
            self.expression = ""

    def _mem(self, op):
        try:
            val = float(eval(self.expression or "0"))
        except Exception:
            val = 0.0
        if op == "MC":
            self.memory = 0.0
        elif op == "MR":
            self.expression = str(self.memory)
            self._update_display()
        elif op == "M+":
            self.memory += val
        elif op == "M-":
            self.memory -= val
        elif op == "MS":
            self.memory = val

    def _evaluate(self):
        if not self.expression:
            return
        expr_str = self.expression
        try:
            result = eval(expr_str, {"__builtins__": {}}, {})
            self._record(expr_str, result)
            self.expression = str(result)
            self.just_evaluated = True
            self._update_display(main=self._fmt(result), expr=expr_str + " =")
        except ZeroDivisionError:
            self._update_display(main="÷0 Error", expr=expr_str)
            self.expression = ""
        except Exception:
            self._update_display(main="Error", expr=expr_str)
            self.expression = ""

    # ── Keyboard support ───────────────────────────────────────────────────────
    def _on_key(self, event):
        k = event.keysym
        char = event.char
        if char in "0123456789.+-*/()":
            self._append(char)
        elif k == "Return" or k == "equal":
            self._evaluate()
        elif k == "BackSpace":
            self._backspace()
        elif k == "Escape":
            self._all_clear()
        elif char == "%":
            self._append("/100")

    # ── Display ────────────────────────────────────────────────────────────────
    def _update_display(self, main=None, expr=None):
        if main is None:
            main = self._fmt_expr(self.expression) or "0"
        if expr is None:
            expr = ""
        self.display.configure(text=main)
        self.expr_lbl.configure(text=expr)

    def _fmt(self, val):
        """Format number: remove trailing .0 for integers."""
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return f"{val:.10g}"

    def _fmt_expr(self, expr):
        return (expr.replace("*", "×").replace("/", "÷")
                .replace("**", "^"))

    # ── History ────────────────────────────────────────────────────────────────
    def _record(self, expr, result):
        entry = {
            "expr": self._fmt_expr(expr),
            "result": self._fmt(result),
            "time": datetime.now().strftime("%H:%M"),
        }
        self.history.append(entry)
        save_history(self.history)
        self._refresh_history()

    def _clear_history(self):
        self.history = []
        save_history(self.history)
        self._refresh_history()

    def _refresh_history(self):
        for w in self.hist_scroll.winfo_children():
            w.destroy()

        if not self.history:
            ctk.CTkLabel(
                self.hist_scroll, text="No history yet",
                font=ctk.CTkFont(size=12), text_color="#3f3f5a",
            ).pack(pady=30)
            return

        for entry in reversed(self.history):
            card = ctk.CTkFrame(
                self.hist_scroll, fg_color="#1a1a2e",
                corner_radius=8,
            )
            card.pack(fill="x", padx=4, pady=3)

            ctk.CTkLabel(
                card, text=entry["expr"],
                anchor="e", font=ctk.CTkFont(family="Consolas", size=11),
                text_color="#52526a",
            ).pack(fill="x", padx=10, pady=(6, 0))

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=(0, 6))

            ctk.CTkLabel(
                row, text=f"= {entry['result']}",
                anchor="w",
                font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                text_color="#c4b5fd",
            ).pack(side="left")

            ctk.CTkLabel(
                row, text=entry["time"],
                anchor="e", font=ctk.CTkFont(size=10),
                text_color="#3f3f5a",
            ).pack(side="right")

            # Click to restore
            card.bind("<Button-1>", lambda e, r=entry["result"]: self._restore(r))

    def _restore(self, value):
        self.expression = value
        self.just_evaluated = False
        self._update_display(main=value)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
