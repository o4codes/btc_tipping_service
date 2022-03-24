from django.urls import path, include
from .views import (
    OnChainTransactionViews, 
    OnChainTransactionDetailView,
    verify_lightening_address
    )

urlpatterns = [
    path(
        "on-chain/tips/", OnChainTransactionViews.as_view(), name="onchain-create-list"
    ),
    path(
        "on-chain/tips/<str:sec_id>/",
        OnChainTransactionDetailView.as_view(),
        name="onchain-detail",
    ),
    
    path(
        "lnAddress/verify/<str:address>/", 
        verify_lightening_address, 
        name="verify-lightening-address"),
]
