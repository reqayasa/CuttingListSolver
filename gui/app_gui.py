import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from core import csv_repository
from core.optimizer_service import OptimizerService
from gui.style_manager import StyleManager

class CuttingListApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cutting List Solver")
        StyleManager(self.root)
        # self.root.geometry("800x600")
        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.required_parts = None
        self.scale = 1
        self.stocks = None
        self.result = None

        self.optimizer = OptimizerService()

        self.btn_frame = ttk.Frame(self.mainframe)
        self.btn_frame.grid(row=0, column=0, pady=10)

        ttk.Button(self.btn_frame, text="Import Required Parts",
                   command=self.import_required_parts
                   ).grid(row=0, column=0)
        ttk.Button(self.btn_frame, text="Import Stocks",
                   command=self.import_stocks
                   ).grid(row=0, column=1)
        ttk.Button(self.btn_frame, text="Optimize",
                   command=self.optimize
                   ).grid(row=0, column=2)
        ttk.Button(self.btn_frame, text="Export Result",
                   command=self.export_csv
                   ).grid(row=0, column=3)
        
        self.data_frame = ttk.Frame(self.mainframe)
        self.data_frame.grid(row=1, column=0)

        # DATA FRAME
        ttk.Label(self.data_frame, text="Required Parts:").grid(row=0, column=0)
        self.columns_part = ("_i", "Type", "Length", "Quantity")
        self.tree_required_parts = ttk.Treeview(self.data_frame, columns=self.columns_part, show="headings")
        self.tree_required_parts.grid(row=1, column=0, padx=8, pady=4)
        for col in self.columns_part:
            self.tree_required_parts.heading(col, text=col.capitalize())
            self.tree_required_parts.column(col, width=100, anchor="center")

        ttk.Label(self.data_frame, text="Stocks:").grid(row=0, column=1)
        self.columns_stock = ("_k", "Length", "Quantity")
        self.tree_stocks = ttk.Treeview(self.data_frame, columns=self.columns_stock, show="headings")
        self.tree_stocks.grid(row=1, column=1, padx=8, pady=4)
        for col in self.columns_stock:
            self.tree_stocks.heading(col, text=col.capitalize())
            self.tree_stocks.column(col, width=100, anchor="center")

        ttk.Label(self.data_frame, text="Result:").grid(row=0, column=2)
        self.listbox = tk.Listbox(self.data_frame, width=80, height=30)
        self.listbox.grid(row=1, column=2, padx=8, pady=4)

    
    def import_required_parts(self):  
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.required_parts, self.scale = csv_repository.load_required_parts_aggreageted(filename)
            messagebox.showinfo("Info", f"{len(self.required_parts)} required part loaded")
        if self.required_parts:
            for i in self.tree_required_parts.get_children():
                self.tree_required_parts.delete(i)
            for i, part in enumerate(self.required_parts):
                self.tree_required_parts.insert("", tk.END, values=(i, part.part_type, part.length, part.quantity))
        

    def import_stocks(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.stocks = csv_repository.load_stocks_aggregated(filename, 1)
            messagebox.showinfo("Info", f"{len(self.stocks)} stocks loaded")
        if self.stocks:
            for k in self.tree_stocks.get_children():
                self.tree_stocks.delete(k)
            for k, stock in enumerate(self.stocks):
                self.tree_stocks.insert("", tk.END, values=(k, stock.length, stock.quantity))

    def optimize(self):
        if not self.required_parts or not self.stocks:
            messagebox.showerror("Error", "Import Required Parts dan stocks dulu")
            return
        self.result = self.optimizer.run(self.required_parts, self.stocks)
        self.show_result()
    
    def export_csv(self):
        if not self.result:
            messagebox.showerror("Error", "Belum ada hasil optimasi")
            return
        filename = filedialog.asksaveasfilename(defaultextension="csv")
        if filename:
            csv_repository.save_result([b["pieces"] for b in self.result], filename, self.scale)

    def show_result(self):
        self.listbox.delete(0, tk.END)
        for i, b in enumerate(self.result):
            # used = sum(p.length for p in b["pieces"])
            self.listbox.insert(tk.END, f"stock length: {b["stock_length"]} | pattern: {b["pattern"]} | waste: {b["waste"]}")

    def run(self):
        self.root.mainloop()