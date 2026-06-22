import psycopg2 
from datetime import datetime 


class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, item):
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def _sift_up(self, index):
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._sift_up(parent)

    def update_item(self, id1, id2, new_stock):
        for i in range(len(self.heap)):
            if self.heap[i][1] == id1 and self.heap[i][2] == id2:
                old_stock = self.heap[i][0]
                self.heap[i] = (new_stock, id1, id2, self.heap[i][3])
                if new_stock < old_stock:
                    self._sift_up(i)
                else:
                    self._sift_down(i)
                break

    def _sift_down(self, index):
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        size = len(self.heap)
        if left < size and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < size and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._sift_down(smallest)

    def get_sorted_view(self):
        extracted = []
        original_heap = self.heap[:]
        while self.heap:
            min_item = self.heap[0]
            extracted.append(min_item)
            self.heap[0] = self.heap[-1]
            self.heap.pop()
            if self.heap:
                self._sift_down(0)
        self.heap = original_heap
        return extracted


class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
            self.cursor = self.conn.cursor()
            print("Koneksi PostgreSQL berhasil")
        except Exception as e:
            print(f"Gagal: {e}")
            self.conn = None

    def ambilsemuadata(self):
        data = {"gudang": {}, "kandang": {1: {}, 2: {}, 3: {}}, "pakan": {}}

        self.cursor.execute("SELECT id_pakan, nama_pakan FROM pakan")
        for row in self.cursor.fetchall():
            data["pakan"][row[0]] = row[1]

        self.cursor.execute("SELECT pakan_id_pakan, jumlah_stok_gudang FROM stok_gudang WHERE gudang_id_gudang = 1")
        for row in self.cursor.fetchall():
            data["gudang"][row[0]] = row[1]

        self.cursor.execute("SELECT kandang_id_kandang, pakan_id_pakan, jumlah_stok_kandang FROM stok_kandang")
        for row in self.cursor.fetchall():
            cid, pid, stock = row
            if cid in data["kandang"]:
                data["kandang"][cid][pid] = stock

        return data

    def simpandatasupply(self, cid, pid, jumlah, stok_gudang, stok_kandang):
        try:
            today = datetime.now().date()
            self.cursor.execute("UPDATE stok_gudang SET jumlah_stok_gudang = %s WHERE gudang_id_gudang = 1 AND pakan_id_pakan = %s", (stok_gudang, pid))
            self.cursor.execute("UPDATE stok_kandang SET jumlah_stok_kandang = %s WHERE kandang_id_kandang = %s AND pakan_id_pakan = %s", (stok_kandang, cid, pid))
            self.cursor.execute("INSERT INTO supply_kandang (tanggal_supply_kandang, kuantitas, pakan_id_pakan, kandang_id_kandang) VALUES (%s, %s, %s, %s)", (today, jumlah, pid, cid))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error: {e}")
            return False

    def simpanrestokgudang(self, pid, jumlah, new_stok_gudang):
        try:
            today = datetime.now().date()
            self.cursor.execute("UPDATE stok_gudang SET jumlah_stok_gudang = %s WHERE gudang_id_gudang = 1 AND pakan_id_pakan = %s", (new_stok_gudang, pid))
            self.cursor.execute("INSERT INTO supply_gudang (tanggal_supply_gudang, kuantitas, pakan_id_pakan, gudang_id_gudang) VALUES (%s, %s, %s, 1)", (today, jumlah, pid))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error: {e}")
            return False


