import sys
from pathlib import Path
from time import sleep

if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 11):
    import tomli as tomllib
else:
    import tomllib

from web3 import Web3
from web3.contract.contract import Contract
from pandas import DataFrame
from tqdm import tqdm

from src.config import Config
import src.abi as abi

ETH_DECIMALS = 18
LIVEPEER_INIT_BLOCK = 5856411

CONFIG_PATH = Path("config")
COMMON_CONFIG_PATH = CONFIG_PATH.joinpath("common.toml")
SECRETS_CONFIG_PATH = CONFIG_PATH.joinpath("secrets.toml")

config: Config = {}

for filename in CONFIG_PATH.iterdir():
    with open(filename, "rb") as file:
        config = {**config, **tomllib.load(file)}

def main():
   
    provider_arb = Web3.HTTPProvider(config["endpoint"]["arbitrum"])

    w3_arb = Web3(provider=provider_arb)

    bonding_manager_contract: Contract  = w3_arb.eth.contract(config["contract"]["bonding_manager"], abi=abi.BONDING_MANAGER)
    round_manager_contract: Contract  = w3_arb.eth.contract(config["contract"]["rounds_manager"], abi=abi.ROUND_MANAGER)
    lpt_token_contract: Contract = w3_arb.eth.contract(config["contract"]["lpt_token"], abi=abi.ERC_20)
    tlpt_token_contract: Contract = w3_arb.eth.contract(config["contract"]["tlpt_token"], abi=abi.ERC_20)

    lpt_decimals = lpt_token_contract.functions.decimals().call()

    bonding_events = bonding_manager_contract.events.Bond().get_logs(fromBlock=LIVEPEER_INIT_BLOCK, argument_filters={'delegator': config["delegator"]})
    
    first_bonding_block = bonding_events[0]['blockNumber']

    from_block = first_bonding_block if first_bonding_block > LIVEPEER_INIT_BLOCK else LIVEPEER_INIT_BLOCK

    new_round_events = round_manager_contract.events.NewRound().get_logs(fromBlock=from_block)
    
    stake_fees_data = {
        "round": [],
        "stake": [],
        "fees": []
    }

    for event in tqdm(new_round_events, desc="Stake scraping"):
        round = event['args']['round']
        block = event['blockNumber']
        
        status = bonding_manager_contract.functions.delegatorStatus(config["delegator"]).call(block_identifier=block)

        if status == 1:
            pending_stake = bonding_manager_contract.functions.pendingStake(config["delegator"], 0).call(block_identifier=block)
        else:
            lock_id = bonding_manager_contract.functions.getDelegator(config["delegator"]).call(block_identifier=block)[-1] - 1
            pending_stake = bonding_manager_contract.functions.getDelegatorUnbondingLock(config["delegator"], lock_id).call(block_identifier=block)[0]
            
            if pending_stake == 0:
                pending_stake = tlpt_token_contract.functions.balanceOf(config['delegator']).call(block_identifier=block)

        pending_fees = bonding_manager_contract.functions.pendingFees(config["delegator"], 0).call(block_identifier=block)

        stake_fees_data["round"].append(round)
        stake_fees_data["stake"].append(w3_arb.from_wei(pending_stake, "ether"))
        stake_fees_data["fees"].append(w3_arb.from_wei(pending_fees, "ether"))
    
    df = DataFrame(stake_fees_data)

    with open("stake.csv", "w") as file:
        df.to_csv(file, sep=",", index=False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass