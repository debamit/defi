from scripts.run_transaction import borrow_dai_for_weth, get_address
from brownie import accounts, network, Contract, config, Wei, interface

# owner = accounts[0]


def test_borrow_dai_for_weth():
    borrow_dai_for_weth(Wei("10 ether"), 10000, accounts[0])
    _dai_token = Contract.from_explorer(get_address("dai"))
    assert _dai_token.balanceOf(accounts[0].address) == 10000
