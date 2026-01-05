from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics,viewsets, filters,status
from django_filters.rest_framework import DjangoFilterBackend
from inventory.models import Warehouse,Product,Stock
from inventory.serilizers import WerehouseSerializer,ProductSerializer,StockSerializer
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from users.permissions import IsSystemAdmin, IsInventoryManager

from rest_framework.decorators import action
from django.db import models  
from django.db.models import F

# Create your views here.

class WarehouseListCreateAPIView(generics.ListCreateAPIView):
  queryset = Warehouse.objects.all()
  serializer_class = WerehouseSerializer
  def get_permissions(self):
    if self.request.method == 'POST':
        return [(IsSystemAdmin | IsInventoryManager)()]
    return [IsAuthenticated()]

class WarehouseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
  queryset = Warehouse.objects.all()
  serializer_class = WerehouseSerializer
  lookup_field = "warehouse_id"
  def get_permissions(self):
    if self.request.method in ['PUT', 'PATCH', 'DELETE']:
        return [(IsSystemAdmin | IsInventoryManager)()]
    return [IsAuthenticated()]

# industry-level API banane ke liye hum ModelViewSet ka use karenge. Industry mein ViewSet isliye pasand kiya jata hai kyunki ye ek hi class mein GET (list/detail), POST, PUT, PATCH, aur DELETE sab handle kar leta hai.
class ProductViewSet(viewsets.ModelViewSet):
  """
    - Automatic CRUD operations
    - Search by name or SKU
    - Filter by category or vendor
    - Ordering by created_at
    """
  queryset = Product.objects.all().order_by('-created_at')
  serializer_class = ProductSerializer
  # Permissions: Sab dekh sakte hain, par change sirf logged-in user kar sakta hai
  # permission_classes = [IsAuthenticatedOrReadOnly]
  # pr abhi ke liye allowany ka hi use karenge
  permission_classes = [AllowAny]

  # fetures for filtering and searching
  filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
  filterset_fields = ['category', 'vendor']

  search_fields = ['name','sku']

  ordering_fields = ['created_at','name']


class StockViewset(viewsets.ModelViewSet):
  queryset = Stock.objects.all().select_related('product',"warehouse")
  serializer_class = StockSerializer
  filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]

  filterset_fields = ['warehouse','product']
  search_fields = ['product__name','product__sku','warehouse__name']
  ordering_fields = ['quantity','min_stock_level']
  permission_classes = [AllowAny]


  # --- Custom Action: Low Stock report ke liye ---
  # URL: /inventory/stocks/low_stock/
  @action(detail=False, methods=['get'])
  def low_stock(self,request):
    low_stock_items = self.queryset.filter(quantity__lte=models.F('min_stock_level'))
    serializer = self.get_serializer(low_stock_items,many=True)
    return Response(serializer.data)
  # --- Custom Action: Quick Quantity Update ---
  # URL: /inventory/stocks/{id}/add_stock/

  @action(detail=True,methods=['post'])
  def add_stock(self,request,pk=None):
    stock = self.get_object()
    added_qty = request.data.get('added_quantity', 0)
    try:
      stock.quantity += int(added_qty) 
      stock.save()
      return Response({'status': 'Stock updated', 'new_quantity': stock.quantity})
    except ValueError:
      return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)


