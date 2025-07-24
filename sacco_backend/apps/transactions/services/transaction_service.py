from decimal import Decimal

from django.db import transaction
from datetime import datetime
import uuid

from django.utils import timezone

from shared.services.ledger_service import LedgerService
from .fees_calculator import FeesCalculator
from ..models import Transaction, TransactionFee, TransactionLimit

from ...members.models import Member
from ...notifications.services.notification_service import NotificationService


class TransactionService:
    @staticmethod
    @transaction.atomic
    def create_transaction(
            member_id: int,
            transaction_type: str,
            amount: Decimal,
            payment_method: str,
            **kwargs
    ) -> Transaction:
        # Validate transaction limits
        TransactionService._validate_limits(member_id, transaction_type, amount)

        # Calculate fees
        fee = TransactionService._calculate_fee(transaction_type, payment_method, amount)

        # Create transaction
        _transaction = Transaction.objects.create(
            transaction_ref=TransactionService._generate_reference(),
            member_id=member_id,
            transaction_type=transaction_type,
            amount=amount,
            payment_method=payment_method,
            # fee_amount=fee,
            **kwargs
        )

        # Process based on type
        if transaction_type == 'DEPOSIT':
            TransactionService._process_deposit(_transaction)
        elif transaction_type == 'WITHDRAWAL':
            TransactionService._process_withdrawal(_transaction)

        NotificationService.send_transaction_notification(_transaction)
        return _transaction

    @staticmethod
    def _generate_reference() -> str:
        return f"TXN{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def _validate_limits(member_id: int, transaction_type: str, amount: Decimal):
        member = Member.objects.get(id=member_id)
        limits = TransactionLimit.objects.filter(
            transaction_type=transaction_type,
            member_type=member.membership_type
        )

        for limit in limits:
            if limit.limit_type == 'SINGLE' and amount > limit.amount:
                raise ValueError(f"Amount exceeds single transaction limit of {limit.amount}")
            # Add other limit validations

    @staticmethod
    def _calculate_fee(transaction_type: str, payment_method: str, amount: Decimal) -> Decimal:
        try:
            fee_structure = TransactionFee.objects.get(
                transaction_type=transaction_type,
                payment_method=payment_method
            )

            percentage_fee = amount * (fee_structure.percentage / 100)
            total_fee = fee_structure.fixed_amount + percentage_fee

            if fee_structure.max_amount:
                total_fee = min(total_fee, fee_structure.max_amount)

            return max(total_fee, fee_structure.min_amount)
        except TransactionFee.DoesNotExist:
            return Decimal('0')

    @staticmethod
    def _process_deposit(_transaction: Transaction) -> Transaction:
        try:
            with transaction.atomic():
                # Calculate fees
                fee = FeesCalculator.calculate_deposit_fee(
                    _transaction.amount,
                    _transaction.payment_method,
                    _transaction.member.membership_type
                )

                # Update savings account
                savings_account = _transaction.member.savings_account
                savings_account.balance += (_transaction.amount - fee)
                savings_account.save()

                # Record fee transaction if applicable
                if fee > 0:
                    Transaction.objects.create(
                        transaction_ref=f"FEE-{_transaction.transaction_ref}",
                        member=_transaction.member,
                        transaction_type='FEE',
                        amount=fee,
                        payment_method='INTERNAL',
                        status='COMPLETED',
                        description=f"Fee for deposit {_transaction.transaction_ref}",
                        source_account=_transaction.source_account
                    )

                # Update transaction status
                _transaction.status = 'COMPLETED'
                _transaction.processed_date = timezone.now()
                _transaction.save()

                # Create ledger entries
                LedgerService.create_deposit_entries(_transaction, fee)

                return _transaction

        except Exception as e:
            _transaction.status = 'FAILED'
            _transaction.description = f"Failed: {str(e)}"
            _transaction.save()
            raise

    @staticmethod
    def _process_withdrawal(_transaction: Transaction) -> Transaction:
        try:
            with transaction.atomic():
                # Calculate fees
                fee = FeesCalculator.calculate_withdrawal_fee(
                    _transaction.amount,
                    _transaction.payment_method,
                    _transaction.member.membership_type
                )

                total_deduction = _transaction.amount + fee
                savings_account = _transaction.member.savings_account

                # Check balance (including minimum balance requirement)
                available_balance = savings_account.balance - savings_account.minimum_balance
                if available_balance < total_deduction:
                    raise ValueError("Insufficient funds including fees and minimum balance requirement")

                # Update savings account
                savings_account.balance -= total_deduction
                savings_account.save()

                # Record fee transaction
                if fee > 0:
                    Transaction.objects.create(
                        transaction_ref=f"FEE-{_transaction.transaction_ref}",
                        member=_transaction.member,
                        transaction_type='FEE',
                        amount=fee,
                        payment_method='INTERNAL',
                        status='COMPLETED',
                        description=f"Fee for withdrawal {_transaction.transaction_ref}",
                        source_account=_transaction.source_account
                    )

                # Update transaction status
                _transaction.status = 'COMPLETED'
                _transaction.processed_date = timezone.now()
                _transaction.save()

                # Create ledger entries
                LedgerService.create_withdrawal_entries(_transaction, fee)

                return _transaction

        except Exception as e:
            _transaction.status = 'FAILED'
            _transaction.description = f"Failed: {str(e)}"
            _transaction.save()
            raise
