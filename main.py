import sys
from pathlib import Path
from time import sleep

if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 11):
    import tomli as tomllib
else:
    import tomllib

from web3 import Web3
from web3.contract.contract import Contract

from src.config import Config
from src.utils import readable_amount
import src.abi as abi

ETH_DECIMALS = 18

CONFIG_PATH = Path("config")
COMMON_CONFIG_PATH = CONFIG_PATH.joinpath("common.toml")
SECRETS_CONFIG_PATH = CONFIG_PATH.joinpath("secrets.toml")

config: Config = {}

for filename in CONFIG_PATH.iterdir():
    with open(filename, "rb") as file:
        config = {**config, **tomllib.load(file)}

def main():
   
    provider_arb = Web3.HTTPProvider(config["endpoint"]["arbitrum"])
    provider_eth = Web3.HTTPProvider(config["endpoint"]["ethereum"])

    w3_arb = Web3(provider=provider_arb)
    w3_eth = Web3(provider=provider_eth)

    arb_latest_block = w3_arb.eth.get_block_number()
    eth_latest_block = w3_eth.eth.get_block_number()

    bonding_manager_contract: Contract  = w3_arb.eth.contract(config["contract"]["bonding_manager"], abi=abi.BONDING_MANAGER)
    round_manager_contract: Contract  = w3_arb.eth.contract(config["contract"]["rounds_manager"], abi=abi.ROUND_MANAGER)
    lpt_token_contract: Contract = w3_arb.eth.contract(config["contract"]["lpt_token"], abi=abi.ERC_20)

    lpt_decimals = lpt_token_contract.functions.decimals().call()

    print(round_manager_contract.events)

    block = arb_latest_block
    while True:
        current_round_eth_start_block = round_manager_contract.functions.currentRoundStartBlock().call(block_identifier=block)
        
        print(current_round_start_block)
              
        pending_stake = bonding_manager_contract.functions.pendingStake(config["delegator"], 0).call(block_identifier=block)

        print(current_round_start_block, readable_amount(pending_stake, lpt_decimals))
        
        block = current_round_start_block - 1

        

    for block_no in range(config["block"]["starting"], arb_latest_block, config["block"]["step"]):
        pending_stake = bonding_manager_contract.functions.pendingStake(config["delegator"], 0).call(block_identifier=block_no)
        pending_fees = bonding_manager_contract.functions.pendingFees(config["delegator"], 0).call(block_identifier=block_no)
        print(block_no, pending_stake / 10 ** lpt_decimals, pending_fees/ 10 ** ETH_DECIMALS)
        sleep(0.1)


if __name__ == "__main__":
    main()