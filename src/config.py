from typing import TypedDict

class Endpoint(TypedDict):
    arbitrum: str
    ethereum: str

class Contract(TypedDict):
    bonding_manager: str
    round_manager: str
    lpt_token: str
    delegator: str

class Block(TypedDict):
    step: int
    starting: int

class Common(TypedDict):
    contract: Contract
    block: Block

class Secrets(TypedDict):
    delegator: str
    enpoint: Endpoint

class Config(TypedDict):
    contract: Contract
    block: Block
    endpoint: Endpoint
    delegator: str

