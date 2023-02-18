from algosdk import account, mnemonic, constants

word = input("What string to find: ").upper()

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    #print("My address: {}".format(address))
    #print("My private key: {}".format(private_key))
    #print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))

def new_address():    
    details = private_key, address = account.generate_account()
    address_start = details[1][:len(word)] #LETTER COUNT HERE
    pass_phrase = mnemonic.from_private_key(details[0])
    return [address_start, details[0], details [1], pass_phrase]

details = ['']
run_count = 0


while details[0] != word:
    run_count += 1
    details = new_address()
    if details[0] == word: print(details)
    else: print(str(run_count) + ' : ' + details[0])