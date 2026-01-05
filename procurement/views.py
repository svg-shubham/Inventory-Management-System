from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response # Fixed
from rest_framework import viewsets, permissions
from django.utils import timezone # Fixed
from .models import PurchaseRequest
from .serializers import PurchaseRequestSerializer
from users.utils import send_smart_notification 
from users.models import User

class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all().prefetch_related('items')
    serializer_class = PurchaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        pr = serializer.save()
        procurement_users = User.objects.filter(role='procurement', is_active=True)
        for officer in procurement_users:
            send_smart_notification(
                recipient=officer,
                n_type='PR_APPROVAL',
                title='New PR Pending Approval',
                message=f'A new Purchase Request {pr.pr_number} has been created by {self.request.user.username}.',
                slug=f"pr-approval-{pr.id}",
                priority='high',
                action_url=f"/procurement/pr/{pr.id}/"
            )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        pr = self.get_object()
        if request.user.role not in ['admin', 'procurement_head']:
            return Response({"error": "You don't have permission to approve"}, status=403)
        pr.status = 'approved'
        pr.approved_by = request.user
        pr.approved_at = timezone.now()
        pr.save()
        send_smart_notification(
            recipient=pr.requested_by,
            n_type='PR_STATUS',
            title='PR Approved!',
            message=f'Your request {pr.pr_number} has been approved by {request.user.username}.',
            slug=f"pr-approved-{pr.id}",
            priority='medium'
        )
        return Response({"status": "Purchase Request Approved"})
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        pr = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        pr.status = 'rejected'
        pr.rejection_reason = reason
        pr.save()
        send_smart_notification(
            recipient=pr.requested_by,
            n_type='PR_STATUS',
            title='PR Rejected',
            message=f'Your request {pr.pr_number} was rejected. Reason: {reason}',
            slug=f"pr-rejected-{pr.id}",
            priority='high'
        )
        return Response({"status": "Purchase Request Rejected"})