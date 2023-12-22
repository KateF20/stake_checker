from decimal import Decimal
import logging

from settings.settings import EXCHANGE_RATE
from database.database import get_last_stake, get_total_staked, get_all_subscribers


def generate_stake_message():
    logging.info('went to the db')
    last_stake = get_last_stake()
    total_staked = get_total_staked()
    logging.info(f'last stake is: {last_stake}, total staked are: {total_staked}')

    if last_stake is not None:
        duration_seconds = last_stake.unstake_timestamp - int(last_stake.timestamp.timestamp())
        duration_days = duration_seconds // (24 * 3600)

        amount_staked_eth = last_stake.amount_staked / 10 ** 18
        logging.info(f'amount staked: {amount_staked_eth}')
        total_staked_eth = total_staked / 10 ** 18
        logging.info(f'total staked eth: {total_staked_eth}')
        total_staked_usd = total_staked_eth * Decimal(EXCHANGE_RATE)
        logging.info(f'total staked usd: {total_staked_usd}, exchange rate is: {EXCHANGE_RATE}')

        message = (
            f"NEW $PAAL STAKE!\n\n"
            f"🤖 Amount Staked\n"
            f"{amount_staked_eth:.2e} ETH| ${last_stake.usd_value:.2e}\n\n"
            f"⏰ Duration {duration_days} days\n\n"
            f"🔒 Total Staked {total_staked_eth:.2f} ETH| ${total_staked_usd:.2f}")

    else:
        message = "No stakes found."

    return message
