from django.shortcuts import render
from rest_framework import viewsets
from finance.models import Transaction,PaymentLog
from finance.serializers import TransactionSerializer,PaymentLogSerializer
from rest_framework.permissions import AllowAny

# Create your views here.
class TransactionViewset(viewsets.ReadOnlyModelViewSet):
  queryset = Transaction.objects.all().prefetch_related('payment_logs')
  serializer_class = TransactionSerializer
  permission_classes = [AllowAny]

class PaymentLogViewset(viewsets.ModelViewSet):
  queryset = PaymentLog.objects.all()
  serializer_class = PaymentLogSerializer
  permission_classes = [AllowAny]