from scripts.helpful_scripts import get_account
from brownie import interface, config, network

def get_weth():
    account = get_account()
    weth = interface.WETH(config["networks"][network.show_active()]["weth_token"])
    txn = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    txn.wait(1)
    return txn

def main():
    get_weth()