# Jawaban untuk Pertanyaan ADI Account Sequence

## Pertanyaan

> Kenapa adi_account_sequence, tidak bisa jalan?
> Saat saya memilih jurnal baru, saya tidak otomatis keluar error
> "The sequence regex should at least contain the seq grouping keys. For instance:
> ^(?P<prefix1>.*?)(?P<seq>\d*)(?P<suffix>\D*?)$"
>
> Coba tunjukkan skenario cara membuat journal baru dan transaksi customer invoice baru jika ingin menggunakan pola ini di front end

## Jawaban

### 1. Kenapa Error Tidak Muncul Otomatis?

Sebelumnya, validasi regex sequence hanya dilakukan saat posting invoice, **bukan** saat mengkonfigurasi journal. Ini menyebabkan user baru tahu ada masalah setelah mencoba posting invoice.

**Solusi yang sudah diterapkan**: Sekarang validasi dilakukan **segera** saat menyimpan journal. Jika regex tidak valid, error akan muncul langsung saat save journal.

### 2. Perubahan yang Sudah Dibuat

#### A. Validasi Journal (Baru!)

File: `addons/adi_account_sequence/models/account_journal.py`

Ditambahkan constraint `@api.constrains('sequence_override_regex')` yang akan:
- ✅ Validasi sintaks regex
- ✅ Memastikan ada capture group `(?P<seq>\d+)`
- ✅ Menampilkan error jika regex tidak valid

**Sekarang**: Saat save journal dengan regex yang salah, error langsung muncul!

#### B. Panduan Frontend Lengkap

File: `FRONTEND_GUIDE.md`

Panduan lengkap cara menggunakan modul ini di frontend Odoo, termasuk:
- Cara install modul
- Cara membuat journal baru
- Cara membuat customer invoice
- Contoh skenario lengkap
- Troubleshooting

### 3. Skenario Penggunaan di Frontend

#### Langkah 1: Buat Journal Baru

1. Buka **Accounting** → **Configuration** → **Journals**
2. Klik **Create**
3. Isi:
   - **Journal Name**: "Customer Invoice - Goods Type"
   - **Type**: "Sales"
   - **Short Code**: "ADSI"
4. Scroll ke **Sequence Override Regex**, masukkan:

```regex
^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$
```

5. Klik **Save**
   - ✅ Jika regex valid → Journal tersimpan
   - ❌ Jika regex invalid → Error muncul: "The sequence regex should at least contain the seq grouping keys"

#### Langkah 2: Buat Invoice Pertama (Set Pattern)

1. Buka **Accounting** → **Customers** → **Invoices**
2. Klik **Create**
3. Isi:
   - **Customer**: Pilih customer
   - **Invoice Date**: 15 Januari 2026
   - **Journal**: Pilih journal yang baru dibuat
   - **Goods Type**: "01" (field baru!)
4. Tambah invoice lines (produk, harga, dll)
5. **PENTING**: Sebelum posting, set Number secara manual:
   - Field **Number**: `AD-SI-L-2601-01-0001`
   - Ini akan jadi pattern untuk invoice selanjutnya
6. Klik **Confirm**

**Hasil**: Invoice pertama dengan nomor `AD-SI-L-2601-01-0001`

#### Langkah 3: Invoice Selanjutnya (Auto-Generate)

**Contoh 1: Bulan sama, goods_type sama**
1. Create invoice baru
2. Invoice Date: 20 Januari 2026
3. Goods Type: "01" (sama)
4. Isi invoice lines
5. Klik **Confirm**

**Hasil**: `AD-SI-L-2601-01-0002` (otomatis naik!)

**Contoh 2: Bulan sama, goods_type berbeda**
1. Create invoice baru
2. Invoice Date: 25 Januari 2026
3. Goods Type: "02" (berbeda!)
4. Isi invoice lines
5. Klik **Confirm**

**Hasil**: `AD-SI-L-2601-02-0001` (reset untuk goods_type baru!)

