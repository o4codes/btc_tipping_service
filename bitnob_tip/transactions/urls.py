from django.urls import path, include
from .views import OnChainTransactionViews

urlpatterns = [
    path('on-chain/tips/', OnChainTransactionViews.as_view(), name='onchain-create-list'),
]