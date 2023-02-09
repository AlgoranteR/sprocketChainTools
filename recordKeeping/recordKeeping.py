####                Imports
import modules.requestHandling as requestHandling
import json

####                Welcome
print('\n\nWelcome to sprocketChainTools - Algorand RecordKeeping. Built by HashingSlash\n\n')


####                Load data
try:
    inFile = open('db.json', 'r')
    db = json.load(inFile)
    inFile.close()
    print('Loaded database')
except IOError: #database load failed. prompt user to input wallet address to init new database
####                Init data
#   Using db as a main dictionary to hold all relevant data as sub-dictionaries.
    print('Init new database')
    db = {'wallet':input('Paste wallet address: '),     #str    - wallet public key (address)
        'rawTransactions': {},
        'txnRounds': {},
        'groups': {}}                             #dict   - {transaction id : raw/'on-chain' transaction data}


####                Fetch and store wallet transactions
#
#   collect transactions using requestHandling module
#   count existing stored txns, add received data, then count total stored txns.

skipTxnFetch = False
def fetchTxns():
    #Could use improvement.
    incomingTxns = requestHandling.reqTxns(db['wallet'], 'first')
    #--     return {'txns':txnJson['transactions'],'token':token}
    preRunCount = len(db['rawTransactions'])
    db['rawTransactions'] = requestHandling.addNewTxns(incomingTxns, db['rawTransactions'])
    #--     returns txnDB with new txns added to 
    newCount = len(db['rawTransactions']) - preRunCount
    while newCount != 0:
        incomingTxns = requestHandling.reqTxns(db['wallet'], incomingTxns['token'])
        preRunCount = len(db['rawTransactions'])
        db['rawTransactions'] = requestHandling.addNewTxns(incomingTxns, db['rawTransactions'])
        newCount = len(db['rawTransactions']) - preRunCount
    else: print('Finished fetching transactions.\n')


if len(db['rawTransactions']) == 0 or (skipTxnFetch == False and input('Would you like to request a transaction update? (Y/N): ').upper() == 'Y'):
    fetchTxns()
else: print('Skipping update')

####                Populate local dbs
payC = 0
keyregC = 0
acfgC = 0
axferC = 0
afrzC = 0
applC = 0

groupedTxns = 0
for txn in db['rawTransactions']:
    ##                  txn Rounds

    txnRound = str(db['rawTransactions'][txn]['confirmed-round'])
    if txnRound in db['txnRounds'] and txn not in db['txnRounds'][txnRound]:
    #If this txn Round is already in the DB but this txn is missing, add it.
        roundList = db['txnRounds'][txnRound]
        roundList.append(txn)
        db['txnRounds'][txnRound] = roundList
    else:
    #Add this txns Round and this txn to that round
        db['txnRounds'][txnRound] = [txn]

    ##                  txn Groups

    if 'group' in db['rawTransactions'][txn]: #filter out ungrouped txns
        groupedTxns += 1
        groupID = db['rawTransactions'][txn]['group']
        if groupID in db['groups'] and txn not in db['groups'][groupID]:
        #If this groupID is already in rKdb, but not this txn, add it.
            groupList = db['groups'][groupID]
            groupList.append(txn)
            db['groups'][groupID] = groupList
        else:
        #New group, add it and this txn.
            db['groups'][groupID] = [txn]

    ##                  txn Types

        if db['rawTransactions'][txn]['tx-type'] == 'pay':
            txnDetails = db['rawTransactions'][txn]['payment-transaction']
            payC += 1
        elif db['rawTransactions'][txn]['tx-type'] == 'keyreg':
            txnDetails = db['rawTransactions'][txn]['keyreg-transaction']
            keyregC += 1
        elif db['rawTransactions'][txn]['tx-type'] == 'acfg':
            txnDetails = db['rawTransactions'][txn]['asset-config-transaction']
            acfgC += 1
        elif db['rawTransactions'][txn]['tx-type'] == 'axfer':
            txnDetails = db['rawTransactions'][txn]['asset-transfer-transaction']
            axferC += 1
        elif db['rawTransactions'][txn]['tx-type'] == 'afrz':
            txnDetails = db['rawTransactions'][txn]['asset-freeze-transaction']
            afrzC += 1
        elif db['rawTransactions'][txn]['tx-type'] == 'appl':
            txnDetails = db['rawTransactions'][txn]['application-transaction']
            applC += 1
        else:
            print('!!!txnDetails!!!')


####                Print interesting data
print('\nWallet Stats:')
print('Total transactions: ' + str(len(db['rawTransactions'])))
print('Number of rounds containing transactions: ' + str(len(db['txnRounds'])))
print('Average number of transactions per round: ' + str(len(db['rawTransactions']) / len(db['txnRounds'])))
print('Number of singular transations: ' + str(len(db['rawTransactions']) - groupedTxns))
print('Number of grouped transactions: ' + str(groupedTxns))
print('Number of transction groups: ' + str(len(db['groups'])))
print('Average number of transactions per group: ' + str(groupedTxns / len(db['groups'])))
print('\nTransaction types:')
print('Payments: ' + str(payC))
print('Key Regs: ' + str(keyregC))
print('Asset Configs: ' + str(acfgC))
print('Asset Transfers: ' + str(axferC))
print('Asset Freezes: ' + str(afrzC))
print('Application Transactions: ' + str(applC))

####                Store data
dbJson = json.dumps(db)
outFile = open('db.json', 'w')
outFile.write(dbJson)
outFile.close()

####                Thanks
print('\nThank you for using sprocketChainTools\n')