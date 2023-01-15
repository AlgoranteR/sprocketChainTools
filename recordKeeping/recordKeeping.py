####                Imports
import modules.requestHandling as requestHandling
import json

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
        'transactions': {}}                             #dict   - {transaction id : raw/'on-chain' transaction data}


####                Fetch and store wallet transactions
#   
def addNewTxns(fetchedTxns, txnDB):
    addedCount = 0
    for txn in fetchedTxns[0]:
        if txn['id'] not in txnDB:
            txnDB[txn['id']] = txn
            addedCount += 1
        else:
            return(txnDB)
    print('Current transaction total ' + str(len(txnDB)) + '. Added: ' + str(addedCount))
    return(txnDB)

incomingTxns = requestHandling.txns(db['wallet'], 'first')
preRunCount = len(db['transactions'])
db['transactions'] = addNewTxns(incomingTxns, db['transactions'])
newCount = len(db['transactions']) - preRunCount
while incomingTxns[1] != 'finished' and newCount != 0:
    incomingTxns = requestHandling.txns(db['wallet'], incomingTxns[1])
    preRunCount = len(db['transactions'])
    db['transactions'] = addNewTxns(incomingTxns, db['transactions'])
    newCount = len(db['transactions']) - preRunCount
else: print('Finished fetching transactions. ' + str(len(db['transactions'])) + ' total\n')

for txn in db['transactions']:
    pass

####                Store data
dbJson = json.dumps(db)
outFile = open('db.json', 'w')
outFile.write(dbJson)
outFile.close()