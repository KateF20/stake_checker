import time
import logging
import threading
from web3 import Web3

from database.database import insert_stake_event_into_database, get_last_stake
from settings.settings import CONTRACT_ABI, CONTRACT_ADDRESS, START_BLOCK, PROVIDER_URL

w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def handle_event(event):
    block_number = event['blockNumber']
    user_address = event['args']['user']
    stake_id = event['args']['stakeId']
    amount_staked_wei = event['args']['stakedAmount']
    unstake_timestamp = event['args']['unstakeTimestamp']

    block = w3.eth.get_block(block_number)
    event_timestamp = block['timestamp']

    amount_staked_eth = amount_staked_wei / 10 ** 18

    insert_stake_event_into_database(
        block_number,
        user_address,
        stake_id,
        amount_staked_eth,
        unstake_timestamp,
        event_timestamp
    )


def start_history_fetcher():
    logger.info('started fetching history')
    last_processed_block = get_last_stake().block_number if get_last_stake() else START_BLOCK

    staked_event_filter = contract.events.Staked.create_filter(fromBlock=START_BLOCK)
    events = staked_event_filter.get_all_entries()
    latest_block_number = events[-1]['blockNumber']

    if int(last_processed_block) < int(latest_block_number):
        events_to_process = fetch_staked_events(last_processed_block, latest_block_number)
        logger.info(f'last block in DB: {last_processed_block}, last block on contract: {latest_block_number}')

        for event in events_to_process:
            logger.info(f'event to handle: {event}')
            handle_event(event)
        logger.info(f"Processed historical events up to block {latest_block_number}")


def fetch_staked_events(start_block, end_block):
    staked_event_filter = contract.events.Staked.create_filter(fromBlock=start_block, toBlock=end_block)
    logger.info(f'there some events {staked_event_filter.get_all_entries()}')
    return staked_event_filter.get_all_entries()


def start_event_listener():
    staked_event_filter = contract.events.Staked.create_filter(fromBlock='latest')
    logger.info("Staked event filter created successfully.")

    while True:
        try:
            logger.info('started listening to new events')
            events = staked_event_filter.get_new_entries()
            for event in events:
                handle_event(event)
            if events:
                logger.info(f"Processed {len(events)} new events.")
            time.sleep(60)
        except Exception as e:
            logger.error(f"Error processing new events: {e}")


if __name__ == '__main__':
    history_thread = threading.Thread(target=start_history_fetcher)
    listener_thread = threading.Thread(target=start_event_listener)

    history_thread.start()
    listener_thread.start()

    history_thread.join()
    listener_thread.join()
