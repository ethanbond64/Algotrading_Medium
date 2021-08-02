import cbpro
import numpy as np
import datetime as dt
import time

public_client = cbpro.PublicClient()

public = ""
private = ""
secret = ""

auth_client = cbpro.AuthenticatedClient(public,private,secret)

# Amount to initially invest
initInvestment = 100

# Amount that will be used for purchase starts at the initial amount
funding = float(initInvestment*0.4)
funding1 = float(initInvestment*0.2)
funding2 = float(initInvestment*0.2)
funding3 = float(initInvestment*0.2)


# Currency to trade, for reference:
# 'BCH-USD' = Bitcoin Cash, 'BTC-USD' = Bitcoin, 'ETH-USD' = Ether
currency = 'DOGE-USD'
currency1 = 'BTC-USD'
currency2 = 'ETH-USD'
currency3 = 'ADA-USD'

# Will return the ID of your specific currency account
def getSpecificAccount(cur):
    x = auth_client.get_accounts()
    for account in x:
        if account['currency'] == cur:
            return account['id']

# Get the currency's specific ID
# You have to type in the specific currency you want eg. 'DOGE' = DOGE-USD, 'BTC' = BTC-USD, etc
specificID = getSpecificAccount(str('DOGE'))
specificID1 = getSpecificAccount(str('BTC'))
specificID2 = getSpecificAccount(str('ETH'))
specificID3 = getSpecificAccount(str('ADA'))

# Granularity (in seconds). So 300 = data from every 5 min (its a stickler about the seconds tho)
period = 60

# We will keep track of how many iterations our bot has done
iteration = 1

# Start off by looking to buy (you need to set each buy to true for each cryptocurrency)
buy = True
buy1 = True
buy2 = True
buy3 = True
sellstop = False

# Calculates the Curve for the currencies
def CoppockFormula(price):
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
    CoppockFormula.variable = coppockD1

# BuySell function buys and sells the crypto using the CoppockFormula above
def BuySell(buyvar, coppockD1, currency, funds, currentPrice, possibleIncome, initInvestment, owned, fundingvar):
    # The maximum amount of Cryptocurrency that can be purchased with your funds.
    # The function BuySell has a variable so you could have an unlimited amount of currencies listed
    # as long as you make sure they are assigned to a variable
    possiblePurchase = (float(funds)) / float(currentPrice)
    global buy_var
    buy_var = buyvar
    print(coppockD1[0] / abs(coppockD1[0]))
    print(coppockD1[1] / abs(coppockD1[1]))
    if buyvar == True and (coppockD1[0] / abs(coppockD1[0])) == 1 and (coppockD1[1] / abs(coppockD1[1])) == -1:

        # Place the order
        auth_client.place_market_order(product_id=currency, side='buy', funds=str(funds))

        # Print message in the terminal for reference
        message = "Buying Approximately " + str(possiblePurchase) + " " + currency + "  Now @ " + str(currentPrice) + "/Coin. TOTAL = " + str(funds)
        print(message)

        # Update funding level and Buy variable
        fundingvar = 0
        buy_var = False

    print(coppockD1[0]/abs(coppockD1[0]))
    print(coppockD1[1]/abs(coppockD1[1]))
    # Sell Conditions: latest derivative is - and previous is +
    if buyvar == False and (coppockD1[0]/abs(coppockD1[0])) == -1 and (coppockD1[1]/abs(coppockD1[1])) == 1:

        # Place the order
        auth_client.place_market_order(product_id=currency,side='sell',size=str(owned))

        # Print message in the terminal for reference
        message = "Selling " + str(owned) + " " + currency + "Now @ " + \
        str(currentPrice) + "/Coin. TOTAL = " + str(possibleIncome)
        print(message)

        # Update funding level and Buy variable
        fundingvar = int(possibleIncome)
        buy_var = True

    # Stop loss: sell everything and stop trading if your value is less than 80% of initial investment
    if (possibleIncome+owned) <= 0.8 * initInvestment:
        # If there is any of the crypto owned, sell it all
        if owned > 0.0:
            auth_client.place_market_order(product_id=currency, side='sell', size=str(owned))
            print("STOP LOSS SOLD ALL")
            time.sleep(1)
        # Will break out of the while loop and the program will end
        sellstop = True
    BuySell.variable = fundingvar
    #time.sleep(1)


#  misc statistics for better readability
def stats(currentPrice, funds, owned, currency, coppockres):
    print("Current Price: $" + str(currentPrice))
    print("Your Funds: $" + str(funds))
    print("You Own: ", owned, currency)
    print("coppock data: ", coppockres)

