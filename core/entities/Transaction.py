from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String
from config.database import Base


class WalletInDB(BaseModel):
    transaction_id: int 
    user_id: int          # идентификатор владельца кошелька
    amount: float = 0.0   # сумма транзакции
    status: str           # pending completed failed 
    model_config = {
        "from_attributes": True
    }


class Transaction(Base):
    transaction_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    amount = Column(Numeric(10, 2), default=0, nullable=False)
    status = Column(String, nullable=False)

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.transaction_id})")
    
    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.transaction_id}")