import cbpro

# CB Pro granted api credentials as strings
apiKey = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
apiSecret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
passphrase = "XXXXXXXXXXX"

auth_client = cbpro.AuthenticatedClient(apiKey,apiSecret,passphrase)

# Change this to whichever currency you want to trade
# BCH = Bitcoin Cash, BTC = Bitcoin, ETH = Ether
currency = 'BCH'

# Will print the id of your specific currency account in the terminal
x = auth_client.get_accounts()
for account in x:
    if account['currency'] == currency:
        print(account['id'])
