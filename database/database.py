import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .aix_to_usd import price_data
from .models import Base, Stake, Subscriber
from settings.settings import DB_USERNAME, DB_PASSWORD, DB_NAME

engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@localhost:5432/{DB_NAME}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def insert_stake_event_into_database(block_number, user_address, stake_id,
                                     amount_staked, unstake_timestamp, event_timestamp):
    session = Session()
    existing_stake = session.query(Stake).filter_by(stake_id=stake_id).first()
    if existing_stake:
        session.close()
        return

    amount_in_usd = amount_staked / 10 ** 18 * price_data

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


def is_subscribed(chat_id):
    session = Session()
    exists = session.query(Subscriber).filter_by(chat_id=chat_id).first() is not None
    session.close()
    return exists


def add_subscriber(chat_id):
    session = Session()
    new_subscriber = Subscriber(chat_id=chat_id)
    logging.info(f'subscriber before adding: {new_subscriber.chat_id}')
    try:
        session.add(new_subscriber)
        logging.info(f'new subscriber {new_subscriber.chat_id} added, success: {session.add(new_subscriber)}')
        session.commit()
    except Exception as e:
        logging.error(f"Error adding subscriber: {e}")
        session.rollback()
    finally:
        session.close()


def remove_subscriber(chat_id):
    session = Session()
    subscriber = session.query(Subscriber).filter_by(chat_id=chat_id).first()
    logging.info(f'subscriber before removal: {subscriber.chat_id}')
    if subscriber:
        try:
            session.delete(subscriber)
            logging.info(f'subscriber {subscriber.chat_id} removed, success: {session.delete(subscriber)}')
            session.commit()
        except Exception as e:
            logging.error(f"Error removing subscriber: {e}")
            session.rollback()
    session.close()


def get_all_subscribers():
    session = Session()
    all_subscribers = session.query(Subscriber).all()
    logging.info(f'there are {len(all_subscribers)} sunbscribers')
    subscriber_ids = [subscriber.chat_id for subscriber in all_subscribers]
    logging.info(f'there are {len(subscriber_ids)} ids found')
    session.close()

    return subscriber_ids
