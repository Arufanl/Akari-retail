import sys
import os
import argparse
import sqlite3

# Ensure scripts dir is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from akari_label_generator import (
    render_retail_label,
    add_or_update_product,
    get_product,
    DB_PATH,
    OUTPUT_DIR
)

def search_products(query, limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    pattern = f"%{query}%"
    c.execute("""
    SELECT plu, barcode, name, short_name, size
    FROM products
    WHERE name LIKE ? OR plu = ? OR barcode = ?
    ORDER BY name ASC
    LIMIT ?
    """, (pattern, query, query, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def print_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    total = c.fetchone()[0]
    conn.close()
    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"📊 Database Stats:")
    print(f"   • Total Produk: {total:,} item")
    print(f"   • Ukuran File DB: {size_mb:.2f} MB")
    print(f"   • Lokasi DB: {os.path.abspath(DB_PATH)}")
    print(f"   • Folder Output Label: {os.path.abspath(OUTPUT_DIR)}")

def main():
    parser = argparse.ArgumentParser(description="Akari Retail Barcode & Label Service")
    subparsers = parser.add_subparsers(dest="command", help="Perintah yang tersedia")

    # Command: label
    p_label = subparsers.add_parser("label", help="Generate kartu label dari PLU atau Barcode")
    p_label.add_argument("code", help="Nomor PLU atau Barcode EAN-13")

    # Command: tb (tambah barang / barcode)
    p_tb = subparsers.add_parser("tb", help="Tambah/Perbarui produk baru ke database")
    p_tb.add_argument("plu", help="Nomor PLU toko (misal 20096783)")
    p_tb.add_argument("barcode", help="Kode barcode EAN-13 (misal 8936018025712)")
    p_tb.add_argument("name", nargs="?", default=None, help="Nama lengkap produk (opsional jika barcode sudah ada di DB)")
    p_tb.add_argument("--short", default=None, help="Nama singkat varian untuk banner kuning")
    p_tb.add_argument("--size", default=None, help="Ukuran / gramatur (misal 180 g)")

    # Command: search / cari
    p_search = subparsers.add_parser("search", help="Cari produk berdasarkan kata kunci")
    p_search.add_argument("query", help="Kata kunci pencarian nama atau kode")
    p_search.add_argument("--limit", type=int, default=10, help="Maksimal hasil yang ditampilkan")

    # Command: stats
    subparsers.add_parser("stats", help="Tampilkan statistik database")

    args = parser.parse_args()

    if args.command == "label":
        res = render_retail_label(args.code)
        if res.get("success"):
            print("✅ Label Berhasil Dibuat!")
            print(f"📁 File: {res['image_path']}")
            print("\n" + res["caption"])
        else:
            print(res.get("message", "Gagal membuat label."))

    elif args.command == "tb":
        full_name = args.name.strip() if args.name else None
        prod = add_or_update_product(
            plu=args.plu,
            barcode_num=args.barcode,
            name=full_name,
            short_name=args.short,
            size=args.size
        )
        print("✅ Produk Berhasil Disimpan ke Database!")
        print(f"   PLU: {prod['plu']} | Barcode: {prod['barcode']} | Nama: {prod['name']}")
        print("\nSedang membuat kartu label otomatis ...")
        res = render_retail_label(args.plu)
        if res.get("success"):
            print(f"📁 Label Tersimpan: {res['image_path']}")
            print("\n" + res["caption"])

    elif args.command == "search":
        results = search_products(args.query, limit=args.limit)
        if not results:
            print(f"❌ Tidak ada produk ditemukan dengan kata kunci: '{args.query}'")
        else:
            print(f"🔍 Ditemukan {len(results)} produk untuk '{args.query}':\n")
            for i, r in enumerate(results, 1):
                sz = f" ({r['size']})" if r.get('size') else ""
                print(f"{i}. {r['name']}{sz}")
                print(f"   Barcode: {r['barcode']}")
            print(f"\n💡 Hubungkan ke PLU toko dengan:")
            print(f"   /tb [PLU] [Barcode]")

    elif args.command == "stats":
        print_stats()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
