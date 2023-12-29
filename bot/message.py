import logging

from database.aix_to_usd import price_data
from database.database import get_last_stake
from events.stake_checker import total_staked


def generate_stake_message():
    logging.info('went to the db')
    last_stake = get_last_stake()
    logging.info(f'last stake is: {last_stake}, total staked are: {total_staked}')

    if last_stake is not None:
        duration_seconds = last_stake.unstake_timestamp - int(last_stake.timestamp.timestamp())
        duration_days = duration_seconds // (24 * 3600)

        amount_staked_aix = last_stake.amount_staked / 10 ** 18
        total_staked_usd = total_staked * price_data

        message = (
            f"New AIX Stake!\n\n"
            f"🤖 Amount Staked\n"
            f"{amount_staked_aix:.2e} ETH| ${last_stake.usd_value:.2e}\n\n"
            f"⏰ Duration {duration_days} days\n\n"
            f"🔒 Total Staked {total_staked:.2f} AIX| ${total_staked_usd:.2f}")

    else:
        message = "No stakes found."

    return message
