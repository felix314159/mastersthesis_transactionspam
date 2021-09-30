import os
import random
import time
import requests
import web3
from pathlib import Path
from web3 import Web3


def run_code(opcode="FA", mainnet=True):
    """This function is based on code provided by Egli et al.

    Source:
    https://hackmd.io/@iwck0wkoSzauVnsYI0h7JA/SkyFmk4_r
    (Accessed: 2 July, 2021)

    In addition to Egli et al. experiments with opcodes
    BALANCE, EXTCODESIZE, EXTCODEHASH and STATICCALL
    I have experimented with other opcodes e.g.
    operations SLOAD, DELEGATECALL, BLOCKHASH, SSTORE,
    CREATE, CREATE2, CALL, CALLCODE, 
    """

    if opcode in ["31", "3b", "3f"]:
        reps = 1594
    elif opcode in ["fa", "f4"]:
        reps = 1586
    elif opcode in ["f1", "f2"]:
        reps = 1584
    else: # used for other opcodes I tested that arent suited for transaction spam attacks
        reps = 1500

    # generate code depending on opcode that is used 
    if opcode in ["fa", "f4", "55", "f0", "f5"]: # (construct 2)
        code = "5b" + ("60008080805a5a" + opcode + "50")*reps + "600056"

    elif opcode in ["f1", "f2"]: # (construct 3)    
        code = "5b" + ("6000808080805a5a" + opcode + "50")*reps + "600056"

    else: # opcode in ["31", "3b", "3f", "54", "40"] (construct 1)
        code = "5b" + ("5a" + opcode + "50")*reps + "600056"


    '''
    OVERVIEW OF RELEVANT EVM-OPERATIONS I COMPILED:
    ######################################################################################
    FOR BALANCE / EXTCODESIZE / EXTCODEHASH / SLOAD:

    	00000    5b                             JUMPDEST
	00001    5a                             GAS
	00002    31 / 3b / 3f / 54              BALANCE / EXTCODESIZE / EXTCODEHASH / SLOAD
	00003    50                             POP
	00004    60                             PUSH1 0x00
	00006    56                             JUMP

    ######################################################################################
    FOR STATICCALL / DELEGATECALL:

    	00000    5B                             JUMPDEST
	00001    60                             PUSH1 0x00
	00003    80                             DUP1
	00004    80                             DUP1
	00005    80                             DUP1
	00006    5a                             GAS
	00007    5a                             GAS
	00008    fa / f4                        STATICCALL / DELEGATECALL
	00009    50                             POP
	0000a    60                             PUSH1 0x00
	0000c    56                             JUMP

    ######################################################################################
    FOR CALL, CALLCODE:

        00000    5B                             JUMPDEST
        00001    60                             PUSH1 0x00
        00003    80                             DUP1
        00004    80                             DUP1
        00005    80                             DUP1
        00006    80                             DUP1
        00007    5a                             GAS
        00008    5a                             GAS
        00009    f1 / f2                        CALL / CALLCODE
        0000a    50                             POP
        0000b    60                             PUSH1 0x00
        0000d    56                             JUMP

    '''

    geth_params = [
        {
            # 1/3 of median of used gas per block of mainnet blocks [11567295, 11567314]: 4152896 Gas
            "gas":hex(random.randint(4142896,4162896)),
            # send call to any address of valid length
            "to":"0x1123581321345589144233377610987159725844"
        },
        "latest",
        {
            # temporarily overwrite code field of that address to contain the generated code
            "0x1123581321345589144233377610987159725844": {
                "code": "0x" + code
            }
        }
    ]
    
    if mainnet:
        chainId = 1
    else:
        chainId = 47
    
    # measure execution time (it is also shown in cmd, negligible difference between shown times)
    start = time.time()
    r = requests.post("http://localhost:8545", json={
        "method": "eth_call",
        "params": geth_params, "id": chainId, "jsonrpc": "2.0"
    })
    end = time.time()
    duration = end - start
    print("Execution of", str(reps), "repetitions in seconds:", duration)


'''
USAGE ON MAINNET SYNCED FULLNODE (which uses chainId "1"):

-> Host the blockchain using one of the following commands:
    with caching on (default):
   ./geth/geth --datadir . --networkid 1 --nodiscover --http --http.api "miner,ethash,personal,eth,net" --http.port 8545 --rpc.gascap 12478453

    with caching explicitely turned off:
    ./geth/geth --cache 0 --cache.database 0 --cache.trie 0 --cache.trie.journal disable --cache.gc 0 --cache.snapshot 0 --cache.noprefetch --datadir . --networkid 1 --nodiscover --http --http.api "miner,ethash,personal,eth,net" --http.port 8545 --rpc.gascap 12478453
    
-> Then to test ALL opcodes:
    main()
    
-> You can also test only one opcode using something like (3b = EXTCODESIZE):
    run_code("3b")

################################################
USAGE ON PRIVATE NETWORK (assuming a node called "ethereum" exists and chainId of blockchain is "47"):

-> Host the blockchain using the following command:
    with caching on (default):
   ./geth --datadir ./ethereum/ --networkid 47 --nodiscover --http --http.api "miner,ethash,personal,eth,net" --http.port 8545 --rpc.gascap 12478453

    with caching explicitely turned off:
    ./geth --cache 0 --cache.database 0 --cache.trie 0 --cache.trie.journal disable --cache.gc 0 --cache.snapshot 0 --cache.noprefetch --datadir ./ethereum/ --networkid 47 --nodiscover --http --http.api "miner,ethash,personal,eth,net" --http.port 8545 --rpc.gascap 12478453


-> Then to test ALL opcodes:
    main(False)
    
-> You can also test only one opcode using something like (3b = EXTCODESIZE):
    run_code("3b", False)
---------------------------
# notes:
-> the time measurements of Geth and Python can differ up to ~ 10ms
'''

def main(mainnet=True):
    """Calls multiple opcodes and measures their execution times.

    Use param True if blockchainId is 1, use False if blockchainId is 47."""
    
    opcodes = {"STATICCALL": "fa", "DELEGATECALL": "f4", "SSTORE": "55", "CREATE": "f0",
               "CREATE2": "f5", "CALL": "f1", "CALLCODE": "f2",
               "BALANCE": "31", "EXTCODESIZE": "3b", "EXTCODEHASH": "3f", "SLOAD": "54",
               "BLOCKHASH": "40"}

    for i, j in zip(opcodes, opcodes.values()):
        print(i + ":")
        try:
            run_code(j, mainnet)
            print()
        except:
            print("Execution was so slow that Python would have thrown an exception.\n")


main(True)
# run_code("f4", False)
