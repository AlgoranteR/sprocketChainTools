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
        'rawTransactions': {},                          #dict   - {transaction id : raw/'on-chain' transaction data}
        'txnRounds': {},
        'groups': {},                             
        'counts':{'payC' : 0, 'keyregC' : 0, 'acfgC' : 0, 'axferC' : 0, 'afrzC' : 0, 'applC' : 0, 'feesC' : 0, 'sentC' : 0, 'receivedC' : 0,
            'txnWithInnerC' : 0, 'innerTxnC' : 0, 'innerWithInnerC' : 0, 'inInnerTxnC' : 0, 'groupedTxns' : 0}
        }


####                Fetch and store wallet transactions
#
#   collect transactions using requestHandling module
#   count existing stored txns, add received data, then count total stored txns.

fetchTxns = False       #False will bypass txn update. For testing.
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

### If local txn DB empty, or the user asks, update the local txn DB
if len(db['rawTransactions']) == 0 or (fetchTxns == True and input('Would you like to request a transaction update? (Y/N): ').upper() == 'Y'):
    fetchTxns()
else: print('Skipping update')

####                Populate local dbs
db['counts']['groupedTxns'] = 0

for txnID in db['rawTransactions']:
    ##                  txn Rounds

    txnRound = str(db['rawTransactions'][txnID]['confirmed-round'])
    if txnRound in db['txnRounds'] and txnID not in db['txnRounds'][txnRound]:
    #If this txn Round is already in the DB but this txn is missing, add it.
        roundList = db['txnRounds'][txnRound]
        roundList.append(txnID)
        db['txnRounds'][txnRound] = roundList
    else:
    #Add this txns Round and this txn to that round
        db['txnRounds'][txnRound] = [txnID]

    ##                  txn Groups
    
    if 'group' in db['rawTransactions'][txnID]: #filter out ungrouped txns
        db['counts']['groupedTxns'] += 1
        groupID = db['rawTransactions'][txnID]['group']
        if groupID in db['groups'] and txnID not in db['groups'][groupID]:
        #If this groupID is already in rKdb, but not this txn, add it.
            groupList = db['groups'][groupID]
            groupList.append(txnID)
            db['groups'][groupID] = groupList
        else:
        #New group, add it and this txn.
            db['groups'][groupID] = [txnID]


    ##                  txn type Details
    receiver = ''
    if db['rawTransactions'][txnID]['tx-type'] == 'pay':
        txnDetails = db['rawTransactions'][txnID]['payment-transaction']
        receiver = txnDetails['receiver']
        db['counts']['payC'] += 1
    elif db['rawTransactions'][txnID]['tx-type'] == 'appl':
        txnDetails = db['rawTransactions'][txnID]['application-transaction']
        db['counts']['applC'] += 1
    elif db['rawTransactions'][txnID]['tx-type'] == 'axfer':
        txnDetails = db['rawTransactions'][txnID]['asset-transfer-transaction']
        receiver = txnDetails['receiver']
        db['counts']['axferC'] += 1
    elif db['rawTransactions'][txnID]['tx-type'] == 'keyreg':
        txnDetails = db['rawTransactions'][txnID]['keyreg-transaction']
        db['counts']['keyregC'] += 1
    elif db['rawTransactions'][txnID]['tx-type'] == 'acfg':
        txnDetails = db['rawTransactions'][txnID]['asset-config-transaction']
        db['counts']['acfgC'] += 1
    elif db['rawTransactions'][txnID]['tx-type'] == 'afrz':
        txnDetails = db['rawTransactions'][txnID]['asset-freeze-transaction']
        db['counts']['afrzC'] += 1

    sender = db['rawTransactions'][txnID]['sender']
    if sender == db['wallet']:
        db['counts']['sentC'] += 1
        db['counts']['feesC'] += db['rawTransactions'][txnID]['fee']
    elif receiver == db['wallet']:
        db['counts']['receivedC'] += 1
    
    ##                  inner transactions
    if 'inner-txns' in db['rawTransactions'][txnID]:
        #print(txn)
        db['counts']['txnWithInnerC'] += 1
        for innerTxn in db['rawTransactions'][txnID]['inner-txns']:
            db['counts']['innerTxnC'] += 1
            #print(innerTxn['tx-type'])
            #print('-')
            if 'inner-txns' in innerTxn:
                db['counts']['innerWithInnerC'] += 1
                for inInnerTxn in innerTxn['inner-txns']:
                    db['counts']['inInnerTxnC'] += 1
                    #print('inInner')
                    #print(inInnerTxn['tx-type'])
        #print(db['rawTransactions'][txn]['inner-txns'])
        #print('\n')
    

    ##                  participation rewards


####                Print interesting data
print('\nWallet Stats:')
print('Total transactions: ' + str(len(db['rawTransactions'])))
print('Number of rounds containing transactions: ' + str(len(db['txnRounds'])))
print('Average number of transactions per round: ' + str(len(db['rawTransactions']) / len(db['txnRounds'])))
print('Number of singular transations: ' + str(len(db['rawTransactions']) - db['counts']['groupedTxns']))
print('Number of grouped transactions: ' + str(db['counts']['groupedTxns']))
print('Number of transction groups: ' + str(len(db['groups'])))
print('Average number of transactions per group: ' + str(db['counts']['groupedTxns'] / len(db['groups'])))
print('\nTransaction types:')
print('Payments: ' + str(db['counts']['payC']))
print('Key Regs: ' + str(db['counts']['keyregC']))
print('Asset Configs: ' + str(db['counts']['acfgC']))
print('Asset Transfers: ' + str(db['counts']['axferC']))
print('Asset Freezes: ' + str(db['counts']['afrzC']))
print('Application Transactions: ' + str(db['counts']['applC']))
print('\nTransactions sent: ' + str(db['counts']['sentC']))
print('Transactions received: ' + str(db['counts']['receivedC']))
print('Transaction fees paid: ' + str(db['counts']['feesC'] / 1000000) + ' ALGO')
print('Number of transactions containing inner transactions: ' + str(db['counts']['txnWithInnerC']))
print('Number of inner transactions: ' + str(db['counts']['innerTxnC']))
print('Number of inner transactions that contain inner transactions: ' + str(db['counts']['innerWithInnerC']))
print('Number of inner transactions inside inner transactions: ' + str(db['counts']['inInnerTxnC']))

####                Store data
dbJson = json.dumps(db)
outFile = open('db.json', 'w')
outFile.write(dbJson)
outFile.close()

####                Thanks
print('\nThank you for using sprocketChainTools\n')