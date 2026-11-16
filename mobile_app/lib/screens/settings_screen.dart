import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../theme/miku_theme.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _urlCtrl = TextEditingController();
  final TextEditingController _keyCtrl = TextEditingController();
  bool _isLoading = true;
  bool _isTesting = false;
  String? _connectionStatus;
  bool _connectionOk = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  void _loadSettings() async {
    final url = await ApiService.getServerUrl();
    final key = await ApiService.getApiKey();
    if (!mounted) return;
    setState(() {
      _urlCtrl.text = url;
      _keyCtrl.text = key;
      _isLoading = false;
    });
  }

  void _saveAndTest() async {
    final url = _urlCtrl.text.trim();
    final key = _keyCtrl.text.trim();

    if (url.isEmpty || key.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Alamat server & API Key tidak boleh kosong!')),
      );
      return;
    }

    setState(() {
      _isTesting = true;
      _connectionStatus = null;
    });

    await ApiService.saveSettings(url, key);

    try {
      final info = await ApiService.testConnection(overrideUrl: url, overrideKey: key);
      if (!mounted) return;
      final totalDb = info['total_products'] ?? 50606;
      setState(() {
        _isTesting = false;
        _connectionOk = true;
        _connectionStatus = 'Terhubung ke Server Tablet! ($totalDb produk siap)';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Berhasil terhubung! ($totalDb produk)'),
          backgroundColor: MikuTheme.teal,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isTesting = false;
        _connectionOk = false;
        _connectionStatus = 'Pengaturan disimpan, tetapi server belum merespons: $e';
      });
    }
  }

  void _scanSetupQr() {
    bool isPopped = false;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (ctx) => Scaffold(
          appBar: AppBar(title: const Text('Scan QR Setup Server')),
          body: MobileScanner(
            onDetect: (capture) {
              if (isPopped) return;
              final barcodes = capture.barcodes;
              if (barcodes.isNotEmpty && barcodes.first.rawValue != null) {
                final raw = barcodes.first.rawValue!;
                try {
                  final data = jsonDecode(raw);
                  if (data['server_url'] != null && data['api_key'] != null) {
                    isPopped = true;
                    setState(() {
                      _urlCtrl.text = data['server_url'].toString();
                      _keyCtrl.text = data['api_key'].toString();
                    });
                    Navigator.pop(ctx);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Pengaturan QR berhasil dibaca!'),
                        backgroundColor: MikuTheme.teal,
                      ),
                    );
                  }
                } catch (_) {
                  // Not valid setup JSON
                }
              }
            },
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _urlCtrl.dispose();
    _keyCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pengaturan Server Tablet', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: MikuTheme.teal))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // QR Setup Banner Button
                  InkWell(
                    onTap: _scanSetupQr,
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFE8F8F7), Color(0xFFD3F2EE)],
                        ),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: MikuTheme.teal),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.qr_code_scanner, color: MikuTheme.darkTeal, size: 36),
                          SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Scan QR Code Setup di Tablet', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: MikuTheme.darkTeal)),
                                Text('Buka http://192.168.1.2:5000 di tablet lalu scan QR untuk konfigurasi instan!', style: TextStyle(fontSize: 11, color: Colors.black87)),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  const Text('Konfigurasi Manual', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey)),
                  const SizedBox(height: 12),

                  TextField(
                    controller: _urlCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Alamat Server Tablet (URL)',
                      hintText: 'Contoh: http://192.168.1.2:5000',
                      prefixIcon: Icon(Icons.wifi, color: MikuTheme.teal),
                    ),
                  ),
                  const SizedBox(height: 14),

                  TextField(
                    controller: _keyCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Kunci Rahasia API Key',
                      hintText: 'miku_retail_secret_key_2026',
                      prefixIcon: Icon(Icons.key, color: MikuTheme.teal),
                    ),
                  ),
                  const SizedBox(height: 20),

                  if (_connectionStatus != null)
                    Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _connectionOk ? const Color(0xFFE8F8F7) : const Color(0xFFFFECEF),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: _connectionOk ? MikuTheme.teal : MikuTheme.pink),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            _connectionOk ? Icons.check_circle : Icons.error_outline,
                            color: _connectionOk ? MikuTheme.darkTeal : MikuTheme.pink,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              _connectionStatus!,
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: _connectionOk ? MikuTheme.darkTeal : Colors.red.shade900,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: MikuTheme.teal,
                    ),
                    onPressed: _isTesting ? null : _saveAndTest,
                    icon: _isTesting
                        ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Icon(Icons.save_alt),
                    label: Text(
                      _isTesting ? 'Mengecek Koneksi Server...' : 'Tes Koneksi & Simpan Pengaturan',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
