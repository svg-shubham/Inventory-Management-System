from rest_framework import serializers
from .models import ProductionBatch,ProductionOutput


class ProductionOutputSerializer(serializers.ModelSerializer):
  class Meta:
    model = ProductionOutput
    fields = [
      'product', 'quantity', 'weight', 'is_scrap'
    ]

class ProductionBatchSerializer(serializers.ModelSerializer):
  output = ProductionOutputSerializer(many=True,read_only = True)
  class Meta:
    model = ProductionBatch
    fields = '__all__'
    read_only_fields = ['batch_id', 'issued_by', 'status', 'process_loss', 'total_produced_weight', 'total_scrap_weight']
  def validate(self, data):
    user = self.context['request'].user
    if ProductionBatch.objects.filter(issued_by=user, status='issued').exists():
        raise serializers.ValidationError("Bhai, pehle purana batch complete karo tabhi naya bundle milega!")
    return data