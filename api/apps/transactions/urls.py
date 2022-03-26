from django.urls import path, include
from .views.lightning_views import (
    LightningTransactionViews,
    LightningDetailsView,
    receiver_confirm_btc
    )

from .views.onchain_views import (
    generate_btc_address,
    OnChainTransactionViews, 
    OnChainTransactionDetailView,
    verify_btc_onchain_address,
)

urlpatterns = [
    ######### BTC OnChain Transactions ###########
    path(
        'btc/onchain/address/<str:email>', 
        generate_btc_address, 
        name='generate_btc_address'),
    
    path(
        'btc/onchain/validate/<str:address>',
        verify_btc_onchain_address,
        name="verify-btc-onchain-address"
    ),
    
    path(
        "btc/onchain/tips", 
        OnChainTransactionViews.as_view(), 
        name="onchain-create-list"
    ),
    path(
        "on-chain/tips/<str:sec_id>",
        OnChainTransactionDetailView.as_view(),
        name="onchain-detail",
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
        "lightning/tips/confirm/<str:sec_id>",
        receiver_confirm_btc,
        name="confirm btc transaction"
         
    )
    
    
]
