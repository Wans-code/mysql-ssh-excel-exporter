# MySQL SSH Excel Exporter

**MySQL SSH Excel Exporter** adalah tool berbasis Python yang dirancang untuk mengekstrak data dari database MySQL yang berada di balik firewall/jaringan tertutup. Tool ini menggunakan SSH Tunneling untuk terhubung dengan aman, mengeksekusi query kustom, dan mengekspor hasilnya langsung menjadi file Excel (`.xlsx`). 

Tool ini dioptimalkan untuk memproses data berukuran besar secara *memory-efficient* menggunakan metode *chunking* (membaca dan menulis data per-bagian).

## Fitur Utama

- **SSH Tunneling**: Terhubung secara aman ke database MySQL remote (seperti server produksi) melalui SSH.
- **Multi-Koneksi**: Mendukung banyak profil koneksi sekaligus. Anda dapat menyimpan konfigurasi untuk berbagai server dalam satu file JSON dan memilihnya saat runtime.
- **Memory Efficient**: Menggunakan `SSCursor` (Server-Side Cursor) dari `pymysql` dan mode *write-only* dari `openpyxl` untuk mencegah kehabisan memori (Out Of Memory/RAM) saat mengekspor jutaan baris data.
- **Kustom SQL**: Query dipisahkan dalam file `query.sql`, memudahkan Anda untuk menulis query kompleks (JOIN, subquery, dsb) tanpa harus mengubah kode program.
- **Auto-naming & Progress Tracking**: File hasil export dinamakan secara otomatis berdasarkan nama koneksi dan waktu proses. Progress export juga ditampilkan di terminal.

## Prasyarat

- Python 3.7 atau versi lebih baru.

## Instalasi

1. **Clone/Download Repository ini**
   ```bash
   git clone https://github.com/username_anda/nama_repository_anda.git
   cd nama_repository_anda
   ```

2. **(Opsional) Buat Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/Mac
   # venv\Scripts\activate   # Untuk Windows
   ```

3. **Install Dependencies**
   Install library yang dibutuhkan menggunakan `pip`:
   ```bash
   pip install -r requirements.txt
   ```

## Konfigurasi

1. Duplikat atau *rename* file `connections.json.example` menjadi `connections.json`:
   ```bash
   cp connections.json.example connections.json
   ```
2. Buka `connections.json` dan isi kredensial SSH serta Database Anda. Anda bisa menambahkan banyak profil dengan membuat *key* JSON baru (misal: `"server_produksi"`, `"server_staging"`).

**PENTING: Jangan pernah membagikan atau mengupload file `connections.json` ke public repository (GitHub, dsb). File ini sudah dimasukkan ke `.gitignore` secara default.**

## Cara Penggunaan

1. Buka file `query.sql` menggunakan text editor.
2. Tulis atau paste query MySQL yang ingin Anda eksekusi.
3. Jalankan program utamanya:
   ```bash
   python main.py
   ```
4. Program akan menampilkan daftar koneksi yang tersedia di `connections.json`. Ketik nama koneksi yang ingin digunakan lalu tekan Enter.
5. Tunggu proses selesai. Hasil export akan tersimpan di folder yang sama dengan format nama `export_[nama_koneksi]_[timestamp].xlsx`.

## Troubleshooting

- **`Authentication failed`**: Pastikan username/password SSH benar. Jika menggunakan key, pastikan path di `SSH_KEY_PATH` tepat.
- **`Lost connection to MySQL server`**: Cek apakah port MySQL di server tujuan benar (biasanya 3306), dan user MySQL memiliki akses localhost/127.0.0.1 dari sisi server tujuan.
