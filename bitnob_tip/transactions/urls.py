from django.urls import path, include
from .views import OnChainTransactionViews, OnChainTransactionDetailView

urlpatterns = [
    path(
        "on-chain/tips/", OnChainTransactionViews.as_view(), name="onchain-create-list"
    ),
    path(
        "on-chain/tips/<uuid:sec_id>/",
        OnChainTransactionDetailView.as_view(),
        name="onchain-detail",
    ),
]
