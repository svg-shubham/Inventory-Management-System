from rest_framework import serializers
from finance.models import Transaction,PaymentLog

class PaymentLogSerializer(serializers.ModelSerializer):
  class Meta:
    model = PaymentLog
    fields = ['log_id', 'transaction', 'amount_paid', 'payment_mode', 'reference_number', 'payment_date', 'remarks']

class TransactionSerializer(serializers.ModelSerializer):
  payment_logs = PaymentLogSerializer(many=True,read_only = True)
  class Meta:
    model = Transaction
    fields = [
      'transaction_id', 'purchase_order', 'sales_order', 
      'total_amount', 'penalty_amount', 'paid_amount_cache', 
      'balance_amount', 'status', 'updated_at', 'payment_logs'
    ]
    read_only_fields = ['total_amount', 'paid_amount_cache', 'balance_amount', 'status']

