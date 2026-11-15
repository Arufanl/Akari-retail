import 'package:flutter/material.dart';
import '../theme/miku_theme.dart';
import '../services/api_service.dart';
import 'label_preview_screen.dart';

class ProductFormScreen extends StatefulWidget {
  final String scannedCode;
  final Map<String, dynamic> lookupResult;

  const ProductFormScreen({
    super.key,
    required this.scannedCode,
    required this.lookupResult,
  });

  @override
  State<ProductFormScreen> createState() => _ProductFormScreenState();
}

class _ProductFormScreenState extends State<ProductFormScreen> {
  late TextEditingController _pluCtrl;
  late TextEditingController _barcodeCtrl;
  late TextEditingController _nameCtrl;
  late TextEditingController _sizeCtrl;

  bool _isFound = false;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _isFound = widget.lookupResult['found'] == true;
    final prod = (widget.lookupResult['product'] as Map<String, dynamic>?) ?? {};

    final matchType = widget.lookupResult['match_type'] ?? '';
    final code = widget.scannedCode;

    if (_isFound) {
      if (matchType == 'plu') {
        _pluCtrl = TextEditingController(text: prod['plu'] ?? code);
        _barcodeCtrl = TextEditingController(text: prod['barcode'] ?? '');
      } else {
        _pluCtrl = TextEditingController(text: ''); // User needs to enter store PLU
        _barcodeCtrl = TextEditingController(text: prod['barcode'] ?? code);
      }
      _nameCtrl = TextEditingController(text: prod['name'] ?? '');
      _sizeCtrl = TextEditingController(text: prod['size'] ?? '');
    } else {
      _pluCtrl = TextEditingController(text: code.length == 8 ? code : '');
      _barcodeCtrl = TextEditingController(text: code.length != 8 ? code : '');
      _nameCtrl = TextEditingController(text: '');
      _sizeCtrl = TextEditingController(text: '');
    }
  }

  void _onSave() async {
    final plu = _pluCtrl.text.trim();
    final barcode = _barcodeCtrl.text.trim();
    final name = _nameCtrl.text.trim();
    final size = _sizeCtrl.text.trim();

    if (plu.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Nomor PLU toko wajib diisi!'), backgroundColor: MikuTheme.pink),
      );
      return;
    }
    if (barcode.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Nomor barcode EAN-13 wajib diisi!'), backgroundColor: MikuTheme.pink),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      final res = await ApiService.saveProduct(
        plu: plu,
        barcode: barcode,
        name: name.isNotEmpty ? name : null,
        size: size.isNotEmpty ? size : null,
      );

      if (!mounted) return;
      setState(() => _isSaving = false);

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => LabelPreviewScreen(
            plu: plu,
            barcode: barcode,
            name: name,
            size: size,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isSaving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gagal menyimpan: $e'), backgroundColor: Colors.redAccent),
      );
    }
  }

  @override
  void dispose() {
    _pluCtrl.dispose();
    _barcodeCtrl.dispose();
    _nameCtrl.dispose();
    _sizeCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Hubungkan Barang', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _isFound ? MikuTheme.lightTeal : Colors.amber.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _isFound ? MikuTheme.teal : Colors.amber),
            ),
            child: Text(
              _isFound ? 'DB 50.600 OK' : 'Barang Baru',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: _isFound ? MikuTheme.darkTeal : Colors.amber.shade900,
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Miku Cheer Box
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFE8F8F7), Color(0xFFFDE8F1)],
                ),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: MikuTheme.borderTeal),
              ),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: MikuTheme.teal, width: 2),
                      image: const DecorationImage(
                        image: AssetImage('assets/images/miku_chibi.jpg'),
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _isFound ? 'Barang Ditemukan! 🎉' : 'Daftarkan Barang Baru 📝',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                        Text(
                          _isFound
                              ? 'Nama barang otomatis ditarik dari DB 50.600. Cukup isi nomor PLU tokomu!'
                              : 'Barcode ini belum ada di 50.600. Silakan lengkapi nama produk.',
                          style: const TextStyle(fontSize: 11, color: Colors.black87),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // PLU Field (Prominent)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: MikuTheme.teal, width: 2),
                boxShadow: [
                  BoxShadow(color: MikuTheme.teal.withOpacity(0.08), blurRadius: 10),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.between,
                    children: [
                      Text('Nomor PLU Toko (8 Digit)', style: TextStyle(fontWeight: FontWeight.bold, color: MikuTheme.darkTeal)),
                      Text('Wajib Diisi', style: TextStyle(fontSize: 10, color: MikuTheme.pink, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _pluCtrl,
                    keyboardType: TextInputType.number,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, fontFamily: 'monospace', letterSpacing: 1.5),
                    decoration: const InputDecoration(
                      hintText: 'Contoh: 20069208',
                      prefixIcon: Icon(Icons.tag, color: MikuTheme.teal),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Barcode Field
            TextField(
              controller: _barcodeCtrl,
              keyboardType: TextInputType.number,
              style: const TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.bold),
              decoration: const InputDecoration(
                labelText: 'Barcode EAN-13 Kemasan',
                prefixIcon: Icon(Icons.qr_code_scanner, color: MikuTheme.teal),
              ),
            ),
            const SizedBox(height: 14),

            // Name Field
            TextField(
              controller: _nameCtrl,
              decoration: const InputDecoration(
                labelText: 'Nama Lengkap Produk',
                prefixIcon: Icon(Icons.shopping_bag_outlined, color: MikuTheme.teal),
              ),
            ),
            const SizedBox(height: 14),

            // Size Field
            TextField(
              controller: _sizeCtrl,
              decoration: const InputDecoration(
                labelText: 'Ukuran / Gramatur (misal: 600 ML, 180 GR)',
                prefixIcon: Icon(Icons.scale_outlined, color: MikuTheme.teal),
              ),
            ),
            const SizedBox(height: 28),

            // Save CTA Button
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: MikuTheme.teal,
              ),
              onPressed: _isSaving ? null : _onSave,
              child: _isSaving
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.save, size: 20),
                        SizedBox(width: 8),
                        Text('Simpan & Generate Label Kartu', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
