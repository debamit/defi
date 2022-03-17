from brownie import accounts, network, Contract, config, Wei


class Lend:
    asset: Contract
    liability: Contract
    lending_pool: Contract
    owner: Contract

    def __init__(self, _asset, _liability, _lending_pool, _owner):
        self.asset = _asset
        self.liability = _liability
        self.lending_pool = _lending_pool
        self.owner = _owner

    def deposit(self, _amount):
        self.asset.approve(self.lending_pool, Wei(_amount), {"from": self.owner})
        self.lending_pool.deposit(
            self.asset.address,
            Wei(_amount),
            self.owner.address,
            0,
            {"from": self.owner},
        )

    def get_borrowable_data(self):
        (
            total_collateral_eth,
            total_debt_eth,
            available_borrow_eth,
            current_liquidation_threshold,
            tlv,
            health_factor,
        ) = self.lending_pool.getUserAccountData(self.owner.address)
        available_borrow_eth = Wei(available_borrow_eth).to("ether")
        total_collateral_eth = Wei(total_collateral_eth).to("ether")
        total_debt_eth = Wei(total_debt_eth).to("ether")
        print(f"You have {total_collateral_eth} worth of ETH deposited.")
        print(f"You have {total_debt_eth} worth of ETH borrowed.")
        print(f"You can borrow {available_borrow_eth} worth of ETH.")
        return (float(available_borrow_eth), float(total_debt_eth))

    def borrow(self, _amount_to_borrow):
        tx = self.lending_pool.borrow(
            self.liability.address,
            Wei(_amount_to_borrow),
            1,
            0,
            self.owner.address,
            {"from": self.owner},
        )
        tx.wait(1)