**Contoh 3: Bulan berbeda, goods_type sama**
1. Create invoice baru
2. Invoice Date: 10 Februari 2026 (bulan berbeda!)
3. Goods Type: "01"
4. Isi invoice lines
5. Klik **Confirm**

**Hasil**: `AD-SI-L-2602-01-0001` (reset untuk bulan baru!)

### 4. Tabel Contoh Lengkap

| Invoice | Tanggal | Goods Type | Nomor yang Dihasilkan |
|---------|---------|------------|----------------------|
| 1 | 2026-01-15 | 01 | AD-SI-L-2601-01-0001 |
| 2 | 2026-01-20 | 01 | AD-SI-L-2601-01-0002 |
| 3 | 2026-01-25 | 02 | AD-SI-L-2601-02-0001 |
| 4 | 2026-02-10 | 01 | AD-SI-L-2602-01-0001 |
| 5 | 2026-02-15 | 02 | AD-SI-L-2602-02-0001 |

### 5. Penjelasan Format

Format: `AD-SI-L-2601-01-0001`

- `AD-SI-L-` = Prefix tetap
- `2601` = Tahun-Bulan (YYMM format: 26=2026, 01=Januari)
- `01` = Goods Type (kode jenis barang)
- `0001` = Nomor urut (4 digit)

### 6. Aturan Reset Sequence

Sequence akan reset (mulai dari 0001) ketika:
1. **Bulan berubah**: 2601 → 2602 (Januari → Februari)
2. **Goods Type berubah**: 01 → 02

Setiap kombinasi tahun-bulan-goods_type punya counter sendiri!

### 7. File Dokumentasi

- **FRONTEND_GUIDE.md**: Panduan lengkap frontend (ENGLISH)
- **ANSWER.md**: Jawaban teknis original question (ENGLISH)
- **CUSTOM_SEQUENCE_FORMAT.md**: Dokumentasi teknis detail (ENGLISH)
- **README.md**: Overview modul (ENGLISH)
- **JAWABAN_INDONESIA.md**: File ini (BAHASA INDONESIA)

### 8. Testing

File baru: `tests/test_journal_validation.py`

Test yang sudah ditambahkan:
- ✅ Test regex valid diterima
- ✅ Test regex tanpa seq group ditolak
- ✅ Test regex dengan sintaks salah ditolak
- ✅ Test update journal dengan regex invalid ditolak

### 9. Kesimpulan

**Masalah Awal**: Error tidak muncul saat konfigurasi journal, hanya muncul saat posting invoice.

**Solusi**:
1. ✅ Ditambahkan validasi di level journal
2. ✅ Error muncul langsung saat save journal
3. ✅ Panduan frontend lengkap dibuat
4. ✅ Test validasi ditambahkan

**Sekarang**: Modul `adi_account_sequence` sudah **bisa jalan dengan baik** dan memberikan feedback langsung kepada user!

### 10. Cara Install & Test

1. Update module:
   ```bash
   # Di Odoo
   Apps → Update Apps List
   Apps → ADI Account Sequence → Upgrade
   ```

2. Test validasi:
   - Buka Accounting → Configuration → Journals
   - Buat journal baru
   - Coba masukkan regex yang salah (tanpa seq group)
   - Error seharusnya langsung muncul!

3. Test sequence generation:
   - Ikuti langkah-langkah di "Skenario Penggunaan" di atas
   - Buat beberapa invoice dengan goods_type berbeda
   - Lihat nomor sequence yang dihasilkan

### 11. Support

Jika ada masalah, cek:
1. **FRONTEND_GUIDE.md** - Panduan detail
2. **Troubleshooting** section di FRONTEND_GUIDE.md
3. **example_goods_type_sequence.py** - Contoh kode Python

---

**Catatan**: Semua perubahan sudah di-commit dan di-push. Module sekarang sudah berfungsi dengan baik dan memberikan validasi langsung di frontend!
