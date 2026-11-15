import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../theme/miku_theme.dart';
import '../services/api_service.dart';
import 'product_form_screen.dart';
import 'search_screen.dart';
import 'settings_screen.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final MobileScannerController _controller = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal,
    facing: CameraFacing.back,
    torchEnabled: false,
  );

  bool _isProcessing = false;
  bool _isTorchOn = false;

  void _onDetect(BarcodeCapture capture) async {
    if (_isProcessing) return;
    final List<Barcode> barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;

    final String? rawCode = barcodes.first.rawValue;
    if (rawCode == null || rawCode.trim().isEmpty) return;

    final code = rawCode.trim();
    setState(() => _isProcessing = true);

    try {
      final res = await ApiService.lookupProduct(code);
      if (!mounted) return;

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ProductFormScreen(
            scannedCode: code,
            lookupResult: res,
          ),
        ),
      ).then((_) {
        if (mounted) setState(() => _isProcessing = false);
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Koneksi Server Gagal: $e'),
          backgroundColor: Colors.redAccent,
        ),
      );
      setState(() => _isProcessing = false);
    }
  }

  void _manualInputDialog() {
    final textCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Text('⌨️ ', style: TextStyle(fontSize: 20)),
            Text('Input Kode Manual', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ],
        ),
        content: TextField(
          controller: textCtrl,
          keyboardType: TextInputType.number,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'Masukkan Barcode atau PLU...',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Batal', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              final code = textCtrl.text.trim();
              if (code.isNotEmpty) {
                Navigator.pop(ctx);
                _lookupManual(code);
              }
            },
            child: const Text('Cari'),
          ),
        ],
      ),
    );
  }

  void _lookupManual(String code) async {
    setState(() => _isProcessing = true);
    try {
      final res = await ApiService.lookupProduct(code);
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ProductFormScreen(
            scannedCode: code,
            lookupResult: res,
          ),
        ),
      ).then((_) {
        if (mounted) setState(() => _isProcessing = false);
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.redAccent),
      );
      setState(() => _isProcessing = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7FCFB),
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
              decoration: BoxDecoration(
                color: MikuTheme.teal,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                '01',
                style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w900, fontFamily: 'monospace'),
              ),
            ),
            const SizedBox(width: 8),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Akari Retail', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900)),
                Text('Scanner Hatsune Miku', style: TextStyle(fontSize: 10, color: MikuTheme.darkTeal, fontWeight: FontWeight.w600)),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(
              _isTorchOn ? Icons.flash_on : Icons.flash_off,
              color: _isTorchOn ? Colors.amber : Colors.grey,
            ),
            onPressed: () {
              _controller.toggleTorch();
              setState(() => _isTorchOn = !_isTorchOn);
            },
          ),
          IconButton(
            icon: const Icon(Icons.search, color: MikuTheme.darkTeal),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SearchScreen())),
          ),
          IconButton(
            icon: const Icon(Icons.settings, color: Colors.grey),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
          ),
        ],
      ),
      body: Column(
        children: [
          // Miku Speech Bubble
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: MikuTheme.borderTeal),
              boxShadow: [
                BoxShadow(color: MikuTheme.teal.withOpacity(0.08), blurRadius: 10, offset: const Offset(0, 3)),
              ],
            ),
            child: const Row(
              children: [
                Text('🎵 ', style: TextStyle(fontSize: 14)),
                Expanded(
                  child: Text(
                    'Arahkan kamera ke barcode kemasan produk ya~',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: MikuTheme.darkTeal),
                  ),
                ),
              ],
            ),
          ),

          // Camera Viewfinder Area
          Expanded(
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: MikuTheme.teal, width: 3),
                boxShadow: [
                  BoxShadow(color: MikuTheme.teal.withOpacity(0.15), blurRadius: 20),
                ],
              ),
              clipBehavior: Clip.antiAlias,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  MobileScanner(
                    controller: _controller,
                    onDetect: _onDetect,
                  ),

                  // Framing Target Box
                  Container(
                    width: 240,
                    height: 140,
                    decoration: BoxDecoration(
                      border: Border.all(color: MikuTheme.teal.withOpacity(0.7), width: 2),
                      borderRadius: BorderRadius.circular(16),
                      color: Colors.white.withOpacity(0.15),
                    ),
                  ),

                  if (_isProcessing)
                    Container(
                      color: Colors.black45,
                      child: const Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(color: MikuTheme.teal),
                            SizedBox(height: 12),
                            Text(
                              'Mengecek DB 50.600...',
                              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),

          // Bottom Action Panel
          Container(
            padding: const EdgeInsets.all(20),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
              boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 15, offset: Offset(0, -2))],
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: MikuTheme.softBg,
                          foregroundColor: MikuTheme.darkTeal,
                          elevation: 0,
                          side: const BorderSide(color: MikuTheme.borderTeal),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        onPressed: _manualInputDialog,
                        icon: const Icon(Icons.keyboard, size: 18),
                        label: const Text('Input PLU Saja'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: MikuTheme.softBg,
                          foregroundColor: Colors.blueGrey,
                          elevation: 0,
                          side: const BorderSide(color: MikuTheme.borderTeal),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SearchScreen())),
                        icon: const Icon(Icons.search, size: 18),
                        label: const Text('Cari Nama'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
