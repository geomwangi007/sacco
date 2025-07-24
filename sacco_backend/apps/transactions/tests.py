from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date
from unittest.mock import patch

from apps.authentication.models import Role
from apps.members.models import Member
from apps.transactions.models import Transaction, TransactionFee
from apps.transactions.services.transaction_service import TransactionService
from apps.savings.models import SavingsAccount

User = get_user_model()


class TransactionWorkflowTest(TestCase):
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
            balance=Decimal('100000'),
            interest_rate=Decimal('3.50'),
            status='ACTIVE',
            minimum_balance=Decimal('10000')
        )

        # Link savings account to member
        self.member.savings_account = self.savings_account
        self.member.save()

        # Create transaction fees for testing
        TransactionFee.objects.create(
            transaction_type='WITHDRAWAL',
            payment_method='CASH',
            fixed_amount=Decimal('1000'),
            percentage=Decimal('0'),
        )
        
        TransactionFee.objects.create(
            transaction_type='DEPOSIT',
            payment_method='CASH',
            fixed_amount=Decimal('0'),
            percentage=Decimal('0'),
        )

        # Mock notification service
        self.notification_patcher = patch('apps.transactions.services.transaction_service.NotificationService')
        self.mock_notification_service = self.notification_patcher.start()

        # Mock ledger service
        self.ledger_patcher = patch('apps.transactions.services.transaction_service.LedgerService')
        self.mock_ledger_service = self.ledger_patcher.start()

    def tearDown(self):
        self.notification_patcher.stop()
        self.ledger_patcher.stop()

    def test_deposit_transaction(self):
        # Create a deposit transaction
        with patch('apps.transactions.services.transaction_service.TransactionService._generate_reference',
                   return_value='TXN20240101TEST'):
            transaction = TransactionService.create_transaction(
                member_id=self.member.id,
                transaction_type='DEPOSIT',
                amount=Decimal('50000'),
                payment_method='CASH',
                description='Test deposit'
            )

        # Check transaction was created correctly
        self.assertEqual(transaction.transaction_ref, 'TXN20240101TEST')
        self.assertEqual(transaction.member, self.member)
        self.assertEqual(transaction.transaction_type, 'DEPOSIT')
        self.assertEqual(transaction.amount, Decimal('50000'))
        self.assertEqual(transaction.status, 'COMPLETED')

        # Check savings account was updated
        self.savings_account.refresh_from_db()
        self.assertEqual(self.savings_account.balance, Decimal('150000'))  # 100000 + 50000

        # Check notification was sent
        self.mock_notification_service.send_transaction_notification.assert_called_once()

    def test_withdrawal_transaction(self):
        # Create a withdrawal transaction
        with patch('apps.transactions.services.transaction_service.TransactionService._generate_reference',
                   return_value='TXN20240102TEST'):
            transaction = TransactionService.create_transaction(
                member_id=self.member.id,
                transaction_type='WITHDRAWAL',
                amount=Decimal('30000'),
                payment_method='CASH',
                description='Test withdrawal'
            )

        # Check transaction was created correctly
        self.assertEqual(transaction.transaction_ref, 'TXN20240102TEST')
        self.assertEqual(transaction.member, self.member)
        self.assertEqual(transaction.transaction_type, 'WITHDRAWAL')
        self.assertEqual(transaction.amount, Decimal('30000'))
        self.assertEqual(transaction.status, 'COMPLETED')

        # Check savings account was updated (amount + fee)
        self.savings_account.refresh_from_db()
        self.assertEqual(self.savings_account.balance, Decimal('69000'))  # 100000 - 30000 - 1000 (fee)

        # Check notification was sent
        self.mock_notification_service.send_transaction_notification.assert_called_once()

    def test_withdrawal_exceeding_balance(self):
        # Try to withdraw more than the available balance (considering minimum balance and fees)
        # Available balance = 100000 - 10000 (min balance) = 90000
        # With 1000 fee, max withdrawal is 89000
        with self.assertRaises(ValueError):
            TransactionService.create_transaction(
                member_id=self.member.id,
                transaction_type='WITHDRAWAL',
                amount=Decimal('90000'),  # Exceeds available balance after minimum balance and fee
                payment_method='CASH',
                description='Invalid withdrawal'
            )

        # Check savings account balance is unchanged
        self.savings_account.refresh_from_db()
        self.assertEqual(self.savings_account.balance, Decimal('100000'))

    def test_transaction_with_fees(self):
        # Mock the fee calculation to return a fixed fee
        with patch('apps.transactions.services.transaction_service.TransactionService._calculate_fee',
                   return_value=Decimal('1000')):
            with patch('apps.transactions.services.transaction_service.TransactionService._generate_reference',
                       return_value='TXN20240103TEST'):
                transaction = TransactionService.create_transaction(
                    member_id=self.member.id,
                    transaction_type='WITHDRAWAL',
                    amount=Decimal('20000'),
                    payment_method='CASH',
                    description='Test withdrawal with fee'
                )

        # Check transaction was created correctly
        self.assertEqual(transaction.transaction_ref, 'TXN20240103TEST')
        self.assertEqual(transaction.amount, Decimal('20000'))

        # Check savings account was updated with amount + fee
        self.savings_account.refresh_from_db()
        self.assertEqual(self.savings_account.balance, Decimal('79000'))  # 100000 - 20000 - 1000