import logging
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from .models import Base, Stake
from settings.settings import DB_USERNAME, DB_PASSWORD, DB_NAME, EXCHANGE_RATE

engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@localhost/{DB_NAME}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def insert_stake_event_into_database(block_number, user_address, stake_id,
                                     amount_staked, unstake_timestamp, event_timestamp):
    session = Session()
    existing_stake = session.query(Stake).filter_by(stake_id=stake_id).first()
    if existing_stake:
        session.close()
        return

    amount_in_usd = amount_staked / 10 ** 18 * EXCHANGE_RATE

    try:
        new_stake = Stake(
            block_number=block_number,
            user_address=user_address,
            stake_id=stake_id,
            amount_staked=amount_staked,
            unstake_timestamp=unstake_timestamp,
            usd_value=amount_in_usd,
            timestamp=datetime.fromtimestamp(event_timestamp)
        )

        session.add(new_stake)
        session.commit()

    except Exception as e:
        logging.error(f"Error inserting stake event into database: {e}")
        session.rollback()
    finally:
        session.close()


def get_last_stake():
    session = Session()
    last_stake = session.query(Stake).order_by(Stake.id.desc()).first()
    session.close()
    return last_stake


def get_total_staked():
    session = Session()
    total_staked = session.query(func.sum(Stake.amount_staked)).scalar()
    session.close()
    return total_staked if total_staked is not None else 0
