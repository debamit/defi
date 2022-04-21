from brownie import accounts, network, Contract, config, Wei, interface
from scripts.aave_lend import Lend


def get_address(contract_name: str):
    return config.get("networks").get(network.show_active()).get(contract_name)


def get_lending_pool():
    lending_pool_address_provider = Contract.from_explorer(
        get_address("aave_pool_addresses_provider")
    )
    lending_pool = lending_pool_address_provider.getLendingPool()
    return Contract.from_explorer(lending_pool)


def get_asset_price():
    price_feed = Contract.from_explorer(get_address("dai_eth_price"))
    return float(Wei(price_feed.latestRoundData()[1]).to("ether"))


def get_weth(_weth_token, _amount, _account):
    _weth_token.deposit({"from": _account, "value": _amount})


def get_dai_to_borrow(eth_available_to_borrow, borrow_limit=0.8):
    dai_eth_price = get_asset_price()
    return float((1 / dai_eth_price) * (eth_available_to_borrow * borrow_limit))


# Function to call to get WETH and then borrow some DIA against it using AAVE v2 
def borrow_dai_for_weth(_weth_amount, _dai_amount, owner):
    _weth_token = interface.IWeth(get_address("weth"))
    _dai_token = Contract.from_explorer(get_address("dai"))
    lp = get_lending_pool()
    if Wei(_weth_amount) > _weth_token.balanceOf(owner.address):
        get_weth(
            _weth_token,
            _amount=_weth_amount - _weth_token.balanceOf(owner.address),
            _account=owner,
        )
    lending_pool = Lend(
        _asset=_weth_token,
        _liability=_dai_token,
        _lending_pool=lp,
        _owner=owner,
    )
    lending_pool.deposit(_weth_amount)
    eth_available_to_borrow, debt_in_eth = lending_pool.get_borrowable_data()
    dai_available_to_borrow = get_dai_to_borrow(eth_available_to_borrow)
    if dai_available_to_borrow > _dai_amount:
        lending_pool.borrow(_dai_amount)
