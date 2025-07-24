# apps/loans/services/loan_service.py
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Tuple

from django.db import transaction
from django.utils import timezone

from apps.loans.models import Loan, LoanRepayment
from apps.members.models import Member
from apps.notifications.services.notification_service import NotificationService
from apps.risk_management.models import RiskProfile

logger = logging.getLogger(__name__)


class LoanService:
    @staticmethod
    def calculate_monthly_payment(principal: Decimal, annual_rate: Decimal, term_months: int) -> Decimal:
        monthly_rate = annual_rate / 12 / 100
        payment = (principal * monthly_rate * (1 + monthly_rate) ** term_months) / (
                (1 + monthly_rate) ** term_months - 1)
        return payment.quantize(Decimal('0.01'))

    @staticmethod
    @transaction.atomic
    def approve_loan(loan: Loan, approved_by):
        loan.status = 'APPROVED'
        loan.approval_date = timezone.now()
        loan.approved_by = approved_by
        loan.save()

        NotificationService.send_loan_approval_notification_sync(loan.member)
        return loan

    @staticmethod
    @transaction.atomic
    def disburse_loan(loan: Loan):
        loan.status = 'DISBURSED'
        loan.disbursement_date = timezone.now()
        loan.save()

        # Create repayment schedule
        monthly_payment = LoanService.calculate_monthly_payment(
            loan.amount, loan.interest_rate, loan.term_months
        )

        for month in range(1, loan.term_months + 1):
            due_date = loan.disbursement_date.date() + timedelta(days=30 * month)

            # Calculate principal and interest components (simplified)
            # In a real system, you would use an amortization schedule
            remaining_months = loan.term_months - month + 1
            interest_component = (loan.amount * (loan.interest_rate / 12 / 100)).quantize(Decimal('0.01'))
            principal_component = (monthly_payment - interest_component).quantize(Decimal('0.01'))

            LoanRepayment.objects.create(
                loan=loan,
                reference=f"RP{loan.reference[2:]}-{month:02d}",
                due_date=due_date,
                amount=monthly_payment,
                principal_component=principal_component,
                interest_component=interest_component,
                penalty_amount=Decimal('0.00')
            )

        NotificationService.send_loan_disbursement_notification_sync(loan.member)
        return loan

    @staticmethod
    async def check_eligibility(member: Member) -> Tuple[bool, str]:
        """Check if member is eligible for a loan"""
        try:
            # Check membership duration
            membership_duration = (date.today() - member.registration_date).days
            if membership_duration < 90:  # 3 months minimum
                return False, "Minimum membership period not met (3 months required)"

            # Check existing loans
            active_loans = await Loan.objects.filter(
                member=member,
                status__in=['PENDING', 'APPROVED', 'DISBURSED']
            ).acount()

            if active_loans > 0:
                return False, "Has existing active loan"

            # Check minimum savings requirement
            savings_balance = member.savings_account.balance
            if savings_balance < Decimal('100000'):  # Minimum 100,000 UGX
                return False, "Insufficient savings balance (min. 100,000 UGX)"

            # Check payment history
            defaulted_loans = await Loan.objects.filter(
                member=member,
                status='DEFAULTED'
            ).acount()

            if defaulted_loans > 0:
                return False, "Previous loan defaults found"

            # Check KYC status
            if not member.is_verified:
                return False, "KYC verification incomplete"

            # Get credit score
            risk_profile = await RiskProfile.objects.filter(member=member).afirst()
            if risk_profile and risk_profile.credit_score < 600:
                return False, "Credit score below minimum requirement"

            return True, "Eligible for loan"

        except Exception as e:
            logger.error(f"Error checking loan eligibility for member {member.id}: {str(e)}")
            return False, "Error checking eligibility"