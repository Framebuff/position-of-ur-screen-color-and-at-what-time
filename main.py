from __future__ import annotations

import sys
import os
from datetime import datetime

import customtkinter as ctk
import keyboard
import pyautogui
from PIL import ImageGrab

if sys.platform == "win32":
    try:
        import ctypes

        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("core.picker.app.1.0")
    except Exception:
        pass


def resource_path(filename):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def sample_pixel():
    x, y = pyautogui.position()
    img = ImageGrab.grab()
    r, g, b = img.getpixel((x, y))[:3]
    return x, y, (r, g, b), f"#{r:02x}{g:02x}{b:02x}"


def get_contrast_text(hex_value):
    hex_value = hex_value.lstrip("#")
    r, g, b = int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 150 else "#ffffff"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("colorpicker")
        self.geometry("380x650")
        self.resizable(False, False)
        self.configure(fg_color="#000000")

        try:
            self.iconbitmap(resource_path("9jycn8.ico"))
        except Exception:
            pass

        self.hotkey_var = ctk.StringVar(value="f8")
        self.hotkey_handle = None
        self.records = []
        self.row_elements = []

        self.build_layout()
        self.bind_hotkey()

    def build_layout(self):
        ctk.CTkLabel(
            self,
            text="colorpicker",
            font=("consolas", 18, "bold"),
            text_color="#ffffff"
        ).pack(pady=(16, 2))

        self.status_label = ctk.CTkLabel(
            self,
            text="press f8 to sample screen",
            text_color="#666666",
            font=("consolas", 12)
        )
        self.status_label.pack(pady=(0, 12))

        hotkey_card = ctk.CTkFrame(
            self,
            fg_color="#080808",
            corner_radius=6,
            border_width=1,
            border_color="#1f1f1f"
        )
        hotkey_card.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(
            hotkey_card,
            text="hotkey",
            font=("consolas", 12),
            text_color="#888888"
        ).pack(side="left", padx=12, pady=8)

        self.hotkey_entry = ctk.CTkEntry(
            hotkey_card,
            width=70,
            height=28,
            textvariable=self.hotkey_var,
            justify="center",
            fg_color="#000000",
            border_width=1,
            border_color="#222222",
            text_color="#ffffff",
            font=("consolas", 11)
        )
        self.hotkey_entry.pack(side="left", padx=4, pady=8)

        ctk.CTkButton(
            hotkey_card,
            text="rebind",
            width=65,
            height=28,
            fg_color="#111111",
            hover_color="#1f1f1f",
            text_color="#dddddd",
            font=("consolas", 11),
            corner_radius=6,
            command=self.bind_hotkey
        ).pack(side="right", padx=12, pady=8)

        info_card = ctk.CTkFrame(
            self,
            fg_color="#080808",
            corner_radius=6,
            border_width=1,
            border_color="#1f1f1f"
        )
        info_card.pack(fill="x", padx=16, pady=10)

        self.swatch = ctk.CTkFrame(
            info_card,
            width=48,
            height=48,
            fg_color="#111111",
            corner_radius=6,
            border_width=1,
            border_color="#222222"
        )
        self.swatch.pack(side="left", padx=12, pady=12)
        self.swatch.pack_propagate(False)

        info_column = ctk.CTkFrame(info_card, fg_color="transparent")
        info_column.pack(side="left", padx=8, pady=12, fill="both", expand=True)

        entry_options = dict(
            height=24,
            fg_color="#000000",
            border_width=0,
            text_color="#cccccc",
            font=("consolas", 11)
        )

        self.pos_field = ctk.CTkEntry(info_column, **entry_options)
        self.pos_field.pack(fill="x", pady=2)

        self.hex_field = ctk.CTkEntry(info_column, **entry_options)
        self.hex_field.pack(fill="x", pady=2)

        self.rgb_field = ctk.CTkEntry(info_column, **entry_options)
        self.rgb_field.pack(fill="x", pady=2)

        def block_edit(event):
            allowed = {"Left", "Right", "Home", "End", "Shift_L", "Shift_R", "Control_L", "Control_R"}
            if event.keysym in allowed or (event.state & 0x4):
                return None
            return "break"

        for field in (self.pos_field, self.hex_field, self.rgb_field):
            field.bind("<Key>", block_edit)

        button_row = ctk.CTkFrame(self, fg_color="transparent")
        button_row.pack(fill="x", padx=16, pady=4)
        button_row.grid_columnconfigure((0, 1, 2), weight=1)

        button_options = dict(
            height=32,
            fg_color="#080808",
            hover_color="#121212",
            text_color="#dddddd",
            border_width=1,
            border_color="#1f1f1f",
            corner_radius=6,
            font=("consolas", 11)
        )
        ctk.CTkButton(button_row, text="copy hex", command=self.copy_hex, **button_options).grid(row=0, column=0,
                                                                                                 sticky="ew", padx=2)
        ctk.CTkButton(button_row, text="copy pos", command=self.copy_pos, **button_options).grid(row=0, column=1,
                                                                                                 sticky="ew", padx=2)
        ctk.CTkButton(button_row, text="copy rgb", command=self.copy_rgb, **button_options).grid(row=0, column=2,
                                                                                                 sticky="ew", padx=2)

        history_header = ctk.CTkFrame(self, fg_color="transparent")
        history_header.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            history_header,
            text="history",
            font=("consolas", 12, "bold"),
            text_color="#666666"
        ).pack(side="left")

        ctk.CTkButton(
            history_header,
            text="clear",
            width=50,
            height=22,
            fg_color="#080808",
            hover_color="#121212",
            text_color="#888888",
            border_width=1,
            border_color="#1f1f1f",
            font=("consolas", 10),
            corner_radius=4,
            command=self.clear_history
        ).pack(side="right")

        self.history_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#080808",
            border_width=1,
            border_color="#1f1f1f",
            corner_radius=6,
            scrollbar_button_color="#222222"
        )
        self.history_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def bind_hotkey(self):
        if self.hotkey_handle:
            try:
                keyboard.remove_hotkey(self.hotkey_handle)
            except Exception:
                pass
        key = self.hotkey_var.get().strip().lower() or "f8"
        self.hotkey_handle = keyboard.add_hotkey(key, self.trigger_sample)
        self.status_label.configure(text=f"press {key} anywhere to sample")

    def trigger_sample(self):
        try:
            x, y, rgb, hex_val = sample_pixel()
        except Exception as err:
            self.after(0, lambda: self.log_status(f"error: {err}"))
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        record = {"time": timestamp, "x": x, "y": y, "rgb": rgb, "hex": hex_val}
        self.records.append(record)
        self.after(0, lambda: self.handle_new_record(record))

    def handle_new_record(self, record):
        self.update_preview(record)
        self.add_history_row(record)

    def update_preview(self, record):
        self.swatch.configure(fg_color=record["hex"])
        self.set_field(self.pos_field, f"pos: ({record['x']}, {record['y']})")
        self.set_field(self.hex_field, f"hex: {record['hex']}")
        self.set_field(self.rgb_field, f"rgb: {record['rgb']}")

    def set_field(self, field, text):
        field.delete(0, "end")
        field.insert(0, text)

    def add_history_row(self, record):
        row = ctk.CTkButton(
            self.history_scroll,
            text=f"  {record['hex']}    ({record['x']}, {record['y']})    {record['time']}",
            anchor="w",
            height=30,
            fg_color=record["hex"],
            hover_color=record["hex"],
            text_color=get_contrast_text(record["hex"]),
            font=("consolas", 11),
            border_width=1,
            border_color="#1f1f1f",
            corner_radius=4,
            command=lambda r=record: self.select_row(r)
        )
        row.pack(fill="x", padx=4, pady=2)
        self.row_elements.insert(0, row)
        for element in self.row_elements:
            element.pack_forget()
        for element in self.row_elements:
            element.pack(fill="x", padx=4, pady=2)

    def select_row(self, record):
        self.update_preview(record)
        self.status_label.configure(text=f"viewing {record['hex']} from {record['time']}")

    def clear_history(self):
        for row in self.row_elements:
            row.destroy()
        self.row_elements = []

    def log_status(self, message):
        self.status_label.configure(text=message)

    def copy_hex(self):
        if self.records:
            self.clipboard_clear()
            self.clipboard_append(self.records[-1]["hex"])

    def copy_pos(self):
        if self.records:
            last = self.records[-1]
            self.clipboard_clear()
            self.clipboard_append(f"{last['x']}, {last['y']}")

    def copy_rgb(self):
        if self.records:
            last = self.records[-1]
            self.clipboard_clear()
            self.clipboard_append(str(last["rgb"]))
            self.status_label.configure(text=f"copied rgb {last['rgb']}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
