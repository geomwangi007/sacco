from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.savings.views import SavingsAccountViewSet, SavingsTransactionViewSet, InterestRateViewSet

router = DefaultRouter()
router.register(r'accounts', SavingsAccountViewSet, basename='savings-accounts')
router.register(r'transactions', SavingsTransactionViewSet, basename='savings-transactions')
router.register(r'interest-rates', InterestRateViewSet, basename='interest-rates')

urlpatterns = [
    path('savings/', include(router.urls)),
]