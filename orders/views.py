from django.shortcuts import render
from rest_framework import viewsets,filters,status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import PurchaseOrder,SalesOrder
from .serializers import PurchaseOrderSerializer,SalseOrderSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly

# Create your views here.

class PurchaseOrderViewSet(viewsets.ModelViewSet):
  queryset = PurchaseOrder.objects.all().select_related('vendor', 'product', 'warehouse')
  serializer_class = PurchaseOrderSerializer
  permission_classes = [AllowAny]
  
  # filtering operations
  filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
  filterset_fields = ['status', 'vendor', 'warehouse']
  search_fields = ['order_id', 'product__name','vender__name']
  ordering_fields = ['order_date','due_date','cost_price']
  http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options'] # we can not all put method in that situation or agar cancel karna hoga toh cancel kare or phirse bananeka 

  # Custom Action: Sirf Pending Orders dekhne ke liye kabhi kabhi ad karna ke liye check karna padega
  # URL: /orders/purchase-orders/pending_orders/
  @action(detail=False,methods=['get'])
  def pending_orders(self,request):
    pending_ord = self.queryset.filter(status="pending")
    serializer = self.get_serializer(pending_ord,many=True)
    return Response(serializer.data)
  
  # Custom Action: Order Cancel karne ke liye (Safety Check ke saath) agar kabhi order gaya or aya nahi tab
  @action(detail=True,methods=['post'])
  def cancel_order(self, request, pk=None):
    order = self.get_object() # Ye database se order uthayega
    
    # GALAT: if order_status == 'received':
    # SAHI: Niche wali line dekhein
    if order.status == 'received':
        return Response(
            {"error": "Received orders cannot be cancelled!"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    order.status = 'cancelled'
    order.save() # Is save() se signals bhi trigger honge
    return Response({"status": f"Order {pk} cancelled successfully"})

class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all().select_related('customer', 'product', 'warehouse')
    serializer_class = SalseOrderSerializer
    permission_classes = [AllowAny]
    
    # Industry Security: PUT ban, sirf PATCH allow
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=True, methods=['post'])
    def mark_as_delivered(self, request, pk=None):
        """Custom action to mark order as delivered"""
        order = self.get_object()
        if order.status == 'delivered':
            return Response({"error": "Order already delivered!"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation serializer ke through hi hogi save() pe
        order.status = 'delivered'
        order.save()
        return Response({"status": "Order delivered and stock updated!"})

    @action(detail=True, methods=['post'])
    def return_order(self, request, pk=None):
        """Custom action for customer returns"""
        order = self.get_object()
        if order.status != 'delivered':
            return Response({"error": "Only delivered orders can be returned!"}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'returned'
        order.save()
        return Response({"status": "Order returned and stock added back!"})