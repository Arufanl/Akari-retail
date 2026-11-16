import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:gal/gal.dart';
import '../theme/miku_theme.dart';
import '../services/api_service.dart';

class LabelPreviewScreen extends StatefulWidget {
  final String plu;
  final String barcode;
  final String name;
  final String size;

  const LabelPreviewScreen({
    super.key,
    required this.plu,
    required this.barcode,
    required this.name,
    required this.size,
  });

  @override
  State<LabelPreviewScreen> createState() => _LabelPreviewScreenState();
}

class _LabelPreviewScreenState extends State<LabelPreviewScreen> {
  Uint8List? _imageBytes;
  bool _isLoading = true;
  bool _isSavingGallery = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchImage();
  }

  void _fetchImage() async {
    try {
      final bytes = await ApiService.fetchLabelBytes(widget.plu);
      if (mounted) {
        setState(() {
          _imageBytes = bytes;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  void _saveToGallery() async {
    if (_imageBytes == null) return;
    setState(() => _isSavingGallery = true);

    try {
      final hasAccess = await Gal.hasAccess();
      if (!hasAccess) {
        await Gal.requestAccess();
      }
      await Gal.putImageBytes(
        _imageBytes!,
        name: "akari_label_${widget.plu}",
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Berhasil disimpan ke Galeri HP!'),
          backgroundColor: MikuTheme.teal,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal menyimpan: $e'),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      if (mounted) setState(() => _isSavingGallery = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7FCFB),
      appBar: AppBar(
        title: const Text('Pratinjau Label', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Miku Status Stamp
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: MikuTheme.borderTeal),
              ),
              child: Row(
                children: [
                  const Text('🎉 ', style: TextStyle(fontSize: 18)),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Label PLU: ${widget.plu} Sukses Dibuat!', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        const Text('Format siap cetak untuk rak ritel', style: TextStyle(fontSize: 11, color: MikuTheme.darkTeal)),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: MikuTheme.pink,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text('APPROVED', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // High-Resolution Card Display
            Container(
              width: 260,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 20, offset: const Offset(0, 8)),
                ],
              ),
              clipBehavior: Clip.antiAlias,
              child: _isLoading
                  ? Container(
                      height: 360,
                      color: Colors.white,
                      child: const Center(
                        child: CircularProgressIndicator(color: MikuTheme.teal),
                      ),
                    )
                  : _error != null
                      ? Container(
                          height: 360,
                          color: Colors.white,
                          padding: const EdgeInsets.all(20),
                          child: Center(
                            child: Text('Gagal memuat: $_error', textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
                          ),
                        )
                      : Image.memory(
                          _imageBytes!,
                          fit: BoxFit.contain,
                        ),
            ),
            const SizedBox(height: 28),

            // Action Buttons
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 24),
                backgroundColor: MikuTheme.teal,
                minimumSize: const Size.fromHeight(50),
              ),
              onPressed: (_imageBytes != null && !_isSavingGallery) ? _saveToGallery : null,
              icon: _isSavingGallery
                  ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.download, size: 20),
              label: const Text('Simpan Gambar ke Galeri HP', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 12),

            OutlinedButton(
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                side: const BorderSide(color: MikuTheme.teal),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                minimumSize: const Size.fromHeight(50),
              ),
              onPressed: () => Navigator.pop(context),
              child: const Text('Lanjut Scan Barang Berikutnya', style: TextStyle(color: MikuTheme.darkTeal, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}
