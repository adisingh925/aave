from brownie import network, accounts, config

def get_account(index = 0):
    if(network.show_active() in "sepolia"):
        return accounts.add(config["wallets"]["from_key"])
    elif(network.show_active() in "mainnet-fork"):
        print("index: ", index , "accounts: ", accounts[index])
        return accounts[index]