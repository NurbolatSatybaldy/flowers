from sqlalchemy.orm import Session
from models import User, Flower, Purchase

class UsersRepository:
    def create_user(self, database: Session, email: str, full_name: str, password_hash: str, photo_url: str):
        db_user = User(email=email, full_name=full_name, password_hash=password_hash, photo_url=photo_url)
        database.add(db_user)
        database.commit()
        database.refresh(db_user)
        return db_user.id

    def get_user_by_email(self, database: Session, email: str):
        return database.query(User).filter(User.email == email).first()

    def get_user_by_id(self, database: Session, user_id: int):
        return database.query(User).filter(User.id == user_id).first()

class FlowersRepository:
    def create_flower(self, database: Session, name: str, quantity: int, price: float):
        db_flower = Flower(name=name, quantity=quantity, price=price)
        database.add(db_flower)
        database.commit()
        database.refresh(db_flower)
        return db_flower.id

    def get_all_flowers(self, database: Session):
        return database.query(Flower).order_by(Flower.id).all()

    def get_flower_by_id(self, database: Session, flower_id: int):
        return database.query(Flower).filter(Flower.id == flower_id).first()

    def update_flower(self, database: Session, flower_id: int, name: str = None, quantity: int = None, price: float = None):
        flower = self.get_flower_by_id(database, flower_id)
        if not flower:
            return None
        if name is not None:
            flower.name = name
        if quantity is not None:
            flower.quantity = quantity
        if price is not None:
            flower.price = price
        database.commit()
        database.refresh(flower)
        return flower

    def delete_flower(self, database: Session, flower_id: int):
        flower = self.get_flower_by_id(database, flower_id)
        if not flower:
            return None
        database.delete(flower)
        database.commit()
        return flower.id

class PurchasesRepository:
    def add_purchase(self, database: Session, user_id: int, flower_id: int):
        purchase = Purchase(user_id=user_id, flower_id=flower_id)
        database.add(purchase)
        database.commit()

    def get_purchases_by_user(self, database: Session, user_id: int):
        return database.query(Flower.id, Flower.name, Flower.price).join(Purchase, Purchase.flower_id == Flower.id).filter(Purchase.user_id == user_id).all()
