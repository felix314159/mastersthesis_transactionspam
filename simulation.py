import json
import os
import subprocess
from ast import literal_eval
from binascii import b2a_hex
from pathlib import Path
from pprint import pprint
from random import choice, getrandbits, randint, uniform
from solc import compile_standard
from subprocess import PIPE
from time import sleep, time
from web3 import Web3


def append_address_to_file(address):
    """Writes account addresses to file."""

    with open("addresses.txt", "a") as file:
        file.write(address + "\n")


def block_info_gas(a, b):
    """Lists gasLimit and gasUsed of all blocks in given intervall."""
    for i in range(a, b+1):
        block_info = node_ethereum.eth.get_block(i)
        gasLimit = block_info['gasLimit']
        gasUsed = block_info['gasUsed']
        miner = block_info['miner']
        print("Block", i, "\ngasLimit: ", gasLimit,
              "\ngasUsed: ", gasUsed, "\nminer: ", miner, "\n")


def calculate_data():
    '''Calculates the value required for the data field of a transaction.

    If you want to transact to a Smart Contract, you need to specify
    which function you want to call in that contract with which
    parameters using a data parameter. In this function, I hash the name
    of the to-be-called function with keccak256, then take the first
    4 bytes (8 hex chars) and then add 64 zeroes (since i dont want to
    pass any parameters to main()). Since most Smart Contracts I have
    made use main() without any additional parameters
    I can hardcode this here.
    '''
    # method name: main()
    data = Web3.toHex(Web3.soliditySha3(['string'],
                                        ["main()"]))[:10] + ("0" * 64)
    return data


def deploy_contract(node, contract_name, value=0, spam_creation=False,
                    measure_time=False, runs=20):
    """Compiles, deploys and (optionally) runs a given contract.

    Example call: deploy_contract("node_ethereum", "contract3.sol"

    This function expects the in Solidity defined name of the
    contract to be "Contract". The naming scheme for the actual
    contracts sol file is: "contract<x>.sol" where <x> is
    replaced with a natural number.
    """

    # reminder: do not use eval in a production setting,
    # however in this case it actually is the best readable solution
    address = eval(node + "_address")

    # unlock the account first
    eval(node).geth.personal.unlockAccount(address, "asdf", 999999)

    compiled_sol = compile_standard(
        {"language": "Solidity", "sources": {"Contract.sol":
                                                {"content": read_file(contract_name)}},
                                 "settings": {"outputSelection":
                                             {"*": {"*": ["metadata",
                                                          "evm.bytecode",
                                                          "evm.bytecode.sourceMap"]}}}
        # allow solc to read from current dir to read library files
        }, allow_paths=path)

    # set default account or you will get error account not found
    eval(node).eth.default_account = address

    bytecode = compiled_sol['contracts']['Contract.sol']['Contract']['evm']['bytecode']['object']
    abi = json.loads(compiled_sol['contracts']['Contract.sol']['Contract']['metadata'])['output']['abi']
    Contract = eval(node).eth.contract(abi=abi, bytecode=bytecode)

    # broadcast transaction and wait for transaction to be mined
    if spam_creation:
        # supply wei using value parameter in order to call payable functions
        tx_hash = Contract.constructor().transact({"from": address,
                                                   "value": value})
    # try: setting custom gas value for payable contract
    # if that does not work: transact without setting custom gas
    else:
        try:
            tx_hash = Contract.constructor(eval(node).eth.coinbase,
                                           50000000).transact()
        except:
            # if no gas value is given then it will be chosen
            # by an implicit call of eth.estimate_gas()
            tx_hash = Contract.constructor().transact()

    start_mining()
    tx_receipt = eval(node).eth.wait_for_transaction_receipt(tx_hash)
    stop_mining()

    # get contract address
    address = tx_receipt.contractAddress

    # permanently save contract address and abi
    with open(contract_name[:-4] + "_address.txt", 'w') as file:
            file.write(address)

    with open(contract_name[:-4] + "_abi.txt", 'w') as file:
            # convert list to string before writing to file
            file.write(str(abi))

    contract = eval(node).eth.contract(address=address, abi=abi)

    # optionally measure the average execution time
    # of the contracts main function in x runs
    if measure_time:
        total_run_time = 0
        for i in range(runs):
            start = time()
            output = contract.functions.main().call()
            end = time()
            total_run_time += end-start
        average_run_time = total_run_time / runs
        print("\nAverage execution time in", runs,
              "runs:", average_run_time*1000, " ms")

    if spam_creation:
        print("1 Wei has successfully been sent out\
to every account in the specified interval.")

    return contract, abi


