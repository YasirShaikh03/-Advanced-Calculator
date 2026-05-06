# 🧮 Advanced Calculator with History

A dark-themed scientific calculator built with **CustomTkinter**, featuring a persistent history panel.

## ✨ Features

- ➕ Basic operations: `+  −  ×  ÷  %`
- 🔬 Scientific functions: `sin, cos, tan, log, ln, x², √x, xʸ, 1/x, π, e`
- 🧠 Memory: `MC  MR  M+  M−  MS`
- 📜 **History panel** — shows all past calculations with timestamps
- 🖱️ Click any history entry to restore its result
- ⌨️ **Full keyboard support** — type expressions naturally
- 💾 History saved to `calc_history.json` (last 100 entries)
- ➖ Supports parentheses `( )` and chained expressions

## 🚀 Installation

```bash
pip install customtkinter
```

## ▶️ Run

```bash
python calculator_app.py
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `0-9`, `.`, `+`, `-`, `*`, `/` | Input |
| `Enter` or `=` | Evaluate |
| `Backspace` | Delete last character |
| `Escape` | All Clear |
| `(` `)` | Parentheses |
| `%` | Percentage |

## 📁 Project Structure

```
calculator_app/
├── calculator_app.py    # Main application
├── calc_history.json    # Auto-created (history storage)
└── README.md
```

## 🧱 Tech Stack

| Library | Purpose |
|---|---|
| `customtkinter` | Modern UI widgets |
| `math` | Scientific functions |
| `json` | History persistence |

## 💡 OOP Design

- `CalculatorApp` — main window with display, button grid, history panel
- All state managed inside the class
