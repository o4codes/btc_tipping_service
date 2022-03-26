from django.urls import path, include
from views.lightning_views import (
    LightningTransactionViews,
    LightningDetailsView,
    receiver_confirm_btc_lightening
    )

from views.onchain_views import (
    OnChainTransactionViews, 
    OnChainTransactionDetailView,
    verify_btc_onchain_address,
)

urlpatterns = [
    ######### BTC OnChain Transactions ###########
    path(
        "on-chain/tips", 
        OnChainTransactionViews.as_view(), 
        name="onchain-create-list"
    ),
    path(
        "on-chain/tips/<str:sec_id>",
        OnChainTransactionDetailView.as_view(),
        name="onchain-detail",
    ),
    
    path(
        'btc-onchain/verify/<str:address>',
        verify_btc_onchain_address,
        name="verify-btc-onchain-address"
    ),
    
    ############ BTC Lightning Transactions ############
    path(
        "lightning/tips",
        LightningTransactionViews.as_view(),
        name = "lightening-create-list"
    ),
    
    path(
        "lightning/tips/<str:sec_id>",
        LightningDetailsView.as_view(),
        name="lightening-detail",
    ),
    
    path(
        "lightning/confirm-tip/<str:sec_id>",
        receiver_confirm_btc_lightening,
        name="confirm btc transaction"
         
    )
    
    
]
