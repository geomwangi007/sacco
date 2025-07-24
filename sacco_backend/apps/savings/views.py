# apps/savings/views.py
from decimal import Decimal

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.savings.models import SavingsAccount, SavingsTransaction, InterestRate
from apps.savings.serializers import SavingsAccountSerializer, SavingsTransactionSerializer, InterestRateSerializer
from apps.savings.services.transaction_service import SavingsTransactionService
from apps.savings.services.account_service import SavingsAccountService


class SavingsAccountViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role.name in ['STAFF', 'ADMIN']:
            return SavingsAccount.objects.all()
        return SavingsAccount.objects.filter(member__user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            # Use account service for proper account opening workflow
            account_data = request.data.copy()
            account = SavingsAccountService.create_account(
                member_id=account_data.get('member'),
                account_type=account_data.get('account_type'),
                initial_deposit=Decimal(account_data.get('initial_deposit', '0'))
            )
            return Response(
                SavingsAccountSerializer(account).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        account = self.get_object()
        amount = Decimal(request.data.get('amount', '0'))
        description = request.data.get('description', '')

        if amount <= 0:
            return Response({'error': 'Amount must be greater than 0'}, status=400)

        try:
            transaction = SavingsTransactionService.process_transaction(
                account.id,
                'DEPOSIT',
                amount,
                description=description
            )
            return Response(SavingsTransactionSerializer(transaction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        account = self.get_object()
        amount = Decimal(request.data.get('amount', '0'))
        description = request.data.get('description', '')

        if amount <= 0:
            return Response({'error': 'Amount must be greater than 0'}, status=400)

        try:
            transaction = SavingsTransactionService.process_transaction(
                account.id,
                'WITHDRAWAL',
                amount,
                description=description
            )
            return Response(SavingsTransactionSerializer(transaction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        account = self.get_object()
        return Response({
            'account_number': account.account_number,
            'balance': account.balance,
            'minimum_balance': account.minimum_balance,
            'status': account.status
        })

    @action(detail=True, methods=['get'])
    def statement(self, request, pk=None):
        account = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        transactions = SavingsTransaction.objects.filter(account=account)
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
            
        return Response({
            'account': SavingsAccountSerializer(account).data,
            'transactions': SavingsTransactionSerializer(transactions.order_by('-date'), many=True).data
        })

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        account = self.get_object()
        reason = request.data.get('reason', 'Administrative action')
        
        try:
            SavingsAccountService.freeze_account(account.id, reason)
            account.refresh_from_db()
            return Response({
                'status': 'Account frozen',
                'account_status': account.status
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def unfreeze(self, request, pk=None):
        account = self.get_object()
        
        try:
            SavingsAccountService.unfreeze_account(account.id)
            account.refresh_from_db()
            return Response({
                'status': 'Account unfrozen',
                'account_status': account.status
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        account = self.get_object()
        reason = request.data.get('reason', 'Member request')
        
        try:
            SavingsAccountService.close_account(account.id, reason)
            account.refresh_from_db()
            return Response({
                'status': 'Account closed',
                'final_balance': account.balance
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=400)


class SavingsTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SavingsTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role.name in ['STAFF', 'ADMIN']:
            return SavingsTransaction.objects.all()
        return SavingsTransaction.objects.filter(
            account__member__user=self.request.user
        )


class InterestRateViewSet(viewsets.ModelViewSet):
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only staff and admin can manage interest rates
        if self.request.user.role.name not in ['STAFF', 'ADMIN']:
            # Regular users can only view current rates
            return InterestRate.objects.filter(
                effective_date__lte=timezone.now().date()
            ).order_by('account_type', '-effective_date')
        return InterestRate.objects.all()

