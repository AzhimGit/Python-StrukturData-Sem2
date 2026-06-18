# 🐔 Sistem Manajemen Pakan Peternakan (Heap & PostgreSQL)

Sistem manajemen stok pakan untuk peternakan ayam petelur yang menggunakan struktur data **Min-Heap** untuk mengurutkan prioritas stok terendah secara otomatis. Sistem ini juga terintegrasi dengan **PostgreSQL** untuk penyimpanan data.

## ✨ Fitur Utama
- 📊 **Cek Stok Semua Kandang**: Menampilkan prioritas kandang yang stok pakannya paling rendah.
- 🏠 **Cek Stok Per Kandang**: Melihat detail stok per kandang dengan prioritas terendah.
- 🏭 **Cek Stok Gudang**: Memantau stok gudang untuk kebutuhan restock.
- 🔄 **Supply & Restock**: Melakukan transfer pakan dari gudang ke kandang, atau restock gudang dari supplier.
- 📜 **Riwayat Transaksi**: Mencatat semua aktivitas supply dengan timestamp otomatis.

## 🛠️ Tools yang Digunakan
- **Python 3.x** - Bahasa pemrograman utama
- **PostgreSQL** - Sistem manajemen database
- **psycopg2** - Library adapter PostgreSQL untuk Python
- **Min-Heap (Custom)** - Struktur data utama diimplementasikan dari nol tanpa library `heapq`

## 📋 Prasyarat
Pastikan sudah menginstall:
1. [Python 3.x](https://www.python.org/downloads/)
2. [PostgreSQL](https://www.postgresql.org/download/)

## 🚀 Cara Instalasi & Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/AzhimGit/Python-StrukturData-Sem2.git
cd Python-StrukturData-Sem2
```
### 2. Install Dependencies
```bash
# Buat virtual environment
python -m venv .venv

# (Windows)
.venv\Scripts\activate
# (Mac/Linux)
source .venv/bin/activate

# Install library psycopg2 (database)
pip install psycopg2-binary
```
### 3. Setup Database PostgreSQL
- Buat database baru di PostgreSQL (nama bebas).
- Jalankan query SQL [berikut](https://justpaste.it/et0vt/pdf) untuk membuat tabel-tabel yang diperlukan.
- Jalankan query SQL [berikut](https://justpaste.it/e9kg8/pdf) untuk membuat data dummy.
### 4. Konfigurasi Koneksi Database
Buka main.py dan sesuaikan dengan Database di laptopmu
```bash
self.db = DatabaseManager("nama_db_kamu", "postgres", "password_kamu", "localhost", "5432")
```
### 5. Jalankan Program
```bash
python main.py
```