class SistemPeternakan:
    def __init__(self):
        self.db = DatabaseManager("petelur", "postgres", "root", "localhost", "5432")

        if not self.db.conn:
            print("Tidak ada database.")
            return

        db_data = self.db.ambilsemuadata()
        self.nama_pakan = db_data["pakan"]
        self.nama_kandang = {1: "Kandang 1", 2: "Kandang 2", 3: "Kandang 3"}

        self.stok_gudang = db_data["gudang"]
        self.stok_kandang = db_data["kandang"]

        self.heap_semua = MinHeap()
        self.heap_kandang = {1: MinHeap(), 2: MinHeap(), 3: MinHeap()}
        self.heap_gudang = MinHeap()
        self._init_heaps()

    def _init_heaps(self):
        for pid, stock in self.stok_gudang.items():
            self.heap_gudang.insert((stock, pid, 0, self.nama_pakan[pid]))

        for cid in range(1, 4):
            for pid, stock in self.stok_kandang[cid].items():
                item = (stock, cid, pid, f"{self.nama_kandang[cid]} - {self.nama_pakan[pid]}")
                self.heap_semua.insert(item)
                self.heap_kandang[cid].insert(item)

    def get_pakan_prompt(self):
        return ", ".join([f"{pid}:{nama}" for pid, nama in self.nama_pakan.items()])

    def update_stok_simpan(self, cid, pid, jumlah):
        if self.stok_gudang.get(pid, 0) < jumlah:
            print(f"Stoknya ngga cukup.")
            return False

        new_gudang = self.stok_gudang[pid] - jumlah
        new_kandang = self.stok_kandang[cid].get(pid, 0) + jumlah

        success = self.db.simpandatasupply(cid, pid, jumlah, new_gudang, new_kandang)
        if not success:
            return False

        self.stok_gudang[pid] = new_gudang
        self.stok_kandang[cid][pid] = new_kandang

        self.heap_kandang[cid].update_item(cid, pid, new_kandang)
        self.heap_semua.update_item(cid, pid, new_kandang)
        self.heap_gudang.update_item(pid, 0, new_gudang)

        print(f"Mantap! {jumlah} karung disupply ke {self.nama_kandang[cid]}.")
        return True

    def run(self):
        while True:
            print("\n" + "=" * 50)
            print("SISTEM MANAJEMEN PAKAN PETELUR")
            print("=" * 50)
            print("1. Cek stok pakan")
            print("2. Cek stok pakan per kandang")
            print("3. Cek stok pakan di gudang")
            print("4. Lihat riwayat supply")
            print("5. Selesai")

            choice = input("Pilih menu 1-5: ")

            if choice == '1':
                self.menu_cek_semua_kandang()
            elif choice == '2':
                self.menu_cek_per_kandang()
            elif choice == '3':
                self.menu_cek_gudang()
            elif choice == '4':
                self.menu_riwayat()
            elif choice == '5':
                print("Berhenti.")
                break
            else:
                print("Pilihan tidak valid.")

    def menu_cek_semua_kandang(self):
        print("\nSTOK PAKAN SEMUA KANDANG")
        sorted_items = self.heap_semua.get_sorted_view()
        for i, (stock, cid, pid, name) in enumerate(sorted_items, 1):
            print(f"  {i}. {name} : {stock} karung")

        choice = input("\nApakah ingin melakukan supply dari gudang? (y/n): ").lower()
        if choice == 'y':
            try:
                cid = int(input("Pilih Kandang 1-3: "))
                pid = int(input(f"Pilih Pakan ({self.get_pakan_prompt()}): "))
                jumlah = int(input("Masukkan jumlah supply (karung): "))
                if 1 <= cid <= 3 and pid in self.nama_pakan and jumlah > 0:
                    self.update_stok_simpan(cid, pid, jumlah)
                else:
                    print("Input tidak valid.")
            except ValueError:
                print("Harus berupa angka")

    def menu_cek_per_kandang(self):
        print("\nCEK STOK PER KANDANG")
        try:
            cid = int(input("Pilih Kandang 1-3: "))
            if cid not in [1, 2, 3]:
                print("Kandang tidak valid")
                return

            print(f"\nStok {self.nama_kandang[cid]}:")
            sorted_items = self.heap_kandang[cid].get_sorted_view()
            for i, (stock, _, pid, name) in enumerate(sorted_items, 1):
                print(f"  {i}. {name} : {stock} karung")

            choice = input("\nApakah ingin melakukan supply dari gudang? (y/n): ").lower()
            if choice == 'y':
                pid = int(input(f"Pilih Pakan ({self.get_pakan_prompt()}): "))
                jumlah = int(input("Masukkan jumlah supply (karung): "))
                if pid in self.nama_pakan and jumlah > 0:
                    self.update_stok_simpan(cid, pid, jumlah)
                else:
                    print("Input tidak valid.")
        except ValueError:
            print("Harus berupa angka.")

    def menu_cek_gudang(self):
        print("\nSTOK GUDANG")
        sorted_items = self.heap_gudang.get_sorted_view()
        for i, (stock, pid, _, name) in enumerate(sorted_items, 1):
            print(f"  {i}. {name} : {stock} karung")

        choice = input("\nApakah ingin melakukan restock gudang? (y/n): ").lower()
        if choice == 'y':
            try:
                pid = int(input(f"Pilih Pakan ({self.get_pakan_prompt()}): "))
                jumlah = int(input("Masukkan jumlah restock (karung): "))
                if pid in self.nama_pakan and jumlah > 0:
                    new_gudang = self.stok_gudang.get(pid, 0) + jumlah
                    if self.db.simpanrestokgudang(pid, jumlah, new_gudang):
                        self.stok_gudang[pid] = new_gudang
                        self.heap_gudang.update_item(pid, 0, new_gudang)
                        print(f"Mantap! Gudang {self.nama_pakan[pid]} bertambah {jumlah} karung.")
                    else:
                        print("Gagal.")
                else:
                    print("Input tidak valid.")
            except ValueError:
                print("Input harus berupa angka.")

    def menu_riwayat(self):
        print("\nRIWAYAT SUPPLY")
        try:
            self.db.cursor.execute("""
                SELECT 'Supply Kandang' as tipe, tanggal_supply_kandang as tgl, kuantitas, pakan_id_pakan, kandang_id_kandang 
                FROM supply_kandang 
                UNION ALL 
                SELECT 'Restock Gudang' as tipe, tanggal_supply_gudang as tgl, kuantitas, pakan_id_pakan, gudang_id_gudang 
                FROM supply_gudang 
                ORDER BY tgl DESC
            """)
            rows = self.db.cursor.fetchall()
            if not rows:
                print("Tidak ada supply yang tercatat.")
                return

            for i, row in enumerate(rows, 1):
                tipe, tgl, kuantitas, pid, lokasi_id = row
                nama_pakan = self.nama_pakan.get(pid, "Unknown")
                lokasi = f"Kandang {lokasi_id}" if tipe == "Supply Kandang" else "Gudang"
                print(f"  {i}. [{tgl}] {tipe} - {kuantitas} karung {nama_pakan} ke {lokasi}")
                print("-" * 40)
        except Exception as e:
            print(f"Gagal mengambil riwayat: {e}")


if __name__ == "__main__":
    app = SistemPeternakan()
    if app.db.conn:
        app.run()