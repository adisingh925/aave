from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import network, config, interface
from web3 import Web3

amount = Web3.to_wei(0.1, "ether")

def get_lending_pool():
    lending_pool_Address_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool_address_provider"])
    lending_pool_address = lending_pool_Address_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

def main():
    account = get_account()
    contract_address = config["networks"][network.show_active()]["weth_token"]

    if(network.show_active() in ["mainnet-fork"]):
        get_weth()

    lending_pool = get_lending_pool()
    approve_erc20(amount, lending_pool.address, contract_address, account)
    txn = lending_pool.deposit(contract_address, amount, account.address, 0, {"from": account})
    txn.wait(1)
    print("Deposited!")

    borrowable, dept = get_borrowable_data(lending_pool, account.address)
    price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    amount_dai_to_borrow = (1 / price) * (borrowable * 0.95) 
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # borrow

    borrow_txn = lending_pool.borrow(config["networks"][network.show_active()]["dai_token_address"], Web3.to_wei(amount_dai_to_borrow, "ether"), 2, 0, account.address, {"from":account})
    borrow_txn.wait(1)
    print("Successfully borrowed DAI")
    get_borrowable_data(lending_pool, account.address)

    repay_all(amount, lending_pool, account)

def repay_all(amount, lending_pool, account):
    approve_erc20(amount, lending_pool.address, config["networks"][network.show_active()]["dai_token_address"], account)
    repay_txn = lending_pool.repay(config["networks"][network.show_active()]["dai_token_address"], amount, 2, account.address, {"from": account})
    repay_txn.wait(1)
    print("You repaid borrowed money")

def approve_erc20(amount, spender, erc20_address, account):
    erc20 = interface.IERC20(erc20_address)
    txn = erc20.approve(spender, amount, {"from": account})
    txn.wait(1)
    print("Approved successfully!")
    return txn

def get_borrowable_data(lending_pool, address):
    (
      totalCollateralETH,
      totalDebtETH,
      availableBorrowsETH,
      currentLiquidationThreshold,
      ltv,
      healthFactor
    ) = lending_pool.getUserAccountData(address)

    total_collateral_eth = Web3.from_wei(totalCollateralETH, "ether")
    total_debt_eth = Web3.from_wei(totalDebtETH, "ether")
    available_borrow_eth = Web3.from_wei(availableBorrowsETH, "ether")

    print(f"you have {total_collateral_eth} deposited")
    print(f"you have {total_debt_eth} as debt")
    print(f"you have {available_borrow_eth} available to borrow")

    return (float(available_borrow_eth), float(total_debt_eth))

def get_asset_price(price_feed_address):
    txn = interface.AggregatorV3Interface(price_feed_address)
    (roundId, answer, startedAt, updatedAt, answeredInRound) = txn.latestRoundData()
    converted_price = Web3.from_wei(answer, "ether")
    print(f"The DAI/ETH price is {converted_price}")
    return float(converted_price)
    



        
