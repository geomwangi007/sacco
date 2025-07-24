from decimal import Decimal

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.transactions.models import Transaction, TransactionFee, TransactionLimit
from apps.transactions.serializers import (
    TransactionSerializer, 
    TransactionFeeSerializer, 
    TransactionLimitSerializer,
    TransferSerializer
)
from apps.transactions.services.transaction_service import TransactionService


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role.name in ['STAFF', 'ADMIN']:
            queryset = Transaction.objects.all()
        else:
            queryset = Transaction.objects.filter(member__user=self.request.user)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Add request user context
        transaction_data = serializer.validated_data.copy()
        transaction_data['initiated_by'] = request.user

        try:
            transaction = TransactionService.create_transaction(**transaction_data)
            return Response(
                TransactionSerializer(transaction).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pending transaction."""
        transaction = self.get_object()
        
        if transaction.status != 'PENDING':
            return Response(
                {'error': 'Only pending transactions can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            approved_transaction = TransactionService.approve_transaction(transaction.id, request.user)
            return Response(TransactionSerializer(approved_transaction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending transaction."""
        transaction = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        
        if transaction.status != 'PENDING':
            return Response(
                {'error': 'Only pending transactions can be rejected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rejected_transaction = TransactionService.reject_transaction(transaction.id, reason, request.user)
            return Response(TransactionSerializer(rejected_transaction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reverse(self, request, pk=None):
        """Reverse a completed transaction."""
        transaction = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        
        if transaction.status != 'COMPLETED':
            return Response(
                {'error': 'Only completed transactions can be reversed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reversed_transaction = TransactionService.reverse_transaction(transaction.id, reason, request.user)
            return Response(TransactionSerializer(reversed_transaction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """Process inter-member transfer."""
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            transfer_data = serializer.validated_data
            transfer_data['initiated_by'] = request.user
            
            transactions = TransactionService.process_transfer(**transfer_data)
            return Response({
                'debit_transaction': TransactionSerializer(transactions['debit']).data,
                'credit_transaction': TransactionSerializer(transactions['credit']).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def limits(self, request):
        """Get transaction limits for current user."""
        try:
            limits = TransactionService.get_user_limits(request.user)
            return Response(limits)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary for current user."""
        try:
            summary = TransactionService.get_transaction_summary(
                request.user,
                start_date=request.query_params.get('start_date'),
                end_date=request.query_params.get('end_date')
            )
            return Response(summary)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionFeeViewSet(viewsets.ModelViewSet):
    queryset = TransactionFee.objects.all()
    serializer_class = TransactionFeeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only staff and admin can manage fees
        if self.request.user.role.name not in ['STAFF', 'ADMIN']:
            return TransactionFee.objects.none()
        return TransactionFee.objects.all()


class TransactionLimitViewSet(viewsets.ModelViewSet):
    queryset = TransactionLimit.objects.all()
    serializer_class = TransactionLimitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only staff and admin can manage limits
        if self.request.user.role.name not in ['STAFF', 'ADMIN']:
            return TransactionLimit.objects.none()
        return TransactionLimit.objects.all()