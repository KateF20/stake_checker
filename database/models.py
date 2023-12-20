from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Numeric

Base = declarative_base()


class Stake(Base):

    __tablename__ ='stakes'

    id = Column(Integer, primary_key=True)
    block_number = Column(Integer)
    user_address = Column(String(42), index=True)
    stake_id = Column(BigInteger, index=True)
    amount_staked = Column(BigInteger)
    unstake_timestamp = Column(BigInteger)
    usd_value = Column(Numeric)
    timestamp = Column(DateTime)

    # def calculate_duration(self, tx_timestamp):
    #     if self.unstake_timestamp and tx_timestamp:
    #         self.duration = self.unstake_timestamp - tx_timestamp
    #     else:
    #         self.duration = None
