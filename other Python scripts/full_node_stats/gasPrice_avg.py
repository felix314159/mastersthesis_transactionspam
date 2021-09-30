import web3
from web3 import Web3


def get_avg_gasPrice(node, blockNumber):
    """Helper function to extract gasPrice and calculate arith average."""
    
    # get all transactions mined in this block
    block = node.eth.get_block('latest')['transactions']

    # extract txs
    tx_list = []
    for i in block:
        tx_list.append(node.toHex(i))

    # extract gasPrices of transactions
    gasPrice_list = []
    for i in tx_list:
        # get gasPrice in wei
        gasPrice_list.append(node.eth.getTransaction(i)['gasPrice'])

    # return arithmetic average of all gasPrices paid in this block
    amount = len(gasPrice_list)
    total = 0

    for i in gasPrice_list:
        total += int(i)
    avg_gasPrice = int(total/amount)

    return avg_gasPrice


def main():
    """Returns the arith average of all arith averages
       of gasPrices paid in all transactions of last 20 blocks.

       Overview:
       -> Gets all transactions in block
       -> Gets all gasPrices paid for these transactions.
       -> Calculates arithmetic average of these gasPrices.
       (Repeat this for last 20 blocks)

       -> Then with these 20 arithmetic averages:
           -> Calculate arithmetic average.
    """
    
    # get last 20 block numbers
    node = Web3(Web3.IPCProvider('geth.ipc'))
    block_number = node.eth.get_block('latest')['number']

    numbers = []
    for i in range(block_number-19, block_number+1):
        numbers.append(i)

    # get_avg_gasPrice() of all these blocks
    avg_gasPrices = []
    for i in numbers:
        result = get_avg_gasPrice(node, i)
        avg_gasPrices.append(result)

    # uncomment below to see avg gasPrice of every block
    # print(avg_gasPrices)

    # get arith average of all these arith averages
    amount = len(avg_gasPrices)
    total = 0

    for i in avg_gasPrices:
        total += int(i)
    final_result = int(total/amount)

    print(final_result, " wei <->\n", final_result/(10**9), " gwei", sep="")
    return final_result


main()