def estimate_function_gas_cost(contract_name):
    """Estimates gas costs of given function in a contract."""

    # import contract abi and address from file
    if os.path.exists(contract_name[:-4] + "_address.txt"):
        with open(contract_name[:-4] + "_address.txt") as file:
            address = file.read()

    if os.path.exists(contract_name[:-4] + "_abi.txt"):
        with open(contract_name[:-4] + "_abi.txt") as file:
            abi = literal_eval(file.read())

    contract = node_ethereum.eth.contract(address=address, abi=abi)
    # adjust main() to whatever function you want to estimate gas for
    print("Estimated gas needed to call function : ",
          contract.functions.main().estimateGas())

    '''
    # alternative way to estimate gas
    data = calculate_data()
    # adjust 'to' address to contract address
    gas_cost = node_ethereum.eth.estimate_gas({'to': '0x59678474277A688075Ea1b1ce5f7f3b14304464A', 'data': data})
    print(gas_cost)
    '''


def get_contract_from_file(contract_name):
    """Reads contract address and contract abi from file."""

    if os.path.exists(contract_name[:-4] + "_address.txt"):
        with open(contract_name[:-4] + "_address.txt") as file:
            address = file.read()

    if os.path.exists(contract_name[:-4] + "_abi.txt"):
        with open(contract_name[:-4] + "_abi.txt") as file:
            abi = literal_eval(file.read())

    return node_ethereum.eth.contract(address=address, abi=abi)


def get_contract_functions(abi):
    """Given a contracts ABI, this function returns a
    list of all functions in that contract."""

    functions = []
    for i in abi:
        if i['type'] == 'function':
            functions.append(i['name'])

    return functions


def get_existing_accounts():
    """Goes through every block and creates a txt file that
    contains every address that was sent ETH and therefore
    had a non-zero balance at some point. Used to approximate
    number of active accounts (however accounts that received
    ETH from a Smart Contract are not listed!)"""

    # delete file if it already exists so that there will be no duplicates
    if os.path.exists("addresses.txt"):
        os.remove("addresses.txt")

    start = 0
    # get highest block number
    end = node_ethereum.eth.get_block('latest')['number']
    address_list = []
    for k in range(start, end+1):
        transactions = node_ethereum.eth.getBlock(k)['transactions']
        if transactions != []:
            for tx_id in transactions:
                # check if ether was sent
                value = get_transaction_info(tx_id)['value']
                if value != 0:
                    # if ether was sent then this address had a positive
                    # balance at some point and address will be saved in file
                    address = get_transaction_info(tx_id)['to']
                    if address is not None:
                        # write address to file
                        address_list.append(address)
    # remove all duplicates from file
    address_list = list(set(address_list))
    # write elements to file
    for i in address_list:
        append_address_to_file(i)
    print("Number of unique EOA addresses a node\
has transacted to: ", len(address_list))


def get_keystore_file(node_string):
    """Returns the relative path of the keystore file of a given node."""

    path = str(Path().absolute())

    keystore_path = path + "/" + node_string + "/keystore/"

    keystore_file = os.listdir(keystore_path)[0]
    return keystore_path + keystore_file


def get_node_address(node):
    """Returns the hex address of a node.

    Example usage: print(get_node_address("node_ethereum"))
    """

    try:
        return eval(node).geth.personal.list_accounts()[0]
    except:
        return "This node does not exist. \
Try node_ethereum, node_ethereum2, node_ethereum3, \
node_ethereum4 or node_ethereum5."


def get_transactions_between(i, j):
    """Prints all transactions that occured in the given
    block interval and counts amount of blocks that
    contained transactions.

    Example usage: get_transactions_between(700, 720)"""

    counter = 0
    for k in range(i, j+1):
        transactions = node_ethereum.eth.getBlock(k)['transactions']
        if transactions != []:
            print("Block", k, "contains transactions:", transactions)
            counter += 1
        else:
            print("Block", k, "is empty.")
    print("\nTotal amount of blocks that contain at\
least one transaction: ", counter)


