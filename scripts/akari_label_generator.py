import os
import sqlite3
import urllib.request
import io
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "retail_products.db")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_labels")
FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

def get_font(name, size, fallback="arialbd.ttf"):
    for cand in [os.path.join(FONTS_DIR, name), name, os.path.join(FONTS_DIR, fallback), fallback, "/system/fonts/Roboto-Bold.ttf", "/system/fonts/Roboto-Regular.ttf"]:
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype(name, size)
    except Exception:
        try:
            return ImageFont.truetype(fallback, size)
        except Exception:
            return ImageFont.load_default()

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        plu TEXT PRIMARY KEY,
        barcode TEXT NOT NULL,
        name TEXT NOT NULL,
        short_name TEXT,
        size TEXT,
        image_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_barcode ON products(barcode);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON products(name);")
    conn.commit()
    conn.close()

def get_product(plu_or_barcode):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE plu = ? OR barcode = ?", (plu_or_barcode, plu_or_barcode))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_or_update_product(plu, barcode_num, name=None, short_name=None, size=None, image_url=None):
    conn = get_db()
    cursor = conn.cursor()
    
    # Smart Auto-fill: If name is not provided, look up by barcode from DB 50.600!
    if not name:
        cursor.execute("SELECT name, short_name, size FROM products WHERE barcode = ? LIMIT 1", (barcode_num,))
        existing = cursor.fetchone()
        if existing:
            name = existing["name"]
            short_name = short_name or existing["short_name"]
            size = size or existing["size"]
        else:
            name = f"PRODUK {barcode_num}"
            
    if not image_url:
        image_url = f"https://cdn-klik.klikindomaret.com/klik-catalog/product/{plu}_meta.jpg"
    if not short_name:
        short_name = name[:30]
        
    cursor.execute("""
    INSERT OR REPLACE INTO products (plu, barcode, name, short_name, size, image_url, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
    """, (plu, barcode_num, name, short_name, size, image_url))
    conn.commit()
    conn.close()
    return get_product(plu)

def fetch_product_image(image_url):
    try:
        req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            img_data = res.read()
            return Image.open(io.BytesIO(img_data)).convert("RGBA")
    except Exception:
        img = Image.new("RGBA", (360, 220), color=(255, 251, 242, 255))
        draw = ImageDraw.Draw(img)
        draw.text((120, 100), "FOTO PRODUK", fill=(180, 175, 165, 255))
        return img

def generate_barcode_lines_only(barcode_num):
    code = barcode_num.zfill(12)[:12] if len(barcode_num) <= 12 else barcode_num[:12]
    EAN = barcode.get_barcode_class('ean13')
    writer = ImageWriter()
    options = {
        'module_width': 0.44,
        'module_height': 15.5,
        'quiet_zone': 2.0,
        'write_text': False
    }
    ean = EAN(code, writer=writer)
    fp = io.BytesIO()
    ean.write(fp, options=options)
    fp.seek(0)
    bc_img = Image.open(fp).convert("RGBA")
    return bc_img, ean.get_fullcode()

