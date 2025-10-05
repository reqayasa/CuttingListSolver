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

        self.items = None
        self.scale = 1
        self.stocks = None
        self.result = None

        self.optimizer = OptimizerService()

        self.btn_frame = ttk.Frame(self.mainframe)
        self.btn_frame.grid(row=0, column=0, pady=10)

        ttk.Button(self.btn_frame, text="Import Items",
                   command=self.import_items
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
        ttk.Label(self.data_frame, text="Items:").grid(row=0, column=0)

        self.columns_item = ("Type", "Length")
        self.tree_items = ttk.Treeview(self.data_frame, columns=self.columns_item, show="headings")
        self.tree_items.grid(row=1, column=0, padx=8, pady=4)
        for col in self.columns_item:
            self.tree_items.heading(col, text=col.capitalize())
            self.tree_items.column(col, width=100, anchor="center")

        ttk.Label(self.data_frame, text="Stocks:").grid(row=0, column=1)
        self.columns_stock = ("Length", "Usable Length", "Quantity", "Unit Price")
        self.tree_stocks = ttk.Treeview(self.data_frame, columns=self.columns_stock, show="headings")
        self.tree_stocks.grid(row=1, column=1, padx=8, pady=4)
        for col in self.columns_stock:
            self.tree_stocks.heading(col, text=col.capitalize())
            self.tree_stocks.column(col, width=100, anchor="center")

        ttk.Label(self.data_frame, text="Result:").grid(row=0, column=2)
        self.listbox = tk.Listbox(self.data_frame, width=50, height=10)
        self.listbox.grid(row=1, column=2, padx=8, pady=4)

    
    def import_items(self):  
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.items, self.scale = csv_repository.load_items(filename)
            messagebox.showinfo("Info", f"{len(self.items)} items loaded")
        if self.items:
            for i in self.tree_items.get_children():
                self.tree_items.delete(i)
            for item in self.items:
                self.tree_items.insert("", tk.END, values=(item.type, item.length))
        

    def import_stocks(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.stocks = csv_repository.load_stocks(filename, 1)
            messagebox.showinfo("Info", f"{len(self.stocks)} stocks loaded")
        if self.stocks:
            for i in self.tree_stocks.get_children():
                self.tree_stocks.delete(i)
            for stock in self.stocks:
                self.tree_stocks.insert("", tk.END, values=(stock.length, stock.usable_length, stock.quantity, stock.unit_price))

    def optimize(self):
        if not self.items or not self.stocks:
            messagebox.showerror("Error", "Import items dan stocks dulu")
            return
        self.result = self.optimizer.run(self.items, self.stocks)
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
            used = sum(p.length for p in b["pieces"])
            self.listbox.insert(tk.END, f"stocks {i+1}: used={used}/{b['usable_length']} | pieces={[p.type for p in b['pieces']]}")

    def run(self):
        self.root.mainloop()