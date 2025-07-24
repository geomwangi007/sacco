# apps/savings/services/account_service.py
from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.members.models import Member
from apps.savings.models import SavingsAccount, InterestRate, SavingsTransaction


class SavingsAccountService:
    
    ACCOUNT_STATUS_ACTIVE = 'ACTIVE'
    ACCOUNT_STATUS_FROZEN = 'FROZEN'
    ACCOUNT_STATUS_CLOSED = 'CLOSED'
    ACCOUNT_STATUS_DORMANT = 'DORMANT'

    @staticmethod
    @transaction.atomic
    def create_account(member_id: int, account_type: str, initial_deposit: Decimal = Decimal('0')) -> SavingsAccount:
        """Create a new savings account with proper validation."""
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            raise ValueError("Member not found")

        # Check if member is eligible for new account
        if not SavingsAccountService._check_member_eligibility(member, account_type):
            raise ValueError("Member not eligible for this account type")

        # Get minimum balance requirement
        min_balance = SavingsAccountService._get_minimum_balance(account_type)
        if initial_deposit < min_balance:
            raise ValueError(f"Initial deposit must be at least {min_balance}")

        account_number = SavingsAccountService._generate_account_number(account_type)
        
        # Get interest rate for account type
        try:
            interest_rate_obj = InterestRate.objects.filter(
                account_type=account_type
            ).order_by('-effective_date').first()
            interest_rate = interest_rate_obj.rate if interest_rate_obj else Decimal('2.5')
        except:
            interest_rate = Decimal('2.5')  # Default rate

        account = SavingsAccount.objects.create(
            member=member,
            account_number=account_number,
            account_type=account_type,
            balance=initial_deposit,
            interest_rate=interest_rate,
            status=SavingsAccountService.ACCOUNT_STATUS_ACTIVE,
            minimum_balance=min_balance
        )

        # Create initial deposit transaction if amount > 0
        if initial_deposit > 0:
            SavingsTransaction.objects.create(
                account=account,
                transaction_type='DEPOSIT',
                amount=initial_deposit,
                balance_after=initial_deposit,
                reference=f"INIT_{account_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )

        return account

    @staticmethod
    def freeze_account(account_id: int, reason: str = "Administrative action") -> None:
        """Freeze a savings account."""
        try:
            account = SavingsAccount.objects.get(id=account_id)
            if account.status == SavingsAccountService.ACCOUNT_STATUS_CLOSED:
                raise ValueError("Cannot freeze a closed account")
            
            account.status = SavingsAccountService.ACCOUNT_STATUS_FROZEN
            account.save()
            
            # Log the freeze action
            SavingsTransaction.objects.create(
                account=account,
                transaction_type='CHARGE',
                amount=Decimal('0'),
                balance_after=account.balance,
                reference=f"FREEZE_{account.account_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
        except SavingsAccount.DoesNotExist:
            raise ValueError("Account not found")

    @staticmethod
    def unfreeze_account(account_id: int) -> None:
        """Unfreeze a savings account."""
        try:
            account = SavingsAccount.objects.get(id=account_id)
            if account.status != SavingsAccountService.ACCOUNT_STATUS_FROZEN:
                raise ValueError("Account is not frozen")
            
            account.status = SavingsAccountService.ACCOUNT_STATUS_ACTIVE
            account.save()
            
            # Log the unfreeze action
            SavingsTransaction.objects.create(
                account=account,
                transaction_type='CHARGE',
                amount=Decimal('0'),
                balance_after=account.balance,
                reference=f"UNFREEZE_{account.account_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
        except SavingsAccount.DoesNotExist:
            raise ValueError("Account not found")

    @staticmethod
    @transaction.atomic
    def close_account(account_id: int, reason: str = "Member request") -> Decimal:
        """Close a savings account and return final balance."""
        try:
            account = SavingsAccount.objects.get(id=account_id)
            if account.status == SavingsAccountService.ACCOUNT_STATUS_CLOSED:
                raise ValueError("Account is already closed")
            
            final_balance = account.balance
            
            # Transfer balance to member if any
            if final_balance > 0:
                # In a real system, this would transfer to another account or cash out
                SavingsTransaction.objects.create(
                    account=account,
                    transaction_type='WITHDRAWAL',
                    amount=final_balance,
                    balance_after=Decimal('0'),
                    reference=f"CLOSE_{account.account_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
                account.balance = Decimal('0')
            
            account.status = SavingsAccountService.ACCOUNT_STATUS_CLOSED
            account.save()
            
            return final_balance
        except SavingsAccount.DoesNotExist:
            raise ValueError("Account not found")

    @staticmethod
    def calculate_interest(account_id: int) -> Decimal:
        """Calculate interest for an account."""
        try:
            account = SavingsAccount.objects.get(id=account_id)
            if account.status != SavingsAccountService.ACCOUNT_STATUS_ACTIVE:
                return Decimal('0')
            
            # Simple daily interest calculation
            # In real system, this would be more complex based on account type
            daily_rate = account.interest_rate / Decimal('365') / Decimal('100')
            interest = account.balance * daily_rate
            
            return interest.quantize(Decimal('0.01'))
        except SavingsAccount.DoesNotExist:
            raise ValueError("Account not found")

    @staticmethod
    def _check_member_eligibility(member: Member, account_type: str) -> bool:
        """Check if member is eligible for account type."""
        # Basic eligibility checks
        if member.membership_status != 'ACTIVE':
            return False
        
        # Check for existing accounts of same type
        existing_count = SavingsAccount.objects.filter(
            member=member,
            account_type=account_type,
            status__in=[SavingsAccountService.ACCOUNT_STATUS_ACTIVE, SavingsAccountService.ACCOUNT_STATUS_FROZEN]
        ).count()
        
        # Limit certain account types
        if account_type in ['FIXED', 'CHILDREN'] and existing_count >= 3:
            return False
        
        return True

    @staticmethod
    def _get_minimum_balance(account_type: str) -> Decimal:
        """Get minimum balance for account type."""
        minimum_balances = {
            'REGULAR': Decimal('100'),
            'FIXED': Decimal('1000'),
            'CHILDREN': Decimal('50'),
            'GROUP': Decimal('500')
        }
        return minimum_balances.get(account_type, Decimal('100'))

    @staticmethod
    def _generate_account_number(account_type: str) -> str:
        """Generate unique account number."""
        prefix_map = {
            'REGULAR': 'SAV',
            'FIXED': 'FIX',
            'CHILDREN': 'CHD',
            'GROUP': 'GRP'
        }
        prefix = f"{prefix_map.get(account_type, 'SAV')}{datetime.now().year}"
        
        count = SavingsAccount.objects.filter(
            account_number__startswith=prefix
        ).count()
        
        return f"{prefix}{str(count + 1).zfill(6)}"

    @staticmethod
    def get_account_summary(member_id: int) -> dict:
        """Get summary of all accounts for a member."""
        try:
            member = Member.objects.get(id=member_id)
            accounts = SavingsAccount.objects.filter(member=member)
            
            total_balance = sum(acc.balance for acc in accounts if acc.status == SavingsAccountService.ACCOUNT_STATUS_ACTIVE)
            
            return {
                'member': member.full_name,
                'total_accounts': accounts.count(),
                'active_accounts': accounts.filter(status=SavingsAccountService.ACCOUNT_STATUS_ACTIVE).count(),
                'total_balance': total_balance,
                'accounts': [
                    {
                        'account_number': acc.account_number,
                        'account_type': acc.account_type,
                        'balance': acc.balance,
                        'status': acc.status
                    } for acc in accounts
                ]
            }
        except Member.DoesNotExist:
            raise ValueError("Member not found")