def get_transaction_info(tx_hash):
    """Give the hash of a transaction, returns more
    details of that transaction.

    Find out a valid tx_hash using the
    get_transactions_between(i, j) function
    and then call this function with that value."""

    return node_ethereum.eth.getTransaction(tx_hash)


def hello_world_contract_example():
    """Deploys an example contract and calls its functions
    to verify that everything works correctly."""

    # deploy hello world contract
    contract, abi = deploy_contract("node_ethereum", "contract1.sol")

    # call the greet function
    print(contract.functions.greet().call())

    # call the setGreeting function
    tx_hash = contract.functions.setGreeting("it works!").transact()
    start_mining()
    tx_receipt = node_ethereum.eth.wait_for_transaction_receipt(tx_hash)
    stop_mining()

    # call the greet function again
    print(contract.functions.greet().call())
    return contract, abi


def measure_contract_execution_time():
    """Measures the average execution time of a contract by
    calling it multiple times and calculating
    the arithmetic average."""

    # do multiple runs and calculate arithmetic avg later
    runs = 3
    
    contracts = {"contract3016.sol":"EXTCODESIZE",
                 "contract3018.sol":"BALANCE",
                 "contract3019.sol":"EXTCODEHASH",
                 "contract3020.sol":"STATICCALL",
                 "contract3021.sol":"SLOAD",
                 "contract3025.sol":"DELEGATECALL",
                 "contract3026.sol":"CALL"}

    for i, j in zip(contracts.keys(), contracts.values()):
 
        # same available gas same as in eth_call experiments
        # on Berlin fork this gas is burned very quickly
        gas_value = randint(4142896,4162896)

        # read required contract info from file
        contract = get_contract_from_file(i)

        # measure time while executing
        a = time()
        for i in range(runs):
            contract.functions.main().call({'gas': gas_value})
        b = time()
        avg = (b - a)/runs
        # calculate avg
        print("Average execution time of", j, "contract in",
              str(runs), "runs: ", round(avg, 2), "seconds.")


def print_balance_contract_creation(number):
    """Returns the balance of an account that
    was sent ETH by contract200.sol

    Since I used a for loop over integers e.g. 42
    I can reproduce the contracts steps here to
    generate the address that was used by the contract
    as destination for the 5 wei """

    # hash the given number using keccak256
    # (both available functions produce the same result)
    hash1 = node_ethereum.toHex(node_ethereum.solidityKeccak(['uint256'],
                                                             [number]))
    '''
    Alternatively you can use soliditySha3() it created the same
    results as solidityKeccak() for the tests I conducted
    # hash2 = node_ethereum.toHex(node_ethereum.soliditySha3(['uint256'],
                                                             [number]))
    # print(hash1 == hash2)
    '''

    # keccak256 hash is 64 char hex (32 bytes) but addresses are 40 char hex
    # (20 bytes), first convert then transform to checksum address
    checksum_address = node_ethereum.toChecksumAddress("0x" + hash1[26:])

    # look up the balance of this address
    balance = node_ethereum.eth.get_balance(checksum_address)
    print(balance)


def print_balances(miners_only=True):
    """Returns account balances in Ether.

    This includes the balances of all five nodes I used as well
    as the balances of the addresses that were sent ETH by
    one of these nodes."""

    if miners_only:
        print("Node Ethereum:", node_ethereum.eth.get_balance(
            node_ethereum_address) / 10**18, "ETH")
        print("Node Ethereum2:", node_ethereum.eth.get_balance(
            node_ethereum2_address) / 10**18, "ETH")
        print("Node Ethereum3:", node_ethereum.eth.get_balance(
            node_ethereum3_address) / 10**18, "ETH")
        print("Node Ethereum4:", node_ethereum.eth.get_balance(
            node_ethereum4_address) / 10**18, "ETH")
        print("Node Ethereum5:", node_ethereum.eth.get_balance(
            node_ethereum5_address) / 10**18, "ETH")
    else:
        # print the balances of other known addresses that
        # received ETH from at least one of the nodes
        if os.path.exists("addresses.txt"):
            with open("addresses.txt") as file:
                address = [line.rstrip('\n') for line in file]
        for i in address:
            print(i, node_ethereum.eth.get_balance(i) / 10**18, "ETH")


