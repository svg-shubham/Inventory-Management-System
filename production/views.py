from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import ProductionBatch, ProductionOutput
from inventory.models import Stock
from .serializers import ProductionBatchSerializer
from users.permissions import IsSystemAdmin,IsInventoryManager

class ProductionViewSet(viewsets.ModelViewSet):
    queryset = ProductionBatch.objects.all().order_by('-issued_at')
    serializer_class = ProductionBatchSerializer
    permission_classes = [IsSystemAdmin | IsInventoryManager]

    def perform_create(self, serializer):
        """STEP 1: Batch Issue karte waqt Raw Material Stock se nikalna"""
        with transaction.atomic():
            raw_material_id = self.request.data.get('raw_material')
            warehouse_id = self.request.data.get('warehouse')
            qty_to_issue = int(self.request.data.get('issued_quantity', 0))

            try:
                # Lock the stock row until transaction completes
                stock_item = Stock.objects.select_for_update().get(
                    product_id=raw_material_id, 
                    warehouse_id=warehouse_id
                )
            except Stock.DoesNotExist:
                raise serializers.ValidationError({"error": "Inventory mein ye raw material nahi mila!"})

            if stock_item.quantity < qty_to_issue:
                raise serializers.ValidationError({
                    "error": f"Stock kam hai! Available sirf {stock_item.quantity} hai."
                })

            # Raw Material kam karein
            stock_item.quantity -= qty_to_issue
            stock_item.save()

            # Batch record save karein
            serializer.save(issued_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        """STEP 2: Batch Complete karte waqt Finished Goods Stock mein add karna"""
        batch = self.get_object()
        
        if batch.status != 'issued':
            return Response({"error": "Ye batch pehle hi band ho chuka hai!"}, status=status.HTTP_400_BAD_REQUEST)
        
        outputs_data = request.data.get('outputs', [])
        if not outputs_data:
            return Response({"error": "Kam se kam ek output record zaruri hai!"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            total_pw = Decimal('0.00') 
            total_sw = Decimal('0.00')

            for item in outputs_data:
                # 1. Output Record banayein
                out_obj = ProductionOutput.objects.create(
                    batch=batch,
                    product_id=item['product'],
                    quantity=item['quantity'],
                    weight=Decimal(str(item['weight'])), 
                    is_scrap=item.get('is_scrap', False)
                )

                # 2. FINISHED GOODS STOCK UPDATE
                # Warehouse wahi rahega jo batch issue ke waqt tha
                finished_stock, created = Stock.objects.get_or_create(
                    product_id=item['product'],
                    warehouse=batch.warehouse,
                    defaults={'quantity': 0}
                )
                finished_stock.quantity += int(item['quantity'])
                finished_stock.save()

                # 3. Weights total karein calculation ke liye
                if out_obj.is_scrap:
                    total_sw += out_obj.weight
                else:
                    total_pw += out_obj.weight

            # Final Batch Updates
            batch.total_produced_weight = total_pw
            batch.total_scrap_weight = total_sw
            batch.process_loss = batch.issued_weight - (total_pw + total_sw)
            batch.status = 'completed'
            batch.completed_at = timezone.now()
            batch.save()
            
            return Response({
                "status": "Success", 
                "process_loss": str(batch.process_loss),
                "message": "Finished goods stock mein add ho gaye hain."
            })