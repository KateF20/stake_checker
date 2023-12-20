from web3 import Web3

from settings.settings import CONTRACT_ABI, CONTRACT_ADDRESS, START_BLOCK, PROVIDER_URL
from database.database import insert_stake_event_into_database

w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

start_block = START_BLOCK
end_block = w3.eth.block_number

events = contract.events.Staked.create_filter(fromBlock=start_block, toBlock=end_block).get_all_entries()


def fetch_staked_events(start_block, end_block):
    staked_event_filter = contract.events.Staked.create_filter(
        fromBlock=start_block,
        toBlock=end_block
    )
    return staked_event_filter.get_all_entries()


def process_and_save_events(events):
    for event in events:
        block_number = event['blockNumber']
        user_address = event['args']['user']
        stake_id = event['args']['stakeId']
        amount_staked_wei = event['args']['stakedAmount']
        unstake_timestamp = event['args']['unstakeTimestamp']

        block = w3.eth.get_block(block_number)
        event_timestamp = block.timestamp

        amount_staked_eth = amount_staked_wei / 10 ** 18

        insert_stake_event_into_database(
            block_number,
            user_address,
            stake_id,
            amount_staked_eth,
            unstake_timestamp,
            event_timestamp
        )


if __name__ == '__main__':
    fetch_staked_events(start_block, end_block)
    process_and_save_events(events)
