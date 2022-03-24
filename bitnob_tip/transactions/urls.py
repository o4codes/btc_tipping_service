from django.urls import path, include
from .views import OnChainTransactionViews, OnChainTransactionDetailView

urlpatterns = [
    path('on-chain/tips/', OnChainTransactionViews.as_view(), name='onchain-create-list'),
    path('on-chain/tips/<int:pk>/', OnChainTransactionDetailView.as_view(), name='onchain-detail'),
]