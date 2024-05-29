import tomllib

from web3 import Web3
from web3.contract.contract import Contract
from time import sleep

from config import Config
import abi

ETH_DECIMALS = 18
CONFIG_PATH = "config.toml"

def main():
    with open(CONFIG_PATH, "rb") as file:
        config: Config = tomllib.load(file)
    
    provider_arb = Web3.HTTPProvider(config["endpoint"]["arbitrum"])
    provider_eth = Web3.HTTPProvider(config["endpoint"]["ethereum"])

    w3_arb = Web3(provider=provider_arb)
    w3_eth = Web3(provider=provider_eth)

    arb_latest_block = w3_arb.eth.get_block_number()
    eth_latest_block = w3_eth.eth.get_block_number()

    bonding_manager_contract: Contract  = w3_arb.eth.contract(config["address"]["bonding_manager"], abi=abi.BONDING_MANAGER)
    round_managet_contract: Contract  = w3_arb.eth.contract(config["address"]["round_manager"], abi=abi.ROUND_MANAGER)
    lpt_token_contract: Contract = w3_arb.eth.contract(config["address"]["lpt_token"], abi=abi.ERC_20)

    lpt_decimals = lpt_token_contract.functions.decimals().call()
    
    for block_no in range(config["block"]["starting"], arb_latest_block, config["block"]["step"]):
        pending_stake = bonding_manager_contract.functions.pendingStake(config["address"]["delegator"], 0).call(block_identifier=block_no)
        pending_fees = bonding_manager_contract.functions.pendingFees(config["address"]["delegator"], 0).call(block_identifier=block_no)
        print(block_no, pending_stake / 10 ** lpt_decimals, pending_fees/ 10 ** ETH_DECIMALS)
        sleep(0.1)


if __name__ == "__main__":
    main()