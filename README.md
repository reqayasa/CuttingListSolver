# Cutting List Solver (Python)
![Screen Shot](app_screenshot.png?raw=true "Cutting List Solver")

Program ini adalah aplikasi untuk menyelesaikan **Cutting Stock Problem** 1D dengan algoritma tertentu.  
Dibuat menggunakan **Python 3.x**.

## 🚀 Fitur
- Input data potongan dari file CSV.
- Optimasi penggunaan material stok.
- Output hasil cutting list dengan waste seminimal mungkin.
- GUI sederhana (Tkinter).

## 📦 Instalasi
1. Clone repository:
```bash
git clone https://github.com/reqayasateknik/CuttingListSolver.git
cd CuttingListSolver
```

2. Buat virtual environment:
```bash
python -m venv .venv
```

3. Aktifkan environment:
```bash
.venv/Scripts/Activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

▶️ Menjalankan Program
```bash
python main.py
```

▶️ Menjalankan Unit Test
```bash
python -m pytest tests/ -v
```

▶️ Updating
```bash
pip freeze > requirements.txt
git add .
git commit -m "message"
git push -u origin main
```