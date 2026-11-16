import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/product.dart';

class ApiService {
  static const String defaultServerUrl = "http://192.168.1.2:5000";
  static const String defaultApiKey = "miku_retail_secret_key_2026";

  static Future<String> getServerUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('server_url') ?? defaultServerUrl;
  }

  static Future<String> getApiKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('api_key') ?? defaultApiKey;
  }

  static Future<void> saveSettings(String serverUrl, String apiKey) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('server_url', serverUrl.trim().replaceAll(RegExp(r'/+$'), ''));
    await prefs.setString('api_key', apiKey.trim());
  }

  static Future<Map<String, dynamic>> testConnection({String? overrideUrl, String? overrideKey}) async {
    final baseUrl = (overrideUrl ?? await getServerUrl()).trim().replaceAll(RegExp(r'/+$'), '');
    final apiKey = (overrideKey ?? await getApiKey()).trim();
    final uri = Uri.parse('$baseUrl/api/config/info');

    final response = await http.get(
      uri,
      headers: {'X-API-Key': apiKey},
    ).timeout(const Duration(seconds: 6));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  static Future<Map<String, dynamic>> lookupProduct(String code) async {
    final baseUrl = await getServerUrl();
    final apiKey = await getApiKey();
    final uri = Uri.parse('$baseUrl/api/product/lookup?code=${Uri.encodeComponent(code)}');

    final response = await http.get(
      uri,
      headers: {'X-API-Key': apiKey},
    ).timeout(const Duration(seconds: 8));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Server Error: ${response.statusCode} - ${response.body}');
    }
  }

  static Future<List<ProductItem>> searchProducts(String query, {int limit = 20}) async {
    final baseUrl = await getServerUrl();
    final key = await getApiKey();
    final uri = Uri.parse('$baseUrl/api/product/search?q=${Uri.encodeComponent(query)}&limit=$limit');

    final response = await http.get(
      uri,
      headers: {'X-API-Key': key},
    ).timeout(const Duration(seconds: 8));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = (data['results'] as List?) ?? [];
      return list.map((item) => ProductItem.fromJson(item)).toList();
    } else {
      throw Exception('Search failed: ${response.statusCode}');
    }
  }

  static Future<Map<String, dynamic>> saveProduct({
    required String plu,
    required String barcode,
    String? name,
    String? shortName,
    String? size,
  }) async {
    final baseUrl = await getServerUrl();
    final apiKey = await getApiKey();
    final uri = Uri.parse('$baseUrl/api/product/save');

    final payload = {
      'plu': plu.trim(),
      'barcode': barcode.trim(),
      if (name != null && name.isNotEmpty) 'name': name.trim(),
      if (shortName != null && shortName.isNotEmpty) 'short_name': shortName.trim(),
      if (size != null && size.isNotEmpty) 'size': size.trim(),
    };

    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Gagal menyimpan: ${response.body}');
    }
  }

  static Future<Uint8List> fetchLabelBytes(String code) async {
    final baseUrl = await getServerUrl();
    final uri = Uri.parse('$baseUrl/api/product/label/$code');

    final response = await http.get(uri).timeout(const Duration(seconds: 12));
    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception('Gagal mengunduh gambar label');
    }
  }
}
