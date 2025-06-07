# from app import db
from enum import Enum
from uuid import uuid4
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from endpoints.anjem.model import AnjemDriverStatus

class UserType(Enum):
    CLIENT = "client"
    CUSTOMER = "customer"

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[str]  = mapped_column(db.UUID, primary_key=True, default=uuid4, unique=True)
    name: Mapped[str] = mapped_column(db.Text)
    phone_number: Mapped[str] = mapped_column(db.Text)
    email: Mapped[str] = mapped_column(db.Text)
    password: Mapped[str] = mapped_column(db.Text)
    student_id: Mapped[str] = mapped_column(db.Text)
    user_type: Mapped[UserType]
    gender: Mapped[Gender]

    client: Mapped[Optional['Client']] = relationship('Client', lazy=True, cascade="all, delete-orphan", back_populates='user')
    customer: Mapped[Optional['Customer']] = relationship('Customer', lazy=True, cascade="all, delete-orphan", back_populates='user')
    anjem_orders: Mapped[Optional['AnjemOrder']] = relationship('AnjemOrder', lazy=True, back_populates='user')
    
    def __init__(self, name=None, phone_number=None, email=None, password=None, student_id=None, type=None, gender=None, id=None):
        self.id = id
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.student_id = student_id
        self.user_type = UserType[type]
        self.gender = Gender[gender]

    def json(self, deep: UserType = None):
        base = {
            'id': str(self.id),
            'name': self.name,
            'phone_number': self.phone_number,
            'email': self.email,
            'student_id': self.student_id,
            'type': self.user_type.value,
            'gender': self.gender.value,
        }

        if deep == UserType.CLIENT:
            return {
                **base,
                **self.client.json()
            }
        elif deep == UserType.CUSTOMER:
            return {
                **base,
                **self.customer.json()
            }
        else: 
            return base

class Client(db.Model):
    __tablename__ = 'clients'
    
    user_id: Mapped[str] = mapped_column(db.UUID, ForeignKey('users.id'), primary_key=True)
    interest: Mapped[Optional[str]] = mapped_column(db.Text)
    bank_account: Mapped[str] = mapped_column(db.Text)
    bank_name: Mapped[str] = mapped_column(db.Text)
    ktm: Mapped[Optional[str]] = mapped_column(db.Text)
    anjem_status: Mapped[AnjemDriverStatus] = mapped_column(db.Enum(AnjemDriverStatus), default=AnjemDriverStatus.OFFLINE.value)
    verification_status: Mapped[bool] = mapped_column(db.Boolean, default=True)

    user: Mapped[User] = relationship('User', back_populates='client')

    def __init__(self, user_id, bank_account, bank_name, ktm, anjem_status=AnjemDriverStatus.OFFLINE.value, verification_status=False, interest=None):
        self.user_id = user_id
        self.interest = interest
        self.bank_account = bank_account
        self.bank_name = bank_name
        self.ktm = ktm
        self.anjem_status = AnjemDriverStatus[anjem_status]
        self.verification_status = verification_status
    
    def json(self):
        return {
            'user_id': str(self.user_id),
            'interest': self.interest,
            'bank_account': self.bank_account,
            'bank_name': self.bank_name,
            'anjem_status': self.anjem_status.value,
            'ktm': self.ktm,
            'verification_status': self.verification_status,
        }

class Customer(db.Model):
    __tablename__ = 'customers'

    user_id: Mapped[str] = mapped_column(db.UUID, ForeignKey('users.id'), primary_key=True)
    interest: Mapped[Optional[str]] = mapped_column(db.Text)

    user: Mapped[User] = relationship('User', back_populates='customer')

    def __init__(self, user_id, interest):
        self.user_id = user_id
        self.interest = interest

    def json(self):
        return {
            'user_id': str(self.user_id),
            'interest': self.interest,
        }