def print_constructor_events(contract_name):
    """Goes through all blocks and returns a list of all
    events called "constructor_event" emitted by a contract.

    Example usage: print_constructor_events("contract1.sol")
    """

    contract = get_contract_from_file(contract_name)
    try:
        custom_filter = contract.events.constructor_event.createFilter(fromBlock=0, toBlock='latest')

        eventlist = custom_filter.get_all_entries()
        print(eventlist)
    except:
        print("No event called \"constructor_event\" found in", contract_name)


def read_file(contract_name):
    """Reads data from a text file.
    Used e.g. for reading contracts before compiling them."""

    f = open(contract_name, "r", encoding='utf8')
    return f.read()


def return_account_nonces(node=""):
    """Returns the nonces of all five nodes.

    If you want to automate the process of sending many
    transactions from a node it can happen that a new transaction
    with the some nonce is broadcasted before a previous
    transaction with the same nonce was included in a block.
    Then, since the nonces are equal, the transaction with the
    higher gasPrice would overwrite the other transaction which
    can slow the process of automated transactions down if this
    happens frequently. Therefore, this function can be used to
    check the current nonce and create a new transaction with
    nonce + 1 so that the old transaction that was not mined
    yet is not overwritten.
    """

    nonce_dict = {'node_ethereum': node_ethereum.eth.
                  getTransactionCount(node_ethereum_address),
                  'node_ethereum2': node_ethereum.eth.
                  getTransactionCount(node_ethereum2_address),
                  'node_ethereum3': node_ethereum.eth.
                  getTransactionCount(node_ethereum3_address),
                  'node_ethereum4': node_ethereum.eth.
                  getTransactionCount(node_ethereum4_address),
                  'node_ethereum5': node_ethereum.eth.
                  getTransactionCount(node_ethereum5_address)}

    if node == "":
        return nonce_dict
    else:
        return nonce_dict[node]


def send_transaction(from_node, to_string, data, value=13371337, gas=2000000):
    """Automates the process of transacting ETH between nodes."""

    from_address = eval(from_node + "_address")

    # check if this function was called with node name
    # like "node_ethereum" or with an address like 0x...
    if to_string[:2] != "0x":
        # if function was called with node name then find out its address
        to_address = get_node_address(to_string)
    else:
        to_address = to_string

    # if the user wants to call some Smart Contract function instead
    # of just transferring wei between accounts
    if data:
        # call the main() function of the Smart Contract
        # without any additional parameters
        data = calculate_data()
    else:
        # leave the data field empty if it's just a
        # wei transaction between two EOA's
        data = ""

    # define transaction
    transaction = {'to': to_address,
                   # value in wei
                   'value': value,
                   'gas': gas,
                   'gasPrice': node_ethereum.eth.gasPrice,
                   'nonce': return_account_nonces(from_node),
                   # chainId = 47 as defined in startup script
                   'chainId': node_ethereum.eth.chain_id,
                   'data': data}

    '''
    Depending on from_node pick the correct keystore path
    -> this is more code but it would also be
       more secure in a real setting than just
       unlocking the account
    '''

    if from_node == "node_ethereum":
        keystore_path = get_keystore_file("ethereum")
    elif from_node == "node_ethereum2":
        keystore_path = get_keystore_file("ethereum2")
    elif from_node == "node_ethereum3":
        keystore_path = get_keystore_file("ethereum3")
    elif from_node == "node_ethereum4":
        keystore_path = get_keystore_file("ethereum4")
    elif from_node == "node_ethereum5":
        keystore_path = get_keystore_file("ethereum5")

    else:
        return

    # get private key to sign transaction later
    with open(keystore_path) as key_file:
        encrypted = key_file.read()
        # all nodes have the same password
        key = node_ethereum.eth.account.decrypt(encrypted, 'asdf')

    # sign transaction using private key
    signed = node_ethereum.eth.account.sign_transaction(transaction, key)

    # send raw transaction (with local nodes you have to use RAW transactions)
    tx_hash = node_ethereum.eth.send_raw_transaction(signed.rawTransaction)

    start_mining()
    tx_receipt = node_ethereum.eth.wait_for_transaction_receipt(tx_hash)
    stop_mining()
    print("Transaction has been mined successfully.")


