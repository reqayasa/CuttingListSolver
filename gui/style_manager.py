from tkinter import ttk

class StyleManager:
    def __init__(self, root):
        self.style = ttk.Style(root)
        # self.style.theme_use("clam")
        self.style.configure(
            "TFrame", 
            # background="#dd2828", 
            borderwidth=5, 
            relief="flat",
            padding=(8, 8, 8, 8),
            padx=8, pady=8
            )
        self.style.configure(
            "TButton", 
            # background="#b328dd", 
            # borderwidth=5, 
            # relief="flat",
            padding=(12, 4, 12, 4),
            padx=8, pady=4
            )
        self.style.configure(
            "TLabel",
            padding=(4, 4, 4, 4),
            padx=4, pady=4
            )
        # self.style.configure(
        #     "Treeview.Heading", font=("Segoe UI", 10, "normal")
        # )