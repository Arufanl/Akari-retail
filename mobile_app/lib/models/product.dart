class ProductItem {
  final String plu;
  final String barcode;
  final String name;
  final String shortName;
  final String size;
  final String imageUrl;
  final String labelUrl;

  ProductItem({
    required this.plu,
    required this.barcode,
    required this.name,
    this.shortName = '',
    this.size = '',
    this.imageUrl = '',
    this.labelUrl = '',
  });

  factory ProductItem.fromJson(Map<String, dynamic> json) {
    return ProductItem(
      plu: json['plu']?.toString() ?? '',
      barcode: json['barcode']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      shortName: json['short_name']?.toString() ?? '',
      size: json['size']?.toString() ?? '',
      imageUrl: json['image_url']?.toString() ?? '',
      labelUrl: json['label_url']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'plu': plu,
      'barcode': barcode,
      'name': name,
      'short_name': shortName,
      'size': size,
    };
  }
}