def start_mining():
    """Starts mining on all five nodes."""

    node_ethereum.geth.miner.start(1)
    node_ethereum2.geth.miner.start(1)
    node_ethereum3.geth.miner.start(1)
    node_ethereum4.geth.miner.start(1)
    node_ethereum5.geth.miner.start(1)


def stop_mining():
    """Stops mining of all five nodes."""

    node_ethereum.geth.miner.stop()
    node_ethereum2.geth.miner.stop()
    node_ethereum3.geth.miner.stop()
    node_ethereum4.geth.miner.stop()
    node_ethereum5.geth.miner.stop()


def transaction_spam_prep(tx_amount=5):
    """Automates the process of sending ETH between accounts by
    picking random sender of set and generating random receiver addresses.

    The idea is to automate transactions so that the state of the
    blockchain can get bloated over time. This function is not the
    actual transaction spam attack, it is just a preperation for it.
    Only when the state of the blockchain is large enough, then Smart
    Contract operations like EXTCODESIZE will be comparably slow.
    """

    # tx_amount = how many transactions to random accounts you want to produce
    i = 0
    nodes = ["node_ethereum", "node_ethereum2", "node_ethereum3",
             "node_ethereum4", "node_ethereum5"]
    while i < tx_amount:
        # pick random node
        from_node = choice(nodes)

        # generate a random hex address, it took me a long time
        # to find out i need to use toChecksumAddress here
        try:
            to_node = str(node_ethereum.
                          toChecksumAddress(hex(getrandbits(160))))
        except:
            # sometimes there can occur a conversion error with
            # the checksum function, just generate new address and try again
            continue

        # how much wei is sent
        value = round(uniform(1, 100))

        # broadcast transaction but dont wait until its mined
        # before you send the next transaction
        try:
            send_transaction(from_node, to_node, False, value)
        except:
            continue

        i += 1


# get current path
path = str(Path().absolute())

# connect to the ipc of a running node
# (node names must match those from my tutorial)
node_ethereum = Web3(Web3.IPCProvider(path + '/ethereum/geth.ipc'))
node_ethereum2 = Web3(Web3.IPCProvider(path + '/ethereum2/geth.ipc'))
node_ethereum3 = Web3(Web3.IPCProvider(path + '/ethereum3/geth.ipc'))
node_ethereum4 = Web3(Web3.IPCProvider(path + '/ethereum4/geth.ipc'))
node_ethereum5 = Web3(Web3.IPCProvider(path + '/ethereum5/geth.ipc'))

# get node addresses (needed for some function calls)
node_ethereum_address = node_ethereum.geth.personal.list_accounts()[0]
node_ethereum2_address = node_ethereum2.geth.personal.list_accounts()[0]
node_ethereum3_address = node_ethereum3.geth.personal.list_accounts()[0]
node_ethereum4_address = node_ethereum4.geth.personal.list_accounts()[0]
node_ethereum5_address = node_ethereum5.geth.personal.list_accounts()[0]

# set etherbase (defines where rewards from mined blocks go to)
node_ethereum.geth.miner.setEtherbase(node_ethereum_address)
node_ethereum2.geth.miner.setEtherbase(node_ethereum2_address)
node_ethereum3.geth.miner.setEtherbase(node_ethereum3_address)
node_ethereum4.geth.miner.setEtherbase(node_ethereum4_address)
node_ethereum5.geth.miner.setEtherbase(node_ethereum5_address)


