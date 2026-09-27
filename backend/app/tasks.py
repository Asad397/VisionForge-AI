from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import User, ModelRecord, CreditTransaction, Generation


class CreditService:
    @staticmethod
    def reserve_credits(db: Session, user: User, model: ModelRecord):
        if user.credits < model.credit_cost:
            raise HTTPException(status_code=402, detail='Insufficient credits for this generation')
        user.credits -= model.credit_cost
        db.add(CreditTransaction(user_id=user.id, generation_id=None, amount=-model.credit_cost, reason='generation_reserved', balance_after=user.credits))
        db.commit()
        return user

    @staticmethod
    def refund_credits(db: Session, user: User, model: ModelRecord, generation: Generation):
        user.credits += model.credit_cost
        db.add(CreditTransaction(user_id=user.id, generation_id=generation.id, amount=model.credit_cost, reason='generation_refunded', balance_after=user.credits))
        db.commit()

    @staticmethod
    def commit_credits(db: Session, user: User, model: ModelRecord, generation: Generation):
        db.add(CreditTransaction(user_id=user.id, generation_id=generation.id, amount=0, reason='generation_completed', balance_after=user.credits))
        db.commit()
