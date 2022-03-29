from django.urls import path, include
from .views.lightning_views import (
    validate_lightning_address,
    LightningTransactionViews,
    LightningDetailsView,
    receiver_confirm_btc
    )

from .views.onchain_views import (
    validate_btc_onchain_address,
    OnChainTransactionViews, 
    OnChainTransactionDetailView,
    confirm_receive_btc
)

urlpatterns = [
    ######### BTC OnChain Transactions ###########
    path(
        'btc/onchain/validate/<str:address>',
        validate_btc_onchain_address,
        name="verify-btc-onchain-address"
    ),
    
    path(
        "btc/onchain", 
        OnChainTransactionViews.as_view(), 
        name="onchain-create-list"
    ),
    
    path(
        "btc/onchain/<str:sec_id>",
        OnChainTransactionDetailView.as_view(),
        name="onchain-detail",
    ),
    
    path(
        "btc/onchain/transactions/<str:txid>/address/<str:address>",
        confirm_receive_btc,
        name = "confirm-receive-btc"
    ),
    
    ############ BTC Lightning Transactions ############
    path(
        "btc/lightning/validate/<str:address>",
        validate_lightning_address,
        name="verify-lightning-address"
        ),
    
    path(
        "btc/lightning",
        LightningTransactionViews.as_view(),
        name = "lightening-create-list"
    ),
    
    path(
        "btc/lightning/<str:txid>",
        LightningDetailsView.as_view(),
        name="lightening-detail",
    ),
    
    path(
        "btc/lightning/transactions/<str:txid>/address/<str:address>",
        receiver_confirm_btc,
        name="confirm btc transaction"
         
    )
    
    
]
