import 'package:flutter/material.dart';
import '../theme/miku_theme.dart';
import '../services/api_service.dart';
import '../models/product.dart';
import 'product_form_screen.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _searchCtrl = TextEditingController();
  List<ProductItem> _results = [];
  bool _isLoading = false;
  String _message = 'Ketik nama barang (misal: Indomie, Aqua, Silverqueen)';

  void _performSearch(String query) async {
    final q = query.trim();
    if (q.isEmpty) return;

    setState(() {
      _isLoading = true;
      _message = '';
    });

    try {
      final list = await ApiService.searchProducts(q);
      setState(() {
        _results = list;
        _isLoading = false;
        if (list.isEmpty) {
          _message = 'Tidak ada produk ditemukan untuk "$q"';
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _message = 'Gagal mencari: $e';
      });
    }
  }

  void _onSelectProduct(ProductItem item) async {
    // Look up this product by barcode to check if PLU exists
    try {
      final res = await ApiService.lookupProduct(item.barcode);
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ProductFormScreen(
            scannedCode: item.barcode,
            lookupResult: res,
          ),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.redAccent),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7FCFB),
      appBar: AppBar(
        title: const Text('Cari Database 50.600', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: Column(
        children: [
          // Search Box
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: TextField(
              controller: _searchCtrl,
              autofocus: true,
              textInputAction: TextInputAction.search,
              onSubmitted: _performSearch,
              decoration: InputDecoration(
                hintText: 'Cari nama produk...',
                prefixIcon: const Icon(Icons.search, color: MikuTheme.teal),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.arrow_forward, color: MikuTheme.teal),
                  onPressed: () => _performSearch(_searchCtrl.text),
                ),
              ),
            ),
          ),

          // Results Area
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: MikuTheme.teal))
                : _results.isEmpty
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Text(_message, textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(16),
                        itemCount: _results.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final item = _results[index];
                          return Container(
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: MikuTheme.borderTeal),
                              boxShadow: [
                                BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 6),
                              ],
                            ),
                            child: ListTile(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                              leading: Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: MikuTheme.lightTeal,
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Icon(Icons.inventory_2_outlined, color: MikuTheme.darkTeal, size: 20),
                              ),
                              title: Text(
                                item.name,
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                              ),
                              subtitle: Text(
                                'Barcode: ${item.barcode} ${item.size.isNotEmpty ? "• ${item.size}" : ""}',
                                style: const TextStyle(fontSize: 11, color: MikuTheme.darkTeal, fontFamily: 'monospace'),
                              ),
                              trailing: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: MikuTheme.lightTeal,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: MikuTheme.teal.withOpacity(0.4)),
                                ),
                                child: const Text('Pilih →', style: TextStyle(color: MikuTheme.darkTeal, fontWeight: FontWeight.bold, fontSize: 11)),
                              ),
                              onTap: () => _onSelectProduct(item),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
