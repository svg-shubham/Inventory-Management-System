from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'batches', ProductionViewSet, basename='production-batch')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # Ye saare endpoints automatically handle karega:
    # POST /batches/ -> Subah ka Issue
    # GET /batches/ -> Saari History
    # GET /batches/<id>/ -> Ek batch ki detail
    # PATCH /batches/<id>/complete/ -> Shaam ka Comple
]