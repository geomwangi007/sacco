from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, NextOfKinViewSet

router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='members')
router.register(r'next-of-kin', NextOfKinViewSet, basename='next-of-kin')

urlpatterns = [
    path('', include(router.urls)),
]