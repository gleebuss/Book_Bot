from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    book_id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    published = Column(Integer)
    date_added = Column(DateTime, default=datetime.utcnow)
    date_deleted = Column(DateTime, nullable=True)
    borrows = relationship('Borrow', backref='book')

class Borrow(Base):
    __tablename__ = 'borrows'
    borrow_id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'))
    date_start = Column(DateTime, default=datetime.utcnow)
    date_end = Column(DateTime, nullable=True)
    user_id = Column(Integer)