def render_retail_label(plu_or_barcode, output_filename=None):
    init_db()
    prod = get_product(plu_or_barcode)
    if not prod:
        return {
            "success": False,
            "message": (
                f"❌ Kode '{plu_or_barcode}' belum terdaftar di database.\n\n"
                "💡 Cara Praktis Menambahkan:\n"
                f"1. Jika barang ada di DB 50.600, cukup hubungkan:\n"
                f"   Ketik: /tb {plu_or_barcode} [Barcode]\n"
                "   (Nama & ukuran otomatis terisi dari database!)\n\n"
                f"2. Atau daftarkan produk baru lengkap:\n"
                f"   Ketik: /tb {plu_or_barcode} [Barcode] [Nama Produk]\n\n"
                "🔍 Mau cari barcode barangnya?\n"
                "   Ketik: /cari [Nama Barang]"
            )
        }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not output_filename:
        output_filename = f"label_{prod['plu']}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # EXACT MOCKUP DIMENSIONS & PALETTE
    W, H = 595, 848
    
    # 1. Base Warm Beige Background (#F6ECE0)
    card = Image.new("RGB", (W, H), color=(246, 236, 224))
    draw = ImageDraw.Draw(card)
    
    # Outer dark rounded border
    draw.rounded_rectangle([3, 3, W - 4, H - 4], radius=24, outline=(26, 26, 26), width=2)
    
    # Fonts - Larger, punchy, high-contrast typography
    font_plu = get_font("segoeuib.ttf", 22, "arialbd.ttf")
    font_name = get_font("segoeuib.ttf", 26, "arialbd.ttf")
    font_size_pill = get_font("segoeuib.ttf", 20, "arialbd.ttf")
    font_banner_name = get_font("segoeuib.ttf", 19, "arialbd.ttf")
    font_banner_size1 = get_font("segoeuib.ttf", 19, "arialbd.ttf")
    font_banner_size2 = get_font("segoeuib.ttf", 17, "arialbd.ttf")
    font_digits = get_font("segoeuib.ttf", 38, "arialbd.ttf")

    # 2. Header (NO "AKARI PLANOGRAM TAG", only PLU pill on top right)
    plu_pill_x1, plu_pill_y1 = 405, 18
    plu_pill_x2, plu_pill_y2 = 573, 58
    draw.rounded_rectangle([plu_pill_x1, plu_pill_y1, plu_pill_x2, plu_pill_y2], radius=8, fill=(196, 204, 215)) # #C4CCD7
    
    plu_text = f"PLU: {prod['plu']}"
    bbox_plu = draw.textbbox((0, 0), plu_text, font=font_plu)
    plu_w = bbox_plu[2] - bbox_plu[0]
    plu_h = bbox_plu[3] - bbox_plu[1]
    draw.text(
        (plu_pill_x1 + (plu_pill_x2 - plu_pill_x1 - plu_w) // 2, plu_pill_y1 + (plu_pill_y2 - plu_pill_y1 - plu_h) // 2 - 2),
        plu_text,
        fill=(43, 45, 66),
        font=font_plu
    )

    # 3. Photo Box (Top Container)
    box1_x1, box1_y1 = 21, 76
    box1_x2, box1_y2 = 574, 392
    draw.rounded_rectangle([box1_x1, box1_y1, box1_x2, box1_y2], radius=16, fill=(255, 251, 242), outline=(198, 190, 178), width=1)
    
    # Product Image
    prod_img = fetch_product_image(prod['image_url'])
    prod_img.thumbnail((440, 230), Image.Resampling.LANCZOS)
    img_px = box1_x1 + (box1_x2 - box1_x1 - prod_img.width) // 2
    img_py = box1_y1 + 18
    if prod_img.mode == 'RGBA':
        card.paste(prod_img, (img_px, img_py), prod_img)
    else:
        card.paste(prod_img, (img_px, img_py))

    # Floating Banner at bottom of Photo Box
    short_title = prod['short_name'] or prod['name']
    size_label = prod.get('size') or ""
    
    bbox_bt = draw.textbbox((0, 0), short_title, font=font_banner_name)
    title_w = bbox_bt[2] - bbox_bt[0]
    
    banner_h = 44
    yellow_w = max(210, title_w + 32)
    blue_w = 72
    total_banner_w = yellow_w + blue_w
    
    banner_x1 = box1_x1 + (box1_x2 - box1_x1 - total_banner_w) // 2
    banner_y1 = 333
    banner_x2 = banner_x1 + total_banner_w
    banner_y2 = banner_y1 + banner_h
    
    slant_offset = 18
    # Yellow part
    draw.polygon([
        (banner_x1, banner_y1),
        (banner_x1 + yellow_w + slant_offset, banner_y1),
        (banner_x1 + yellow_w, banner_y2),
        (banner_x1, banner_y2)
    ], fill=(246, 234, 174))
    
    # Blue part
    draw.polygon([
        (banner_x1 + yellow_w + slant_offset, banner_y1),
        (banner_x2, banner_y1),
        (banner_x2, banner_y2),
        (banner_x1 + yellow_w, banner_y2)
    ], fill=(191, 211, 234))
    
    # Banner Text
    draw.text((banner_x1 + 14, banner_y1 + 11), short_title, fill=(50, 45, 40), font=font_banner_name)
    
    size_parts = size_label.split()
    if len(size_parts) >= 2:
        draw.text((banner_x1 + yellow_w + 22, banner_y1 + 4), size_parts[0], fill=(35, 45, 60), font=font_banner_size1)
        draw.text((banner_x1 + yellow_w + 30, banner_y1 + 22), " ".join(size_parts[1:]), fill=(35, 45, 60), font=font_banner_size2)
    else:
        draw.text((banner_x1 + yellow_w + 20, banner_y1 + 11), size_label, fill=(35, 45, 60), font=font_banner_size1)

    # 4. Middle Section (Between Boxes)
    title_y = 422
    name_str = prod['name']
    draw.text((36, title_y), name_str, fill=(43, 45, 66), font=font_name)
    
    # Gramatur Pill
    pill_y = 472
    pill_w = 160
    pill_h = 36
    draw.rounded_rectangle([36, pill_y, 36 + pill_w, pill_y + pill_h], radius=7, fill=(220, 227, 236))
    
    # Clean vector icon (cross-platform, immune to font codec limitations)
    icon_color = (65, 80, 100)
    draw.rectangle([50, pill_y + 9, 54, pill_y + 11], fill=icon_color)
    draw.rounded_rectangle([47, pill_y + 12, 57, pill_y + 25], radius=2, fill=icon_color)
    
    clean_size = (size_label if size_label else "Standar").encode('ascii', 'ignore').decode('ascii')
    draw.text((66, pill_y + 4), clean_size, fill=(50, 60, 75), font=font_size_pill)

    # 5. Barcode Box (Bottom Container)
    box2_x1, box2_y1 = 21, 535
    box2_x2, box2_y2 = 574, 827
    draw.rounded_rectangle([box2_x1, box2_y1, box2_x2, box2_y2], radius=16, fill=(255, 251, 242), outline=(198, 190, 178), width=1)
    
    # Barcode Lines
    bc_img, full_code = generate_barcode_lines_only(prod['barcode'])
    bc_img.thumbnail((440, 195), Image.Resampling.LANCZOS)
    bc_px = box2_x1 + (box2_x2 - box2_x1 - bc_img.width) // 2
    bc_py = box2_y1 + 24
    card.paste(bc_img, (bc_px, bc_py), bc_img)
    
    # Barcode Digits (Cleanly spaced)
    # Drawing with custom tracking to match the reference look
    digit_text = full_code
    char_spacing = 8
    total_w = sum((draw.textbbox((0, 0), ch, font=font_digits)[2] - draw.textbbox((0, 0), ch, font=font_digits)[0]) for ch in digit_text) + (len(digit_text) - 1) * char_spacing
    cur_x = box2_x1 + (box2_x2 - box2_x1 - total_w) // 2
    code_py = box2_y1 + bc_img.height + 34
    
    for ch in digit_text:
        ch_w = draw.textbbox((0, 0), ch, font=font_digits)[2] - draw.textbbox((0, 0), ch, font=font_digits)[0]
        draw.text((cur_x, code_py), ch, fill=(26, 26, 26), font=font_digits)
        cur_x += ch_w + char_spacing
    
    card.save(output_path, quality=95)
    
    caption = (
        f"📌 PLU: {prod['plu']}\n"
        f"📦 PRODUCT: {prod['name']}"
    )
    
    return {
        "success": True,
        "image_path": output_path,
        "caption": caption,
        "product": prod
    }

if __name__ == "__main__":
    init_db()
    res = render_retail_label("20096783")
    print("Exact Match Generated:", res['image_path'])
