from typing import TypedDict

class Endpoint(TypedDict):
    arbitrum: str
    ethereum: str

class Address(TypedDict):
    bonding_manager: str
    round_manager: str
    lpt_token: str
    delegator: str

class Block(TypedDict):
    step: int
    starting: int

class Config(TypedDict):
    enpoint: Endpoint
    address: Address
    block: Block

