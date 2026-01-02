from rest_framework import serializers
from orders.models import PurchaseOrder,SalesOrder

class PurchaseOrderSerializer(serializers.ModelSerializer):
  vendor_name = serializers.ReadOnlyField(source = "vendor.get_full_name")
  product_name = serializers.ReadOnlyField(source = "product.name")
  warehouse_name = serializers.ReadOnlyField(source = "warehouse.name")
  total_amount = serializers.SerializerMethodField()

  class Meta:
    model = PurchaseOrder
    fields = [
      'order_id', 'vendor', 'vendor_name', 'product', 'product_name',
      'warehouse', 'warehouse_name', 'quantity', 'cost_price', 
      'total_amount', 'due_date', 'penalty_rate_month', 
      'order_date', 'status'
    ]
    read_only_fields = ['order_date','order_id']


  def __init__(self, *args, **kwargs):
    super(PurchaseOrderSerializer, self).__init__(*args, **kwargs)
    request = self.context.get('request')
    if request and request.method == 'PATCH':
      for field_name, field in self.fields.items():
        if field_name != 'status':
          field.read_only = True


  def get_total_amount(self,obj):
    return obj.quantity * obj.cost_price
  
  def validate_due_date(self,value):
    from django.utils import timezone
    if value< timezone.now().date():
      raise serializers.ValidationError("you cant give due date less than today")
    return value


class SalseOrderSerializer(serializers.ModelSerializer):
  customer_name = serializers.ReadOnlyField(source = 'customer.get_full_name')
  product_name = serializers.ReadOnlyField(source = "product.name")
  warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
  total_revenue = serializers.SerializerMethodField()
  class Meta:
    model = SalesOrder
    fields = [
        'order_id', 'customer', 'customer_name', 'product', 'product_name',
        'warehouse', 'warehouse_name', 'quantity', 'sell_price', 
        'total_revenue', 'due_date', 'penalty_rate_month', 
        'order_date', 'status'
    ]
    read_only_fields = ['order_id', 'order_date']
  
  def validate(self, data):
        """
        Check karega ki Delivery ke waqt stock available hai ya nahi.
        """
        # data.get() isliye use kar rahe hain kyunki PATCH mein shayad 
        # product ya warehouse na bheja jaye, toh hum instance (purana data) use karenge
        product = data.get('product', getattr(self.instance, 'product', None))
        warehouse = data.get('warehouse', getattr(self.instance, 'warehouse', None))
        quantity = data.get('quantity', getattr(self.instance, 'quantity', 0))
        status_val = data.get('status', getattr(self.instance, 'status', None))

        # Agar status 'delivered' set kiya ja raha hai
        if status_val == 'delivered':
            from inventory.models import Stock
            stock = Stock.objects.filter(product=product, warehouse=warehouse).first()
            
            # Stock check logic
            available_qty = stock.quantity if stock else 0
            
            # Agar update ho raha hai (PUT/PATCH), toh purani quantity ko temporary add back karke check karo
            if self.instance and self.instance.status == 'delivered':
                available_qty += self.instance.quantity

            if available_qty < quantity:
                raise serializers.ValidationError({
                    "quantity": f"Stock khatam! Warehouse mein sirf {available_qty} units bache hain."
                })
        
        return data

  def get_total_revenue(self, obj):
      return obj.quantity * obj.sell_price