# Main Loop
while True:
    # 4 loops for each currency
    try:
        historicData = auth_client.get_product_historic_rates(currency, granularity=period)

        # Make an array of the historic price data from the matrix
        price = np.squeeze(np.asarray(np.matrix(historicData)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        #time.sleep(1)

        # Get latest data and show to the user for reference
        newData = auth_client.get_product_ticker(product_id=currency)
        print(newData)
        currentPrice = newData['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break
    try:
        historicData1 = auth_client.get_product_historic_rates(currency1, granularity=period)

        # Make an array of the historic price data from the matrix
        price1 = np.squeeze(np.asarray(np.matrix(historicData1)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        #time.sleep(1)

        # Get latest data and show to the user for reference
        newData1 = auth_client.get_product_ticker(product_id=currency1)
        print(newData1)
        currentPrice1 = newData1['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break
    try:
        historicData2 = auth_client.get_product_historic_rates(currency2, granularity=period)

        # Make an array of the historic price data from the matrix
        price2 = np.squeeze(np.asarray(np.matrix(historicData2)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        #time.sleep(1)

        # Get latest data and show to the user for reference
        newData2 = auth_client.get_product_ticker(product_id=currency2)
        print(newData2)
        currentPrice2 = newData2['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break
    try:
        historicData3 = auth_client.get_product_historic_rates(currency3, granularity=period)

        # Make an array of the historic price data from the matrix
        price3 = np.squeeze(np.asarray(np.matrix(historicData3)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        #time.sleep(1)

        # Get latest data and show to the user for reference
        newData3 = auth_client.get_product_ticker(product_id=currency3)
        print(newData3)
        currentPrice3 = newData3['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break
    time.sleep(1)


    
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("ids for currencies")
    print(specificID)
    print(specificID1)
    print(specificID2)
    print(specificID3)
    #time.sleep(1)
    print('\n')

    # The amount of currency owned
    owned = float(auth_client.get_account(specificID)['available'])
    owned1 = float(auth_client.get_account(specificID1)['available'])
    owned2 = float(auth_client.get_account(specificID2)['available'])
    owned3 = float(auth_client.get_account(specificID3)['available'])


    # The value of the cryptourrency in USD
    possibleIncome = (float(currentPrice) * owned)
    possibleIncome1 = (float(currentPrice1) * owned1)
    possibleIncome2 = (float(currentPrice2) * owned2)
    possibleIncome3 = (float(currentPrice3) * owned3)

    # This is where all the functions do all the math
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("Coppock function / BuySell stats")

    # Calculate the rate of change 11 and 14 units back, then sum them
    CoppockFormula(price)
    coppockres = CoppockFormula.variable
    statscoppock = coppockres
    print(currency)
    print(coppockres)
    BuySell(buy, coppockres, currency, funding, currentPrice, possibleIncome, funding, owned, funding)
    funding = BuySell.variable
    buy = buy_var

    CoppockFormula(price1)
    coppockres = CoppockFormula.variable
    print(currency1)
    print(coppockres)
    statscoppock1 = coppockres
    BuySell(buy1, coppockres, currency1, funding1, currentPrice1, possibleIncome1, funding1, owned1, funding1)
    buy1 = buy_var
    funding1 = BuySell.variable


    CoppockFormula(price2)
    coppockres = CoppockFormula.variable
    print(currency2)
    print(coppockres)
    statscoppock2 = coppockres
    BuySell(buy2, coppockres, currency2, funding2, currentPrice2, possibleIncome2, funding2, owned2, funding2)
    buy2 = buy_var
    funding2 = BuySell.variable

    CoppockFormula(price3)
    coppockres = CoppockFormula.variable
    statscoppock3 = coppockres
    print(currency3)
    print(coppockres)
    BuySell(buy3, coppockres, currency3, funding3, currentPrice3, possibleIncome3, funding3, owned3, funding3)
    buy3 = buy_var
    funding3 = BuySell.variable
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    #time.sleep(4)

    # Printing here to make the details easier to read in the terminal
    print("iteration number", iteration)

    # Print the details for reference
    stats(currentPrice, funding, owned, currency, statscoppock)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    stats(currentPrice1, funding1, owned1, currency1, statscoppock1)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    stats(currentPrice2, funding2, owned2, currency2, statscoppock2)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    stats(currentPrice3, funding3, owned3, currency3, statscoppock3)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    # Could make this a table and have an unlimited amount of variables to calculate :)
    print('Total invested in currencies: $' + str(abs(int(funding + funding1 + funding2 + funding3) - int(initInvestment))))
    print('Initial investment total: $' + str(initInvestment))
    # Wait for however long the period variable is before repeating
    time.sleep(period)
    iteration += 1
    # I couldn't make the break function stay in the BuySell function, so it goes here.
    if sellstop == True:
        break