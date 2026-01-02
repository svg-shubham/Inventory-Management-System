from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

# viewset ke urls ko hamesha router ke sath use karna hota hain taki id lena a urls ko manage nahi karna padta hain isliye router

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename= "Product")
router.register(r'stocks', StockViewset, basename='stock')


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('warehouse/',WarehouseListCreateAPIView.as_view(),name='warehouse-list-create'),
    path('warehouse/<int:warehouse_id>', WarehouseRetrieveUpdateDestroyAPIView.as_view(),name="warehouse-detail-update")
]


