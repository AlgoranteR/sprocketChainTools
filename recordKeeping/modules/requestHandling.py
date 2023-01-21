####                Imports
import requests
import json

def reqTxns(address, nextToken): #Address to check. Token is used buy API provider to request additional transactions
    if nextToken == 'first': #For initial check and regular updating
        print('\nSending API request - Transactions')
        response = requests.get('https://algoindexer.algoexplorerapi.io/v2/accounts/'
            + address + '/transactions')
    elif nextToken != 'finished': #This is when the token contains required information. For catching up on previous transactions during init
        print('\nSending API request - Transactions')
        response = requests.get('https://algoindexer.algoexplorerapi.io/v2/accounts/'
            + address + '/transactions', params={'next': nextToken, "limit": 10000})
    elif nextToken == 'finished': return [[],{},'finished'] #Exits function, no more transactions to check on. Needed to exit while loop
    txnJson = response.json()
    if 'next-token' in txnJson: #If the API response contains a 'next-token', there may still be more transactions to request.
        token = txnJson['next-token']
        print('Token for more transations received')
    else: token = 'finished'
    #return [txnJson['transactions'], token]
    return {'txns':txnJson['transactions'],
            'token':token}

#   
def addNewTxns(reqTxnsOutput, txnDB):
    #txnDB = db['rawTransactions']
    addedCount = 0
    for txn in reqTxnsOutput['txns']:
        if txn['id'] not in txnDB:
            txnDB[txn['id']] = txn
            addedCount += 1
        else:
            return(txnDB)
    print('Current transaction total ' + str(len(txnDB)) + '. Added: ' + str(addedCount))
    return(txnDB)