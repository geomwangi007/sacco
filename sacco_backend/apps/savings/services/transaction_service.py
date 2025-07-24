# apps/savings/services/transaction_service.py
import uuid
from decimal import Decimal

from django.db import transaction

from apps.savings.models import SavingsTransaction, SavingsAccount


class SavingsTransactionService:
    @staticmethod
    @transaction.atomic
    def process_transaction(
            account_id: int,
            transaction_type: str,
            amount: Decimal,
            reference: str = None,
            description: str = None
    ) -> SavingsTransaction:
        account = SavingsAccount.objects.select_for_update().get(id=account_id)

        if transaction_type == 'WITHDRAWAL':
            if account.balance - amount < account.minimum_balance:
                raise ValueError("Insufficient funds")
            new_balance = account.balance - amount
        else:
            new_balance = account.balance + amount

        account.balance = new_balance
        account.save()

        return SavingsTransaction.objects.create(
            account=account,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=new_balance,
            reference=reference or f"TXN_{transaction_type}_{uuid.uuid4().hex[:8]}"
        )




