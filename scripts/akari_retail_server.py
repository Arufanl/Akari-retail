import os
import sys
import io
import json
import sqlite3
import socket
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, HTMLResponse
from pydantic import BaseModel
import qrcode
import uvicorn

# Ensure script dir is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from akari_label_generator import (
    render_retail_label,
    add_or_update_product,
    get_product,
    DB_PATH,
    OUTPUT_DIR
)

API_KEY = os.environ.get("AKARI_API_KEY", "miku_retail_secret_key_2026")
PORT = int(os.environ.get("AKARI_PORT", 5000))

app = FastAPI(
    title="Akari Retail API - Hatsune Miku Edition",
    description="Backend Server untuk Scanner Barcode & Label Rak Ritel di Tablet Android",
    version="1.0.0"
)

# Enable CORS for Flutter Client / Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

def verify_api_key(x_api_key: Optional[str] = Header(None), api_key: Optional[str] = Query(None)):
    token = x_api_key or api_key
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="API Key tidak valid atau tidak disertakan.")
    return True

class ProductSaveRequest(BaseModel):
    plu: str
    barcode: str
    name: Optional[str] = None
    short_name: Optional[str] = None
    size: Optional[str] = None

def search_products(query: str, limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    pattern = f"%{query}%"
    c.execute("""
    SELECT plu, barcode, name, short_name, size, image_url
    FROM products
    WHERE name LIKE ? OR plu = ? OR barcode = ?
    ORDER BY name ASC
    LIMIT ?
    """, (pattern, query, query, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    total = c.fetchone()[0]
    conn.close()
    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024) if os.path.exists(DB_PATH) else 0
    return {"total_products": total, "db_size_mb": round(size_mb, 2)}

# ==================== PUBLIC WEB & QR SETUP ====================

@app.get("/", response_class=HTMLResponse)
def index_dashboard():
    stats = get_stats()
    server_url = f"http://{LOCAL_IP}:{PORT}"
    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Akari Retail Server - Hatsune Miku Edition</title>
      <style>
        body {{
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #EDF7F6;
          color: #2B333E;
          margin: 0;
          padding: 24px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }}
        .card {{
          background: white;
          border-radius: 28px;
          border: 2px solid #C8EBE7;
          box-shadow: 0 12px 30px rgba(57, 197, 187, 0.18);
          padding: 28px;
          max-width: 460px;
          width: 100%;
          text-align: center;
          box-sizing: border-box;
        }}
        .badge {{
          background: #39C5BB;
          color: white;
          font-weight: bold;
          font-size: 11px;
          padding: 5px 12px;
          border-radius: 12px;
          display: inline-block;
          margin-bottom: 8px;
        }}
        h1 {{ margin: 6px 0; font-size: 22px; color: #1E293B; }}
        .qr-box {{
          background: #F7FCFB;
          border: 2px dashed #39C5BB;
          border-radius: 20px;
          padding: 16px;
          margin: 18px 0;
          display: inline-block;
        }}
        .info-pill {{
          background: #E8F8F7;
          border: 1px solid #C8EBE7;
          border-radius: 14px;
          padding: 10px 14px;
          font-size: 12px;
          color: #229E95;
          margin-bottom: 16px;
          font-family: monospace;
          word-break: break-all;
        }}
        .btn-launch {{
          display: block;
          width: 100%;
          padding: 14px;
          background: #39C5BB;
          color: white;
          text-decoration: none;
          border-radius: 16px;
          font-weight: bold;
          font-size: 15px;
          box-shadow: 0 4px 14px rgba(57, 197, 187, 0.35);
          box-sizing: border-box;
          margin-top: 10px;
        }}
        .btn-launch:hover {{ background: #229E95; }}
        .stats {{
          font-size: 13px;
          color: #64748B;
          margin-top: 16px;
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <span class="badge">初音ミク x Akari Retail</span>
        <h1>Tablet Home Server Aktif 🟢</h1>
        <p style="font-size: 13px; color: #64748B; margin-top: 2px;">
          Buka kamera HP Anda dan scan QR di bawah ini untuk membuka aplikasi:
        </p>

        <div class="qr-box">
          <img src="/api/config/qr" alt="QR Setup" width="220" height="220" style="display:block; border-radius: 10px;" />
        </div>

        <a href="/app" class="btn-launch">📱 Buka Web Scanner di HP Sekarang</a>

        <div class="info-pill" style="margin-top: 16px;">
          URL: {server_url}<br>
          API Key: {API_KEY}
        </div>

        <div class="stats">
          📊 Database: <b>{stats['total_products']:,} Item</b> ({stats['db_size_mb']} MB)<br>
          ⚡ Model: <b>0 Token AI (100% Deterministik)</b>
        </div>
      </div>
    </body>
    </html>
    """

# ==================== LIVE WEB SCANNER APP (MIKU THEMED) ====================

@app.get("/app", response_class=HTMLResponse)
def live_miku_app():
    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
      <title>Akari Retail - Hatsune Miku</title>
      <script src="https://unpkg.com/html5-qrcode"></script>
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #EBF6F5;
          color: #2B333E;
          height: 100vh;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }}
        header {{
          background: white;
          padding: 12px 16px;
          border-bottom: 1px solid #C8EBE7;
          display: flex;
          align-items: center;
          justify-content: space-between;
          box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }}
        .brand {{
          display: flex;
          align-items: center;
          gap: 10px;
        }}
        .miku-badge {{
          background: #39C5BB;
          color: white;
          font-weight: 900;
          font-family: monospace;
          font-size: 11px;
          padding: 4px 7px;
          border-radius: 8px;
        }}
        .brand h1 {{ font-size: 15px; font-weight: 800; color: #1E293B; }}
        .brand p {{ font-size: 10px; color: #229E95; font-weight: 600; }}
        
        /* Navigation Tabs */
        .tabs {{
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          background: white;
          border-bottom: 1px solid #C8EBE7;
          padding: 6px;
          gap: 6px;
        }}
        .tab-btn {{
          padding: 8px 4px;
          border: none;
          background: transparent;
          font-size: 12px;
          font-weight: bold;
          color: #64748B;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s;
        }}
        .tab-btn.active {{
          background: #39C5BB;
          color: white;
          box-shadow: 0 2px 6px rgba(57, 197, 187, 0.3);
        }}

        main {{
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
        }}
        .view {{ display: none; flex-direction: column; height: 100%; }}
        .view.active {{ display: flex; }}

        /* Scanner Screen */
        #reader {{
          width: 100%;
          border-radius: 20px;
          overflow: hidden;
          border: 3px solid #39C5BB;
          background: black;
          box-shadow: 0 8px 24px rgba(57, 197, 187, 0.2);
        }}
        .tip-box {{
          background: white;
          border: 1px solid #C8EBE7;
          border-radius: 16px;
          padding: 12px 14px;
          margin-bottom: 14px;
          font-size: 12px;
          font-weight: 600;
          color: #229E95;
          display: flex;
          align-items: center;
          gap: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }}

        /* Forms & Cards */
        .card {{
          background: white;
          border-radius: 20px;
          border: 1px solid #C8EBE7;
          padding: 16px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.02);
          margin-bottom: 14px;
        }}
        label {{
          display: block;
          font-size: 11px;
          font-weight: bold;
          color: #229E95;
          margin-bottom: 6px;
        }}
        input {{
          width: 100%;
          padding: 12px 14px;
          border-radius: 14px;
          border: 1px solid #C8EBE7;
          background: #F7FCFB;
          font-size: 14px;
          font-family: inherit;
          color: #1E293B;
          outline: none;
          transition: border-color 0.2s;
        }}
        input:focus {{
          border-color: #39C5BB;
          background: white;
        }}
        .btn-primary {{
          width: 100%;
          padding: 14px;
          background: #39C5BB;
          color: white;
          font-weight: bold;
          font-size: 14px;
          border: none;
          border-radius: 16px;
          cursor: pointer;
          box-shadow: 0 4px 14px rgba(57, 197, 187, 0.35);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          margin-top: 10px;
        }}
        .btn-primary:active {{ transform: scale(0.98); }}
        .btn-secondary {{
          width: 100%;
          padding: 12px;
          background: #F0F9F8;
          color: #229E95;
          font-weight: bold;
          font-size: 13px;
          border: 1px solid #C8EBE7;
          border-radius: 14px;
          cursor: pointer;
          margin-top: 8px;
        }}

        /* Label Image Preview */
        .label-preview-img {{
          max-width: 250px;
          width: 100%;
          border-radius: 18px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.15);
          display: block;
          margin: 12px auto;
        }}
      </style>
    </head>
    <body>
      <header>
        <div class="brand">
          <span class="miku-badge">01</span>
          <div>
            <h1>Akari Retail</h1>
            <p>Hatsune Miku Scanner (Live)</p>
          </div>
        </div>
        <span style="font-size: 10px; background: #E8F8F7; color: #229E95; font-weight: bold; padding: 4px 8px; border-radius: 8px; border: 1px solid #C8EBE7;">
          🟢 Server OK
        </span>
      </header>

      <div class="tabs">
        <button class="tab-btn active" id="btn-tab-scan" onclick="showView('scan')">📷 Scan</button>
        <button class="tab-btn" id="btn-tab-form" onclick="showView('form')">📝 Form</button>
        <button class="tab-btn" id="btn-tab-preview" onclick="showView('preview')">🏷️ Label</button>
        <button class="tab-btn" id="btn-tab-search" onclick="showView('search')">🔍 Cari</button>
      </div>

      <main>
        <!-- VIEW 1: CAMERA SCANNER -->
        <div id="view-scan" class="view active">
          <div class="tip-box">
            <span>🎵</span>
            <span>Arahkan kamera HP ke barcode kemasan produk ya~</span>
          </div>
          
          <div id="reader"></div>

          <div style="margin-top: 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <button class="btn-secondary" onclick="promptManualCode()">⌨️ Input Angka</button>
            <button class="btn-secondary" onclick="showView('search')">🔍 Cari Nama</button>
          </div>
        </div>

        <!-- VIEW 2: PRODUCT FORM -->
        <div id="view-form" class="view">
          <div class="tip-box" style="background: #FDF2F7; border-color: #FBCFE8; color: #DB2777;">
            <span>🎉</span>
            <span id="form-status-text">Hubungkan nomor PLU toko dengan barcode kemasan!</span>
          </div>

          <div class="card" style="border: 2px solid #39C5BB;">
            <label style="color: #229E95;">Nomor PLU Toko (8 Digit) *</label>
            <input type="number" id="input-plu" placeholder="Contoh: 20069208" style="font-weight: bold; font-family: monospace; font-size: 16px;">
          </div>

          <div class="card">
            <label>Barcode EAN-13 Kemasan *</label>
            <input type="number" id="input-barcode" placeholder="Contoh: 8996001600269" style="font-family: monospace; font-weight: bold; margin-bottom: 12px;">

            <label>Nama Produk</label>
            <input type="text" id="input-name" placeholder="Nama barang..." style="margin-bottom: 12px;">

            <label>Ukuran / Gramatur</label>
            <input type="text" id="input-size" placeholder="Contoh: 600 ML, 180 GR">
          </div>

          <button class="btn-primary" onclick="submitProductForm()">💾 Simpan & Generate Label</button>
        </div>

        <!-- VIEW 3: LABEL PREVIEW -->
        <div id="view-preview" class="view" style="text-align: center;">
          <div class="tip-box" style="justify-content: center;">
            <span>✅</span>
            <span id="preview-title">Label Rak Siap Dicetak!</span>
          </div>

          <img id="label-image" src="" class="label-preview-img" alt="Label Preview" />

          <a id="btn-download-img" href="#" download class="btn-primary" style="text-decoration: none;">📥 Simpan Gambar ke Galeri HP</a>
          <button class="btn-secondary" onclick="showView('scan')">Lanjut Scan Barang Berikutnya</button>
        </div>

        <!-- VIEW 4: SEARCH -->
        <div id="view-search" class="view">
          <div style="display: flex; gap: 8px; margin-bottom: 12px;">
            <input type="text" id="input-search" placeholder="Ketik nama (misal: Indomie, Aqua)..." onkeydown="if(event.key==='Enter') executeSearch()">
            <button class="btn-primary" style="width: auto; padding: 10px 16px; margin: 0;" onclick="executeSearch()">Cari</button>
          </div>

          <div id="search-results" style="overflow-y: auto; flex: 1;">
            <p style="text-align: center; color: #94A3B8; font-size: 13px; margin-top: 30px;">Ketik kata kunci nama produk di database 50.600</p>
          </div>
        </div>
      </main>

      <script>
        const API_KEY = '{API_KEY}';
        let html5QrCode = null;

        function showView(viewId) {{
          document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
          document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          document.getElementById('view-' + viewId).classList.add('active');
          document.getElementById('btn-tab-' + viewId).classList.add('active');

          if (viewId === 'scan') {{
            startScanner();
          }} else {{
            stopScanner();
          }}
        }}

        function startScanner() {{
          if (!html5QrCode) {{
            html5QrCode = new Html5Qrcode("reader");
          }}
          html5QrCode.start(
            {{ facingMode: "environment" }},
            {{ fps: 15, qrbox: {{ width: 250, height: 140 }} }},
            (decodedText) => {{
              console.log("Scanned:", decodedText);
              stopScanner();
              lookupAndFill(decodedText.trim());
            }},
            (error) => {{}}
          ).catch(err => console.log("Scanner start err:", err));
        }}

        function stopScanner() {{
          if (html5QrCode && html5QrCode.isScanning) {{
            html5QrCode.stop().catch(err => console.log("Scanner stop err:", err));
          }}
        }}

        async function lookupAndFill(code) {{
          try {{
            const res = await fetch(`/api/product/lookup?code=${{encodeURIComponent(code)}}`, {{
              headers: {{ 'X-API-Key': API_KEY }}
            }});
            const data = await res.json();
            
            showView('form');
            if (data.found && data.product) {{
              const p = data.product;
              document.getElementById('input-barcode').value = p.barcode || code;
              document.getElementById('input-plu').value = p.plu !== p.barcode ? p.plu : '';
              document.getElementById('input-name').value = p.name || '';
              document.getElementById('input-size').value = p.size || '';
              document.getElementById('form-status-text').innerText = "Barang ada di DB 50.600! Tinggal isi nomor PLU tokomu.";
            }} else {{
              document.getElementById('input-barcode').value = code;
              document.getElementById('input-plu').value = code.length === 8 ? code : '';
              document.getElementById('input-name').value = '';
              document.getElementById('input-size').value = '';
              document.getElementById('form-status-text').innerText = "Barang baru belum terdaftar. Silakan lengkapi datanya.";
            }}
            document.getElementById('input-plu').focus();
          }} catch (e) {{
            alert("Gagal koneksi ke server tablet: " + e.message);
          }}
        }}

        function promptManualCode() {{
          const code = prompt("Masukkan nomor Barcode atau PLU:");
          if (code && code.trim()) {{
            lookupAndFill(code.trim());
          }}
        }}

        async function submitProductForm() {{
          const plu = document.getElementById('input-plu').value.trim();
          const barcode = document.getElementById('input-barcode').value.trim();
          const name = document.getElementById('input-name').value.trim();
          const size = document.getElementById('input-size').value.trim();

          if (!plu || !barcode) {{
            alert("Nomor PLU dan Barcode wajib diisi!");
            return;
          }}

          try {{
            const res = await fetch('/api/product/save', {{
              method: 'POST',
              headers: {{
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
              }},
              body: JSON.stringify({{ plu, barcode, name, size }})
            }});
            const data = await res.json();
            if (data.success) {{
              // Load Preview
              document.getElementById('label-image').src = `/api/product/label/${{plu}}?t=${{Date.now()}}`;
              document.getElementById('btn-download-img').href = `/api/product/label/${{plu}}`;
              document.getElementById('preview-title').innerText = `Label PLU: ${{plu}} Sukses Dibuat!`;
              showView('preview');
            }} else {{
              alert("Gagal: " + (data.detail || data.message));
            }}
          }} catch (e) {{
            alert("Error: " + e.message);
          }}
        }}

        async function executeSearch() {{
          const q = document.getElementById('input-search').value.trim();
          if (!q) return;
          const container = document.getElementById('search-results');
          container.innerHTML = '<p style="text-align:center; color:#229E95; padding:20px;">Mencari di DB 50.600...</p>';

          try {{
            const res = await fetch(`/api/product/search?q=${{encodeURIComponent(q)}}&limit=25`, {{
              headers: {{ 'X-API-Key': API_KEY }}
            }});
            const data = await res.json();
            if (!data.results || data.results.length === 0) {{
              container.innerHTML = `<p style="text-align:center; color:#94A3B8; padding:20px;">Tidak ditemukan produk untuk "${{q}}"</p>`;
              return;
            }}

            let html = '';
            data.results.forEach(item => {{
              html += `
                <div class="card" onclick="lookupAndFill('${{item.barcode}}')" style="cursor:pointer; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                  <div>
                    <div style="font-size:13px; font-weight:bold; color:#1E293B;">${{item.name}}</div>
                    <div style="font-size:11px; color:#229E95; font-family:monospace; margin-top:2px;">Barcode: ${{item.barcode}} ${{item.size ? '• ' + item.size : ''}}</div>
                  </div>
                  <span style="font-size:10px; background:#E8F8F7; color:#229E95; font-weight:bold; padding:4px 8px; border-radius:8px;">Pilih →</span>
                </div>
              `;
            }});
            container.innerHTML = html;
          }} catch (e) {{
            container.innerHTML = `<p style="color:red; text-align:center;">Gagal: ${{e.message}}</p>`;
          }}
        }}

        // Start scanner on initial load
        window.addEventListener('load', () => {{
          showView('scan');
        }});
      </script>
    </body>
    </html>
    """

@app.get("/api/config/info")
def get_config_info():
    stats = get_stats()
    return {
        "success": True,
        "server_url": f"http://{LOCAL_IP}:{PORT}",
        "local_ip": LOCAL_IP,
        "port": PORT,
        "api_key": API_KEY,
        "stats": stats
    }

@app.get("/api/config/qr")
def get_config_qr():
    # Encode direct mobile app web URL so camera scan opens the app directly!
    app_url = f"http://{LOCAL_IP}:{PORT}/app"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#229E95", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")

# ==================== PRODUCT API ENDPOINTS ====================

@app.get("/api/product/lookup")
def lookup_product(code: str, authorized: bool = Depends(verify_api_key)):
    code_clean = code.strip()
    prod = get_product(code_clean)
    if not prod:
        return {
            "success": True,
            "found": False,
            "code": code_clean,
            "message": f"Kode '{code_clean}' belum terdaftar di database."
        }
    
    is_plu_match = (prod["plu"] == code_clean)
    label_path = os.path.join(OUTPUT_DIR, f"label_{prod['plu']}.png")
    
    return {
        "success": True,
        "found": True,
        "match_type": "plu" if is_plu_match else "barcode",
        "product": {
            "plu": prod["plu"],
            "barcode": prod["barcode"],
            "name": prod["name"],
            "short_name": prod.get("short_name") or "",
            "size": prod.get("size") or "",
            "image_url": prod.get("image_url") or "",
            "has_label_cache": os.path.exists(label_path),
            "label_url": f"/api/product/label/{prod['plu']}"
        }
    }

@app.get("/api/product/search")
def search_product_endpoint(q: str, limit: int = 20, authorized: bool = Depends(verify_api_key)):
    query = q.strip()
    if not query:
        return {"success": True, "total": 0, "results": []}
    
    results = search_products(query, limit=limit)
    return {
        "success": True,
        "query": query,
        "total": len(results),
        "results": [
            {
                "plu": r["plu"],
                "barcode": r["barcode"],
                "name": r["name"],
                "short_name": r.get("short_name") or "",
                "size": r.get("size") or "",
                "label_url": f"/api/product/label/{r['plu']}"
            }
            for r in results
        ]
    }

@app.post("/api/product/save")
def save_product(req: ProductSaveRequest, authorized: bool = Depends(verify_api_key)):
    plu_clean = req.plu.strip()
    bc_clean = req.barcode.strip()
    name_clean = req.name.strip() if req.name else None
    
    if not plu_clean or not bc_clean:
        raise HTTPException(status_code=400, detail="PLU dan Barcode wajib diisi.")
        
    prod = add_or_update_product(
        plu=plu_clean,
        barcode_num=bc_clean,
        name=name_clean,
        short_name=req.short_name,
        size=req.size
    )
    
    # Generate / update shelf label PNG
    label_res = render_retail_label(plu_clean)
    
    return {
        "success": True,
        "message": "Produk dan kartu label berhasil disimpan!",
        "product": {
            "plu": prod["plu"],
            "barcode": prod["barcode"],
            "name": prod["name"],
            "short_name": prod.get("short_name") or "",
            "size": prod.get("size") or "",
            "image_url": prod.get("image_url") or "",
            "label_url": f"/api/product/label/{prod['plu']}",
            "label_success": label_res.get("success", False)
        }
    }

@app.get("/api/product/label/{code}")
def get_label_image(code: str):
    code_clean = code.strip()
    prod = get_product(code_clean)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Produk {code_clean} tidak ditemukan.")
    
    label_path = os.path.join(OUTPUT_DIR, f"label_{prod['plu']}.png")
    if not os.path.exists(label_path):
        res = render_retail_label(prod['plu'])
        if not res.get("success") or not os.path.exists(label_path):
            raise HTTPException(status_code=500, detail="Gagal me-render kartu label.")
            
    return FileResponse(label_path, media_type="image/png", filename=f"label_{prod['plu']}.png")

@app.get("/api/stats")
def stats_endpoint(authorized: bool = Depends(verify_api_key)):
    return {
        "success": True,
        "stats": get_stats()
    }

def start_server():
    print(f"🚀 Memulai Akari Retail Server di http://0.0.0.0:{PORT}...")
    print(f"📱 Akses di browser/HP: http://{LOCAL_IP}:{PORT}/app")
    print(f"🔑 API Key: {API_KEY}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    start_server()
