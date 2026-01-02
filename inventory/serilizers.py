from rest_framework import serializers
from inventory.models import (Warehouse,Product,Stock)


class WerehouseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Warehouse
    fields = [
      "warehouse_id",
      "name",
      "location",
      "created_at"
    ]

class ProductSerializer(serializers.ModelSerializer):
  vendor_name = serializers.ReadOnlyField(source='vendor.username')
  class Meta:
    model = Product
    fields = [
            'product_id', 
            'name', 
            'sku', 
            'vendor', 
            'vendor_name', # Extra field for UI
            'category', 
            'description', 
            'created_at'
    ]
  read_only_fields = ['sku', 'created_at']

  def validate_name(self, value):
        # Example validation: Name 3 characters se bada hona chahiye
        if len(value) < 3:
            raise serializers.ValidationError("Product name bahut chota hai!")
        return value
  

class StockSerializer(serializers.ModelSerializer):
  product_name = serializers.ReadOnlyField(source = "Product.name")
  warehouse_name = serializers.ReadOnlyField(source = "warehouse.name")
  sku = serializers.ReadOnlyField(source = 'product.sku')

  # 1. Ye line model class ke bahar se data fetch karti hai
  is_low_stock = serializers.SerializerMethodField()
  class Meta:
    model = Stock
    fields = [
        'id', 'warehouse', 'warehouse_name', 'product', 
          'product_name', 'sku', 'quantity', 
          'min_stock_level', 'is_low_stock'
      ]
  def get_is_low_stock(self, obj):
    return obj.quantity <= obj.min_stock_level

  # Validation: Stock kabhi negative nahi ho sakta
  def validate_quantity(self, value):
      if value < 0:
          raise serializers.ValidationError("Quantity zero se kam nahi ho sakti.")
      return value