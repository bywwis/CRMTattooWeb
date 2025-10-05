from typing import Optional
import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, REAL, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Customers(Base):
    __tablename__ = 'customers'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='customers_pkey'),
        UniqueConstraint('phone', name='mobile_phone')
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    surname: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)
    patronymic: Mapped[Optional[str]] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)

    record: Mapped[list['Record']] = relationship('Record', back_populates='customers')


class Services(Base):
    __tablename__ = 'services'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='services_pkey'),
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    price: Mapped[Optional[int]] = mapped_column(Integer)

    record: Mapped[list['Record']] = relationship('Record', back_populates='services')
    services_supplies: Mapped[list['ServicesSupplies']] = relationship('ServicesSupplies', back_populates='services')


class Supplies(Base):
    __tablename__ = 'supplies'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='supplies_pkey'),
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    price: Mapped[Optional[int]] = mapped_column(Integer)

    services_supplies: Mapped[list['ServicesSupplies']] = relationship('ServicesSupplies', back_populates='supplies')


class Record(Base):
    __tablename__ = 'record'
    __table_args__ = (
        ForeignKeyConstraint(['id_customers'], ['customers.ID'], name='customer_fkey'),
        ForeignKeyConstraint(['id_services'], ['services.ID'], name='services_fkey'),
        PrimaryKeyConstraint('ID', name='record_pkey')
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_customers: Mapped[int] = mapped_column(Integer, nullable=False)
    id_services: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    customers: Mapped['Customers'] = relationship('Customers', back_populates='record')
    services: Mapped['Services'] = relationship('Services', back_populates='record')


class ServicesSupplies(Base):
    __tablename__ = 'services_supplies'
    __table_args__ = (
        ForeignKeyConstraint(['id_services'], ['services.ID'], name='servis_fkey'),
        ForeignKeyConstraint(['id_supplies'], ['supplies.ID'], name='supplies_fkey'),
        PrimaryKeyConstraint('ID', name='services_supplies_pkey')
    )

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_services: Mapped[int] = mapped_column(Integer, nullable=False)
    id_supplies: Mapped[int] = mapped_column(Integer, nullable=False)
    material_consumption: Mapped[Optional[float]] = mapped_column(REAL)
    units_measurement: Mapped[Optional[str]] = mapped_column(String)

    services: Mapped['Services'] = relationship('Services', back_populates='services_supplies')
    supplies: Mapped['Supplies'] = relationship('Supplies', back_populates='services_supplies')
