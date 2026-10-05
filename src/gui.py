import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mustang_core.compiler import compile_source
from mustang_core.decompiler import decompile_file_text

APP_TITLE = "Mustang"

BG = "#1b1b1f"
PANEL = "#242428"
FG = "#f2f2f2"
MUTED = "#9a9aa0"
ACCENT = "#ff7f32"
ACCENT_DARK = "#e06a20"
HOVER = "#2f2f35"
CLOSE_HOVER = "#c0392b"


class MustangApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.overrideredirect(True)
        self.configure(bg=BG)

        self._normal_geometry = "440x300+200+200"
        self.geometry(self._normal_geometry)
        self._is_maximized = False
        self._minimized = False
        self._drag_x = 0
        self._drag_y = 0

        self._build_header()
        self._build_body()
        self._set_app_icon()

        self.bind("<Map>", self._on_map)

    def _set_app_icon(self):
        icon_png = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "assets", "mustang_icon.png"
        )
        try:
            self._icon_image = tk.PhotoImage(file=icon_png)
            self.iconphoto(True, self._icon_image)
        except Exception:
            pass

    def _build_header(self):
        header = tk.Frame(self, bg=BG, height=34)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = tk.Label(
            header, text=APP_TITLE, bg=BG, fg=FG, font=("Segoe UI", 10, "bold")
        )
        title.pack(side="left", padx=12)

        btn_close = tk.Label(header, text="\u2715", bg=BG, fg=FG, width=3, font=("Segoe UI", 10))
        btn_close.pack(side="right")
        btn_close.bind("<Button-1>", lambda e: self.destroy())
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=CLOSE_HOVER))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=BG))

        btn_max = tk.Label(header, text="\u25a1", bg=BG, fg=FG, width=3, font=("Segoe UI", 10))
        btn_max.pack(side="right")
        btn_max.bind("<Button-1>", lambda e: self.toggle_maximize())
        btn_max.bind("<Enter>", lambda e: btn_max.config(bg=HOVER))
        btn_max.bind("<Leave>", lambda e: btn_max.config(bg=BG))

        btn_min = tk.Label(header, text="\u2013", bg=BG, fg=FG, width=3, font=("Segoe UI", 10))
        btn_min.pack(side="right")
        btn_min.bind("<Button-1>", lambda e: self.minimize())
        btn_min.bind("<Enter>", lambda e: btn_min.config(bg=HOVER))
        btn_min.bind("<Leave>", lambda e: btn_min.config(bg=BG))

        for widget in (header, title):
            widget.bind("<ButtonPress-1>", self._start_move)
            widget.bind("<B1-Motion>", self._do_move)

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_move(self, event):
        x = self.winfo_pointerx() - self._drag_x
        y = self.winfo_pointery() - self._drag_y
        self.geometry(f"+{x}+{y}")

    def minimize(self):
        self._minimized = True
        self.overrideredirect(False)
        self.iconify()

    def _on_map(self, event):
        if self._minimized and self.state() == "normal":
            self._minimized = False
            self.overrideredirect(True)

    def toggle_maximize(self):
        if self._is_maximized:
            self.geometry(self._normal_geometry)
            self._is_maximized = False
        else:
            self._normal_geometry = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"{sw}x{sh}+0+0")
            self._is_maximized = True
    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        tk.Label(
            body, text="Mustang", font=("Segoe UI", 20, "bold"), bg=BG, fg=ACCENT
        ).pack(pady=(20, 2))
        tk.Label(
            body, text="𝘈 𝘭𝘪𝘨𝘩𝘵𝘸𝘦𝘪𝘨𝘩𝘵 𝘱𝘺𝘵𝘩𝘰𝘯 𝘤𝘰𝘮𝘱𝘪𝘭𝘦𝘳.", font=("Segoe UI", 9), bg=BG, fg=MUTED
        ).pack(pady=(0, 18))

        self._make_button(body, "Compile .py .mustang", self.compile_file).pack(pady=6)
        self._make_button(body, "Decompile .mustang .py", self.decompile_file).pack(pady=6)

        self.status = tk.Label(body, text="www.ssb.surf/mustang", bg=BG, fg=MUTED)
        self.status.pack(pady=(16, 10))

    def _make_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            width=28,
            height=2,
            bg=PANEL,
            fg=FG,
            activebackground=ACCENT_DARK,
            activeforeground=FG,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=ACCENT,
            highlightcolor=ACCENT,
            cursor="hand2",
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=PANEL))
        return btn

    def set_status(self, text, color=MUTED):
        self.status.config(text=text, fg=color)
        self.update_idletasks()

    def compile_file(self):
        src_path = filedialog.askopenfilename(
            title="Select a .py file to compile",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        )
        if not src_path:
            return
        try:
            with open(src_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Could not read file:\n{exc}")
            self.set_status("Compile failed.", CLOSE_HOVER)
            return

        default_name = os.path.splitext(os.path.basename(src_path))[0] + ".mustang"
        out_path = filedialog.asksaveasfilename(
            title="Save compiled Mustang file as",
            initialfile=default_name,
            defaultextension=".mustang",
            filetypes=[("Mustang files", "*.mustang"), ("All files", "*.*")],
        )
        if not out_path:
            return

        try:
            compiled_text = compile_source(source_code, filename=os.path.basename(out_path))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(compiled_text)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Compile failed:\n{exc}")
            self.set_status("Compile failed.", CLOSE_HOVER)
            return

        self.set_status(f"Compiled {os.path.basename(out_path)}", ACCENT)
        messagebox.showinfo(
            APP_TITLE,
            f"Compiled successfully:\n{out_path}\n\n"
            f"Run it directly with:\npython \"{out_path}\"",
        )

    def decompile_file(self):
        src_path = filedialog.askopenfilename(
            title="Select a .mustang file to decompile",
            filetypes=[("Mustang files", "*.mustang"), ("All files", "*.*")],
        )
        if not src_path:
            return
        try:
            with open(src_path, "r", encoding="utf-8") as f:
                mustang_text = f.read()
            original_source = decompile_file_text(mustang_text)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Decompile failed:\n{exc}")
            self.set_status("Decompile failed.", CLOSE_HOVER)
            return

        default_name = os.path.splitext(os.path.basename(src_path))[0] + ".py"
        out_path = filedialog.asksaveasfilename(
            title="Save decompiled Python file as",
            initialfile=default_name,
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        )
        if not out_path:
            return

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(original_source)
        self.set_status(f"Decompiled {os.path.basename(out_path)}", ACCENT)
        messagebox.showinfo(APP_TITLE, f"Decompiled successfully:\n{out_path}")


def main():
    app = MustangApp()
    app.mainloop()


if __name__ == "__main__":
    main()
