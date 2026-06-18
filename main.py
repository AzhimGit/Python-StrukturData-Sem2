from datetime import datetime

class MinHeap:
    """Implementasi Min-Heap dari nol tanpa library"""
    def __init__(self):
        self.heap = []  # Menyimpan tuple: (stok, id1, id2, nama)

    def insert(self, item):
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def _sift_up(self, index):
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._sift_up(parent)

    def update_item(self, id1, id2, new_stock):
        """Update stok item tertentu dan sesuaikan posisi di heap"""
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
        """Menampilkan isi heap secara terurut tanpa merusak heap asli"""
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


class SistemPeternakan:
    def __init__(self):
        # Data Master Dinamis
        self.feed_names = {1: "Pakan Layer", 2: "Pakan Grower", 3: "Pakan Starter"}
        self.next_feed_id = 4  
        self.cage_names = {1: "Kandang 1", 2: "Kandang 2", 3: "Kandang 3"}

        # Stok Awal
        self.gudang_stock = {1: 200, 2: 150, 3: 100}
        self.kandang_stock = {
            1: {1: 40, 2: 20, 3: 10},
            2: {1: 30, 2: 50, 3: 5},
            3: {1: 10, 2: 15, 3: 25}
        }

        # Inisialisasi Heap & Riwayat
        self.heap_all = MinHeap()
        self.heap_cages = {1: MinHeap(), 2: MinHeap(), 3: MinHeap()}
        self.heap_gudang = MinHeap()
        self.history = []  # List untuk menyimpan log transaksi

        self._init_heaps()

    def _log_transaction(self, activity, detail):
        """Mencatat Supply dengan timestamp"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.history.append({
            "time": timestamp,
            "activity": activity,
            "detail": detail
        })

    def _init_heaps(self):
        for pid, stock in self.gudang_stock.items():
            self.heap_gudang.insert((stock, pid, 0, self.feed_names[pid]))

        for cid in range(1, 4):
            for pid in self.kandang_stock[cid].keys():
                stock = self.kandang_stock[cid][pid]
                item = (stock, cid, pid, f"{self.cage_names[cid]} - {self.feed_names[pid]}")
                self.heap_all.insert(item)
                self.heap_cages[cid].insert(item)

    def get_pakan_prompt(self):
        return ", ".join([f"{pid}:{nama}" for pid, nama in self.feed_names.items()])

    def _update_stocks(self, cid, pid, amount):
        if pid not in self.feed_names:
            print(" ID Pakan tidak valid!")
            return False
        if self.gudang_stock[pid] < amount:
            print(f"Gagal! Stok gudang {self.feed_names[pid]} tidak cukup (Sisa: {self.gudang_stock[pid]}kg).")
            return False

        self.gudang_stock[pid] -= amount
        self.kandang_stock[cid][pid] += amount

        self.heap_cages[cid].update_item(cid, pid, self.kandang_stock[cid][pid])
        self.heap_all.update_item(cid, pid, self.kandang_stock[cid][pid])
        self.heap_gudang.update_item(pid, 0, self.gudang_stock[pid])
        
        # Catat ke Riwayat
        self._log_transaction(
            "SUPPLY KE KANDANG", 
            f"Menyuplai {amount}kg {self.feed_names[pid]} dari Gudang ke {self.cage_names[cid]}"
        )
        
        print(f"Berhasil! {amount}kg {self.feed_names[pid]} disuplai ke {self.cage_names[cid]}.")
        return True

    def menu_cek_semua_kandang(self):
        print("\n" + "="*50)
        print(" STOK PAKAN SEMUA KANDANG (Prioritas Terendah)")
        print("="*50)
        sorted_items = self.heap_all.get_sorted_view()
        for i, (stock, cid, pid, name) in enumerate(sorted_items, 1):
            print(f"  {i}. {name} : {stock}kg")

        choice = input("\nApakah ingin melakukan supply dari gudang? (y/n): ").lower()
        if choice == 'y':
            try:
                cid = int(input("Pilih ID Kandang (1-3): "))
                pid = int(input(f"Pilih ID Pakan ({self.get_pakan_prompt()}): "))
                amount = int(input("Masukkan jumlah supply (kg): "))
                if 1 <= cid <= 3 and pid in self.feed_names and amount > 0:
                    self._update_stocks(cid, pid, amount)
                else:
                    print("❌ Input tidak valid!")
            except ValueError:
                print("❌ Input harus berupa angka!")

    def menu_cek_per_kandang(self):
        print("\n" + "="*50)
        print("CEK STOK PER KANDANG")
        print("="*50)
        try:
            cid = int(input("Pilih Kandang (1-3): "))
            if cid not in [1, 2, 3]:
                print("Kandang tidak ditemukan!")
                return

            print(f"\nStok {self.cage_names[cid]} (Prioritas Terendah):")
            sorted_items = self.heap_cages[cid].get_sorted_view()
            for i, (stock, _, pid, name) in enumerate(sorted_items, 1):
                print(f"  {i}. {name} : {stock}kg")

            choice = input("\nApakah ingin melakukan supply dari gudang? (y/n): ").lower()
            if choice == 'y':
                pid = int(input(f"Pilih ID Pakan ({self.get_pakan_prompt()}): "))
                amount = int(input("Masukkan jumlah supply (kg): "))
                if pid in self.feed_names and amount > 0:
                    self._update_stocks(cid, pid, amount)
                else:
                    print("Input tidak valid!")
        except ValueError:
            print("Input harus berupa angka!")

    def menu_cek_gudang(self):
        print("\n" + "="*50)
        print(" STOK GUDANG (Prioritas Terendah)")
        print("="*50)
        sorted_items = self.heap_gudang.get_sorted_view()
        for i, (stock, pid, _, name) in enumerate(sorted_items, 1):
            print(f"  {i}. {name} : {stock}kg")

        choice = input("\nApakah ingin melakukan restock gudang dari supplier? (y/n): ").lower()
        if choice == 'y':
            try:
                pid = int(input(f"Pilih ID Pakan ({self.get_pakan_prompt()}): "))
                amount = int(input("Masukkan jumlah restock (kg): "))
                if pid in self.feed_names and amount > 0:
                    self.gudang_stock[pid] += amount
                    self.heap_gudang.update_item(pid, 0, self.gudang_stock[pid])
                    
                    # Catat ke Riwayat
                    self._log_transaction(
                        "RESTOCK GUDANG", 
                        f"Menambah {amount}kg {self.feed_names[pid]} ke Gudang dari Supplier"
                    )
                    
                    print(f"✅ Berhasil! Gudang {self.feed_names[pid]} bertambah {amount}kg.")
                else:
                    print("❌ Input tidak valid!")
            except ValueError:
                print("❌ Input harus berupa angka!")

    def menu_tambah_pakan(self):
        print("\n" + "="*50)
        print("TAMBAH PAKAN BARU")
        print("="*50)
        
        nama_pakan = input("Masukkan nama pakan baru: ").strip()
        if not nama_pakan:
            print("Nama pakan tidak boleh kosong!")
            return

        new_id = self.next_feed_id
        self.feed_names[new_id] = nama_pakan
        self.next_feed_id += 1

        try:
            stok_gudang = int(input(f"Masukkan stok awal gudang untuk {nama_pakan} (kg): "))
            if stok_gudang < 0:
                print("❌ Stok tidak boleh negatif!")
                return
                
            self.gudang_stock[new_id] = stok_gudang
            self.heap_gudang.insert((stok_gudang, new_id, 0, nama_pakan))

            for cid in range(1, 4):
                stok_kandang = int(input(f"Masukkan stok awal {nama_pakan} untuk {self.cage_names[cid]} (kg): "))
                if stok_kandang < 0:
                    print("❌ Stok tidak boleh negatif!")
                    return
                    
                self.kandang_stock[cid][new_id] = stok_kandang
                item = (stok_kandang, cid, new_id, f"{self.cage_names[cid]} - {nama_pakan}")
                self.heap_all.insert(item)
                self.heap_cages[cid].insert(item)

            self._log_transaction("TAMBAH PAKAN BARU", f"Menambahkan pakan baru '{nama_pakan}' (ID: {new_id}) ke sistem")
            print(f"\nPakan '{nama_pakan}' (ID: {new_id}) berhasil ditambahkan ke sistem!")
        except ValueError:
            print("Input stok harus berupa angka!")

    def menu_riwayat(self):
        print("\n" + "="*50)
        print("RIWAYAT SUPPLY")
        print("="*50)
        if not self.history:
            print("Belum ada Supply yang tercatat.")
            return
        
        # Tampilkan dari yang terbaru (reverse)
        for i, log in enumerate(reversed(self.history), 1):
            print(f"  {i}. [{log['time']}]")
            print(f"     Aktivitas : {log['activity']}")
            print(f"     Detail    : {log['detail']}")
            print("-" * 40)

    def run(self):
        while True:
            print("\n" + "="*50)
            print("SISTEM MANAJEMEN PAKAN PETERNAKAN")
            print("="*50)
            print("1. Cek stok pakan (Semua Kandang)")
            print("2. Cek stok pakan per kandang")
            print("3. Cek stok gudang")
            print("4. Tambah pakan baru")
            print("5. Lihat riwayat Supply")
            print("6. Keluar")
            
            choice = input("Pilih menu (1-6): ")
            
            if choice == '1':
                self.menu_cek_semua_kandang()
            elif choice == '2':
                self.menu_cek_per_kandang()
            elif choice == '3':
                self.menu_cek_gudang()
            elif choice == '4':
                self.menu_tambah_pakan()
            elif choice == '5':
                self.menu_riwayat()
            elif choice == '6':
                print("Terima kasih, sistem ditutup.")
                break
            else:
                print("Pilihan tidak valid, silakan coba lagi.")

# Jalankan program
if __name__ == "__main__":
    app = SistemPeternakan()
    app.run()