'''
EXAMPLES FOR PRIVATE BERLIN BLOCKCHAIN:
------------
Function calls used for deploying the different contracts:

    deploy_contract("node_ethereum", "contract3016.sol")
    deploy_contract("node_ethereum", "contract3017.sol")
    deploy_contract("node_ethereum", "contract3018.sol")
    deploy_contract("node_ethereum", "contract3019.sol")
    deploy_contract("node_ethereum", "contract3020.sol")
    deploy_contract("node_ethereum", "contract3021.sol")
    deploy_contract("node_ethereum", "contract3025.sol")
    deploy_contract("node_ethereum", "contract3026.sol")
    deploy_contract("node_ethereum", "contract203.sol", 1000000, True)
--------------
To verify that the "send 1 wei to many accounts" Smart
Contract is working correctly:

    deploy_contract("node_ethereum", "contract203.sol", 1000000, True)
    print_balance_contract_creation(10)
    deploy_contract("node_ethereum", "contract203.sol", 1000000, True)
    print_balance_contract_creation(10)

The addresses that was created using 10 as seed should contain 1 wei more
with every deployment of contract203.sol
(adjust its in intervals in sol to send to other addresses)

What does Smart Contract contract203.sol do?

    # (contract does the following: loop numbers between 0-399,
    # hash them using keccak256, discard characters until the length is
    # a valid address, then send 1 wei to that address)
    # (in Python here I calculate the corresponding address of a
    # loop number so that i can check its balance,
    # its slightly more complicated here because I need to convert
    # the address into a checksum address before i can check its balance
-------------
Now check the gas costs of the main() functions of the different contracts
(do this for every contract (except contract1 or contract2
which dont a function called main) and compare the
gas needed for running the main function once)

    estimate_function_gas_cost("contract203.sol")

-> These gas estimations are inaccurate which is why I manually
calculated gas for the EVM code constructs I used in the eth_call script
in my thesis. I did this for multiple hard forks by using different
revisions of the Yellow Paper which contains a fee schedule of operations.
-----------------
Now lets send wei between accounts:
    # send 100k wei from node_ethereum to an externally owned account
    # with address 0xFeD00C1142c9e104A109c536cE141d4b2d234EC6:

    send_transaction("node_ethereum", "0xFeD00C1142c9e104A109c536cE141d4b2d234EC6", False, 100000)
------------------
Execute the main() function of some Smart Contract:
    # execute the main() function of non-payable contract2
    # which is located at address 0xc5C6C2722842b0a96E80521065777774DF094A89:

    send_transaction("node_ethereum", "0xc5C6C2722842b0a96E80521065777774DF094A89", True, 0)
-----------------
Now lets slightly bloat the state of the blockchains by doing a few
automated transactions to random addresses:

    transaction_spam_prep(3)

Now to actually bloat the state this approach is slow, especially
when considering how many transaction have been mined
on the mainnet over the years, but its a working concept that would
bloat the state if run for a very, very long time
-----------------
See details of a transaction:

    print(get_transaction_info('0xe93e14b8a6305e8bd55604a8c11dcc037432423577247bd9ada81280394f24a5'))
-----------------
Here is a list of contracts that in theory are resource-expensive and their addresses:
    contract3016.sol    0x59678474277A688075Ea1b1ce5f7f3b14304464A
    contract3017.sol    0xC8a4117dedeb0a0487AEE8b2e5755357cD247317
    contract3018.sol    0xc2F4BA7f2f7b17d22dD772319C113Efe05445a5C
    contract3019.sol    0x6122AfdDf0673a287c36E5C185B199a71D5EcE30
    contract3020.sol    0x9dD35f7c7E06683D2AEA313f7ab8052C55A906aA
    contract3021.sol    0x9FFE5ff97a0692d3853738526fA5af8c46B7F2E6
    contract3022.sol    0xeC1a3470A34A40616B6A870085fCd5CFbf06Cd9f

Transactions to the main function of these contracts trigger their execution
-> in a transaction spam attack you spam transactions to these addresses to slow other miners down
-----------------
Alternative way to measure execution time of contract without relying on measure_contract_execution_time():

runs = 3
gas_value = 9000000
contract = get_contract_from_file("contract3000.sol")
a = time()
for i in range(runs):
    contract.functions.main().call({'gas': gas_value})
b = time()
print("Average execution time of contract in", str(runs), "runs: ", (b - a)*1000/runs, "ms")
-----------------
There are many more functions in this script which
should be self-explanatory.
'''

# measure_contract_execution_time()
# deploy_contract("node_ethereum", "contract3022.sol")


