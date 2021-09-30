import socket
import subprocess
from subprocess import PIPE
from time import sleep, time
from web3 import Web3


def get_IP():
    """Returns the local IP address.

    Credits for this function go to user 'dlm' in
    https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    (Accessed 05/28/2021)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


def start_network(ip):
    """This function starts all nodes and the eth-stats server."""

    subprocess.Popen(["PORT=2056 WS_SECRET=asdf npm start"], shell=True,
                     stdout=PIPE, stderr=PIPE, cwd="./eth-netstats/")

    subprocess.Popen(["./geth --datadir ./ethereum \
--gcmode archive \
--networkid 47 --http.api \"txpool,miner,ethash,personal,eth,net,web3\" \
--port 30301 --http --http.corsdomain=\"http://remix.ethereum.org\" \
--rpc --rpcapi \"web3,net,eth,admin,personal\" --rpcaddr " + ip + " \
--rpcport 8545 --rpccorsdomain=\"*\" --http.port 8101 --allow-insecure-unlock \
--nat extip:" + ip + " --ethstats ethereum:asdf@" + ip + ":2056"],
                     shell=True, stdout=PIPE, stderr=PIPE)

    subprocess.Popen(["./geth --datadir ./ethereum2 \
--gcmode archive \
--networkid 47 --http.api \"txpool,miner,ethash,personal,eth,net,web3\" --port 30302 \
--http.port 8102 --nat extip:" + ip + " --ethstats ethereum2:asdf@" + ip + ":2056"],
                     shell=True, stdout=PIPE, stderr=PIPE)

    subprocess.Popen(["./geth --datadir ./ethereum3 \
--gcmode archive \
--networkid 47 --http.api \"txpool,miner,ethash,personal,eth,net,web3\" --port 30303 \
--http.port 8103 --nat extip:" + ip + " --ethstats ethereum3:asdf@" + ip + ":2056"],
                     shell=True, stdout=PIPE, stderr=PIPE)

    subprocess.Popen(["./geth --datadir ./ethereum4 \
--gcmode archive \
--networkid 47 --http.api \"txpool,miner,ethash,personal,eth,net,web3\" --port 30304 \
--http.port 8104 --nat extip:" + ip + " --ethstats ethereum4:asdf@" + ip + ":2056"],
                     shell=True, stdout=PIPE, stderr=PIPE)

    subprocess.Popen(["./geth --datadir ./ethereum5 \
--gcmode archive \
--networkid 47 --http.api \"txpool,miner,ethash,personal,eth,net,web3\" --port 30305 \
--http.port 8105 --nat extip:" + ip + " --ethstats ethereum5:asdf@" + ip + ":2056"],
                     shell=True, stdout=PIPE, stderr=PIPE)


ip = get_IP()
start_network(ip)
