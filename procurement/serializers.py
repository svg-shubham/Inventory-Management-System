from rest_framework import serializers
from .models import PurchaseRequest, PRItem

class PRItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name') # Frontend ki help ke liye

    class Meta:
        model = PRItem
        fields = ['product', 'product_name', 'specification', 'requested_quantity', 'uom', 'estimated_price', 'pending_quantity']

class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PRItemSerializer(many=True) # Nested items
    requested_by_name = serializers.ReadOnlyField(source='requested_by.username')

    class Meta:
        model = PurchaseRequest
        fields = ['id', 'pr_number', 'requested_by', 'requested_by_name', 'priority', 'status', 'description', 'required_by_date', 'items', 'created_at']
        read_only_fields = ['pr_number', 'requested_by', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # Logged in user ko requested_by mein set karna
        request = self.context.get('request')
        pr = PurchaseRequest.objects.create(requested_by=request.user, **validated_data)
        
        for item_data in items_data:
            PRItem.objects.create(pr=pr, **item_data)
        return pr