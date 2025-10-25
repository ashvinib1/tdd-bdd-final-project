"""
Models for Product Store Service
"""
from enum import Enum
from service import db  # Import db from __init__.py


# Custom Exception for validation errors
class DataValidationError(Exception):
    """Used for any data validation errors when deserializing"""
    pass


class Category(Enum):
    """Enum for product categories"""
    ELECTRONICS = "Electronics"
    CLOTHING = "Clothing"
    FOOD = "Food"
    BOOKS = "Books"
    OTHER = "Other"


class Product(db.Model):
    """Product model"""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1024))
    category = db.Column(db.Enum(Category), nullable=False)
    available = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, nullable=False)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "available": self.available,
            "price": self.price,
        }

    def deserialize(self, data):
        try:
            self.name = data["name"]
            self.description = data.get("description", "")
            self.category = Category[data["category"].upper()]
            self.available = data.get("available", True)
            self.price = float(data["price"])
        except KeyError as error:
            raise DataValidationError(f"Missing key: {error}")
        except ValueError as error:
            raise DataValidationError(f"Invalid value: {error}")

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def find(cls, product_id):
        return cls.query.get(product_id)

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter(cls.name.ilike(f"%{name}%")).all()

    @classmethod
    def find_by_category(cls, category):
        return cls.query.filter_by(category=category).all()

    @classmethod
    def find_by_availability(cls, available):
        return cls.query.filter_by(available=available).all()


def init_db(app):
    """Initialize the database"""
    with app.app_context():
        db.create_all()
