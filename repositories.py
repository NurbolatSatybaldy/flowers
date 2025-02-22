# repositories.py
from sqlalchemy.orm import Session
from models import User, Flower, Purchase

class UsersRepository:
    def create_user(self, db: Session, email: str, full_name: str, password_hash: str, photo_url: str):
        new_user = User(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            photo_url=photo_url
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id

    def get_user_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

class FlowersRepository:
    def create_flower(self, db: Session, name: str, quantity: int, price: float):
        flower = Flower(name=name, quantity=quantity, price=price)
        db.add(flower)
        db.commit()
        db.refresh(flower)
        return flower.id

    def get_all_flowers(self, db: Session):
        return db.query(Flower).order_by(Flower.id).all()

    def get_flower_by_id(self, db: Session, flower_id: int):
        return db.query(Flower).filter(Flower.id == flower_id).first()

    def update_flower(self, db: Session, flower_id: int, name: str = None, quantity: int = None, price: float = None):
        flower = self.get_flower_by_id(db, flower_id)
        if not flower:
            return None
        if name is not None:
            flower.name = name
        if quantity is not None:
            flower.quantity = quantity
        if price is not None:
            flower.price = price
        db.commit()
        db.refresh(flower)
        return flower

    def delete_flower(self, db: Session, flower_id: int):
        flower = self.get_flower_by_id(db, flower_id)
        if not flower:
            return None
        db.delete(flower)
        db.commit()
        return flower.id

class PurchasesRepository:
    def add_purchase(self, db: Session, user_id: int, flower_id: int):
        purchase = Purchase(user_id=user_id, flower_id=flower_id)
        db.add(purchase)
        db.commit()

    def get_purchases_by_user(self, db: Session, user_id: int):
        # Example: join Flower with Purchase for a list of (id, name, price)
        return (
            db.query(Flower.id, Flower.name, Flower.price)
            .join(Purchase, Purchase.flower_id == Flower.id)
            .filter(Purchase.user_id == user_id)
            .all()
        )
