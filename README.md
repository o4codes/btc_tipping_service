# BTC Tipping Service

This service allows you to tip users of the platform with Bitcoin.
Once a user is registered with the service, they can tip other users of the platform with Bitcoin in fairly easy and secure manner.
Users have options of sending BTC to other users using either onchain or lightning payments

Deployed server is running on [Heroku Link](https://btc-tip.herokuapp.com/)
## Service Usage

### BTC OnChain Tipping Process

1. Validate the address using the '/btc/onchain/validate/:address' endpoint.
2. Send the amount of BTC to the address by making a POST request to '/btc/onchain' endpoint. The request body will contain the amount of BTC, the address of the user and a message/description
3. The user will receive the amount of BTC in their wallet and confirm that payment is received using the '/btc/onchain/transactions/:txid/address/:address' endpoint. where txid is the transaction id of the payment and address is the address of the receiver.

### BTC Lightning Tipping Process

1. Validate the lightness address using the '/btc/lightning/validate/:address' endpoint
2. Send btc by making a POST request to '/btc/lightning/tips' endpoint. The request body will contain the amount of BTC, the lightning address, a description.
3. The user wull receive the amount of BTC in their wallet and confirm that payment is received using the '/btc/lightning/transactions/:txid/address/:address' endpoint. where txid is the transaction id of the payment and address is the address of the receiver.

## Project Setup Guidelines

1. Create a bitnob business account at <https://app.bitnob.co/accounts/signin> and grab your secret keys
2. Fork the repository
3. Clone the repository using `git clone <github_repo_link>`
4. cd into the root directory of the repository
5. Ensure python is installed  
6. Create a virtual environment using `python3 -m venv venv`
7. Activate the virtual environment using `source venv/bin/activate` (or `venv/Scripts/activate` on Windows)
8. Install the dependencies using `pip install -r requirements.txt`
9. Create a .env file containing the secret keys in the following format specified in the .env.sample file
10. Create migrations using `python manage.py makemigrations`
11. Run the migrations using `python manage.py migrate`
12. Tests can be ran using `python manage.py test`
13. Install ngrok on your systems in order to test locally with webhooks functionality
14. Startup ngrok using `ngrok http 8000`
15. Startup the server using `python manage.py runserver`. Ensure server is running on the port ngrok is running on
16. Go to your bitnob account and add webhook url to the webhooks section of your account. The webhook url should be the url of the ngrok server appended with "/api/v1/webhook"
17. Docs of the endpoints can be viewed from the root url of the server which is <http://127.0.0.1:8000> (if the server is running on port 8000)

## Contribution

1. Setup Project using the guidelines above.
2. Create a feature branch using `git checkout -b feature/<feature-name>`
3. Make contributions
4. Commit changes to the feature branch using
    `git add *
    git commit -m <message>`

5. Push changes to your remote repository using `git push origin feature/<feature-name>`
6. Create a pull request to the dev branch of the main repository.

## Future Development

1. Add email notiification to the service to notify users when payment is recieved or failed
