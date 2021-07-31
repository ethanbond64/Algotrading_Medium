import cbpro
import numpy as np
import datetime as dt
import time

public_client = cbpro.PublicClient()



apiKey = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
apiSecret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
passphrase = "XXXXXXXXXXX"

auth_client = cbpro.AuthenticatedClient(apiKey,apiSecret,passphrase)

                        ### Investment Details ###

# Amount to initially invest
initInvestment = 20.0

# Amount that will be used for purchase starts at the initial amount
funding = initInvestment

# Currency to trade, for reference:
# 'BCH-USD' = Bitcoin Cash, 'BTC-USD' = Bitcoin, 'ETH-USD' = Ether
currency = 'DOGE-USD'
specific_currency = 'DOGE'

# Will return the ID of your specific currency account
def getSpecificAccount(cur):
    x = auth_client.get_accounts()
    for account in x:
        if account['currency'] == cur:
            return account['id']

# Get the currency's specific ID

specificID = getSpecificAccount(str(specific_currency))

# Granularity (in seconds). So 300 = data from every 5 min (its a stickler about the seconds tho)
period = 500

# We will keep track of how many iterations our bot has done
iteration = 1

# Start off by looking to buy
buy = True

while True:
    try:
        historicData = auth_client.get_product_historic_rates(currency, granularity=period)

        # Make an array of the historic price data from the matrix
        price = np.squeeze(np.asarray(np.matrix(historicData)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        time.sleep(1)

        # Get latest data and show to the user for reference
        newData = auth_client.get_product_ticker(product_id=currency)
        print(newData)
        currentPrice = newData['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break

    # Calculate the rate of change 11 and 14 units back, then sum them
    ROC11 = np.zeros(13)
    ROC14 = np.zeros(13)
    ROCSUM = np.zeros(13)

    for ii in range(0,13):
        ROC11[ii] = (100*(price[ii]-price[ii+11]) / float(price[ii+11]))
        ROC14[ii] = (100*(price[ii]-price[ii+14]) / float(price[ii+14]))
        ROCSUM[ii] = ( ROC11[ii] + ROC14[ii] )

    coppock = np.zeros(4)
    # Calculate the past 4 Coppock values with Weighted Moving Average
    for ll in range(0,4):
        coppock[ll] = (((1*ROCSUM[ll+9]) + (2*ROCSUM[ll+8]) + (3*ROCSUM[ll+7]) \
        + (4*ROCSUM[ll+6]) + (5*ROCSUM[ll+5]) + (6*ROCSUM[ll+4]) \
        + (7*ROCSUM[ll+3]) + (8*ROCSUM[ll+2]) + (9*ROCSUM[ll+1]) \
        + (10*ROCSUM[ll])) / float(55))

    # Calculate the past 3 derivatives of the Coppock Curve
    coppockD1 = np.zeros(3)
    for mm in range(0,3):
        coppockD1[mm] = coppock[mm] - coppock[mm+1]

    # The maximum amount of Cryptocurrency that can be purchased with your funds
    possiblePurchase = (float(funding)) / float(currentPrice)

    print(specificID)

    # The amount of currency owned
    owned = float(auth_client.get_account(specificID)['available'])

    # The value of the cryptourrency in USD
    possibleIncome = float(currentPrice) * owned

    # Buy Conditions: latest derivative is + and previous is -
    if buy == True and (coppockD1[0]/abs(coppockD1[0])) == 1 and (coppockD1[1]/abs(coppockD1[1])) == -1:

        # Place the order
        auth_client.place_market_order(product_id=currency, side='buy', funds=str(funding))

        # Print message in the terminal for reference
        message = "Buying Approximately " + str(possiblePurchase) + " " + \
        currency + "  Now @ " + str(currentPrice) + "/Coin. TOTAL = " + str(funding)
        print(message)

        # Update funding level and Buy variable
        funding = 0
        buy = False

    # Sell Conditions: latest derivative is - and previous is +
    if buy == False and (coppockD1[0]/abs(coppockD1[0])) == -1 and (coppockD1[1]/abs(coppockD1[1])) == 1:

        # Place the order
        auth_client.place_market_order(product_id=currency,side='sell',size=str(owned))

        # Print message in the terminal for reference
        message = "Selling " + str(owned) + " " + currency + "Now @ " + \
        str(currentPrice) + "/Coin. TOTAL = " + str(possibleIncome)
        print(message)

        # Update funding level and Buy variable
        funding = int(possibleIncome)
        buy = True

    # Stop loss: sell everything and stop trading if your value is less than 80% of initial investment
    if (possibleIncome+funding) <= 0.8 * initInvestment:

        # If there is any of the crypto owned, sell it all
        if owned > 0.0:
            auth_client.place_market_order(product_id=currency, side='sell', size=str(owned))
            print("STOP LOSS SOLD ALL")

        # Will break out of the while loop and the program will end
        break

    # Printing here to make the details easier to read in the terminal
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("iteration number", iteration)

    # Print the details for reference
    print("Current Price: ", currentPrice)
    print("Your Funds = ", funding)
    print("You Own ", owned, currency)

    # Wait for however long the period variable is before repeating
    time.sleep(300)
    iteration += 1
