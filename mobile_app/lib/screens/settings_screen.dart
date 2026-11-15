import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:fluttertoast/fluttertoast.dart';
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

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  void _loadSettings() async {
    final url = await ApiService.getServerUrl();
    final key = await ApiService.getApiKey();
    setState(() {
      _urlCtrl.text = url;
      _keyCtrl.text = key;
      _isLoading = false;
    });
  }

  void _save() async {
    final url = _urlCtrl.text.trim();
    final key = _keyCtrl.text.trim();

    if (url.isEmpty || key.isEmpty) {
      Fluttertoast.showToast(msg: "Alamat server & API Key tidak boleh kosong!");
      return;
    }

    await ApiService.saveSettings(url, key);
    Fluttertoast.showToast(
      msg: "Pengaturan berhasil disimpan!",
      backgroundColor: MikuTheme.teal,
      textColor: Colors.white,
    );
    if (mounted) Navigator.pop(context);
  }

  void _scanSetupQr() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (ctx) => Scaffold(
          appBar: AppBar(title: const Text('Scan QR Setup Server')),
          body: MobileScanner(
            onDetect: (capture) {
              final barcodes = capture.barcodes;
              if (barcodes.isNotEmpty && barcodes.first.rawValue != null) {
                final raw = barcodes.first.rawValue!;
                try {
                  final data = jsonDecode(raw);
                  if (data['server_url'] != null && data['api_key'] != null) {
                    setState(() {
                      _urlCtrl.text = data['server_url'];
                      _keyCtrl.text = data['api_key'];
                    });
                    Navigator.pop(ctx);
                    Fluttertoast.showToast(
                      msg: "Pengaturan QR berhasil dibaca!",
                      backgroundColor: MikuTheme.teal,
                    );
                  }
                } catch (e) {
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
                  const SizedBox(height: 28),

                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: MikuTheme.teal,
                    ),
                    onPressed: _save,
                    child: const Text('Simpan Pengaturan', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  ),
                ],
              ),
            ),
    );
  }
}
