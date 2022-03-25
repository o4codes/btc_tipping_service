from django.urls import path, include
from .views import (
    OnChainTransactionViews, 
    OnChainTransactionDetailView,
    verify_btc_onchain_address,
    LighteningTransactionViews,
    LighteningDetailsView
    )

urlpatterns = [
    path(
        "on-chain/tips/", 
        OnChainTransactionViews.as_view(), 
        name="onchain-create-list"
    ),
    path(
        "on-chain/tips/<str:sec_id>/",
        OnChainTransactionDetailView.as_view(),
        name="onchain-detail",
    ),
    
    path(
        'btc-onchain/verify/<str:address>/',
        verify_btc_onchain_address,
        name="verify-btc-onchain-address"
    ),
    
    
    path(
        "lightening/tips/",
        LighteningTransactionViews.as_view(),
        name = "lightening-create-list"
    ),
    
    path(
        "lightening/tips/<str:sec_id>/",
        LighteningDetailsView.as_view(),
        name="lightening-detail",
    ),
    
    
    
    
]
