from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import Role
from apps.members.models import Member
from apps.savings.models import SavingsAccount, SavingsTransaction, InterestRate
from apps.savings.services.account_service import SavingsAccountService
from apps.savings.services.transaction_service import SavingsTransactionService

User = get_user_model()


class SavingsAccountServiceTest(TestCase):
    def setUp(self):
        # Create role
        self.role = Role.objects.create(name='MEMBER')

        # Create user
        self.user = User.objects.create_user(
            email='member@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Member',
            role=self.role,
            phone_number='+256700000000',
            national_id='TEST123'
        )

        # Create member
        self.member = Member.objects.create(
            user=self.user,
            member_number='M2024TEST001',
            date_of_birth=date(1990, 1, 1),
            marital_status='SINGLE',
            employment_status='EMPLOYED',
            occupation='Engineer',
            monthly_income=Decimal('700000'),
            physical_address='Test Address',
            city='Kampala',
            district='Central',
            national_id='TEST123',
            membership_number='SACCOM2024TEST001',
            membership_type='INDIVIDUAL'
        )

        # Create interest rates
        InterestRate.objects.create(
            account_type='REGULAR',
            minimum_balance=Decimal('100'),
            rate=Decimal('3.5'),
            effective_date=date.today()
        )
        
        InterestRate.objects.create(
            account_type='FIXED',
            minimum_balance=Decimal('1000'),
            rate=Decimal('5.0'),
            effective_date=date.today()
        )

    def test_create_regular_account(self):
        """Test creating a regular savings account."""
        account = SavingsAccountService.create_account(
            member_id=self.member.id,
            account_type='REGULAR',
            initial_deposit=Decimal('500')
        )

        self.assertEqual(account.member, self.member)
        self.assertEqual(account.account_type, 'REGULAR')
        self.assertEqual(account.balance, Decimal('500'))
        self.assertEqual(account.status, SavingsAccountService.ACCOUNT_STATUS_ACTIVE)
        self.assertEqual(account.minimum_balance, Decimal('100'))
        self.assertTrue(account.account_number.startswith('SAV'))

        # Check initial deposit transaction was created
        transaction = SavingsTransaction.objects.filter(account=account).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.transaction_type, 'DEPOSIT')
        self.assertEqual(transaction.amount, Decimal('500'))

    def test_create_account_insufficient_initial_deposit(self):
        """Test creating account with insufficient initial deposit."""
        with self.assertRaises(ValueError) as context:
            SavingsAccountService.create_account(
                member_id=self.member.id,
                account_type='REGULAR',
                initial_deposit=Decimal('50')  # Below minimum balance
            )
        
        self.assertIn('Initial deposit must be at least', str(context.exception))

    def test_freeze_account(self):
        """Test freezing a savings account."""
        account = SavingsAccountService.create_account(
            member_id=self.member.id,
            account_type='REGULAR',
            initial_deposit=Decimal('500')
        )

        SavingsAccountService.freeze_account(account.id, "Suspicious activity")
        account.refresh_from_db()

        self.assertEqual(account.status, SavingsAccountService.ACCOUNT_STATUS_FROZEN)

        # Check freeze transaction was logged
        freeze_transaction = SavingsTransaction.objects.filter(
            account=account,
            reference__contains='FREEZE'
        ).first()
        self.assertIsNotNone(freeze_transaction)

    def test_calculate_interest(self):
        """Test interest calculation for an account."""
        account = SavingsAccountService.create_account(
            member_id=self.member.id,
            account_type='REGULAR',
            initial_deposit=Decimal('1000')
        )

        interest = SavingsAccountService.calculate_interest(account.id)
        
        # Daily interest = 1000 * 3.5% / 365 = ~0.096
        expected_interest = Decimal('1000') * Decimal('3.5') / Decimal('365') / Decimal('100')
        self.assertEqual(interest, expected_interest.quantize(Decimal('0.01')))


class SavingsTransactionServiceTest(TestCase):
    def setUp(self):
        # Create role
        self.role = Role.objects.create(name='MEMBER')

        # Create user
        self.user = User.objects.create_user(
            email='member@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Member',
            role=self.role,
            phone_number='+256700000000',
            national_id='TEST123'
        )

        # Create member
        self.member = Member.objects.create(
            user=self.user,
            member_number='M2024TEST001',
            date_of_birth=date(1990, 1, 1),
            marital_status='SINGLE',
            employment_status='EMPLOYED',
            occupation='Engineer',
            monthly_income=Decimal('700000'),
            physical_address='Test Address',
            city='Kampala',
            district='Central',
            national_id='TEST123',
            membership_number='SACCOM2024TEST001',
            membership_type='INDIVIDUAL'
        )

        # Create savings account
        self.savings_account = SavingsAccount.objects.create(
            member=self.member,
            account_number='SAV2024000001',
            account_type='REGULAR',
            balance=Decimal('1000'),
            interest_rate=Decimal('3.50'),
            status='ACTIVE',
            minimum_balance=Decimal('100')
        )

    def test_process_deposit_transaction(self):
        """Test processing a deposit transaction."""
        transaction = SavingsTransactionService.process_transaction(
            account_id=self.savings_account.id,
            transaction_type='DEPOSIT',
            amount=Decimal('500'),
            description='Test deposit'
        )

        self.assertEqual(transaction.transaction_type, 'DEPOSIT')
        self.assertEqual(transaction.amount, Decimal('500'))
        self.assertEqual(transaction.balance_after, Decimal('1500'))

        # Check account balance was updated
        self.savings_account.refresh_from_db()
        self.assertEqual(self.savings_account.balance, Decimal('1500'))

    def test_process_withdrawal_transaction(self):
        """Test processing a withdrawal transaction."""
        transaction = SavingsTransactionService.process_transaction(
            account_id=self.savings_account.id,
            transaction_type='WITHDRAWAL',
            amount=Decimal('300'),
            description='Test withdrawal'
        )

        self.assertEqual(transaction.transaction_type, 'WITHDRAWAL')
        self.assertEqual(transaction.amount, Decimal('300'))
        self.assertEqual(transaction.balance_after, Decimal('700'))

        # Check account balance was updated
        self.savings_account.refresh_from_db()
        self.assertEqual(self.savings_account.balance, Decimal('700'))

    def test_withdrawal_exceeding_available_balance(self):
        """Test withdrawal that would breach minimum balance."""
        with self.assertRaises(ValueError) as context:
            SavingsTransactionService.process_transaction(
                account_id=self.savings_account.id,
                transaction_type='WITHDRAWAL',
                amount=Decimal('950'),  # Would leave 50, below minimum of 100
                description='Invalid withdrawal'
            )
        
        self.assertIn('insufficient funds', str(context.exception).lower())
