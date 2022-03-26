# BTC Tipping Service

This service allows you to tip users of the platform with Bitcoin.
Once a user is registered with the service, they can tip other users of the platform with Bitcoin in fairly easy and secure manner.
Users have options of sending BTC to other users using either onchain or lightning payments

## Service Usage

### BTC OnChain Tipping Process

1. Get address of the user you want to tip using the '/btc/onchain/address/:email' endpoint.
2. Validate the address using the '/btc/onchain/validate/:address' endpoint.
3. Send the amount of BTC to the address by making a POST request to '/btc/onchain/tips' endpoint. The request body will contain the amount of BTC, the address of the user and a message/description
4. The user will receive the amount of BTC in their wallet and confirm that payment is received using the '/btc/onchain/tips/confirm/:txid' endpoint.

### BTC Lightning Tipping Process

1. Get lightning invoice of the user you want to tip using the '/btc/lightning/invoice/:email' endpoint.
2. Validate that the invoice is valid using the '/btc/lightning/validate/:invoice' endpoint.
3. Send the amount of BTC to the invoice by making a POST request to '/btc/lightning/tips' endpoint. The request body will contain the amount of BTC, the invoice and a message/description.
4. The user wull receive the amount of BTC in their wallet and confirm that payment is received using the '/btc/lightning/tips/confirm/:tcid' endpoint.

## Project Setup Guidelines
