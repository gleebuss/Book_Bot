from database.models import Base, Book, Borrow
from datetime import date, datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

class DatabaseConnector:
    def __init__(self, user_name):
        self.engine = create_engine(f"postgresql+psycopg2://{user_name}:@localhost:5432/{user_name}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add(self, title, author, published):
        with self.Session() as conn:
            book = Book(title=title, author=author, published=published)
            conn.add(book)
            conn.commit()
            return book.book_id

    def delete(self, book_id):
        with self.Session() as conn:
            borrow = conn.query(Borrow).filter(Borrow.book_id == book_id, Borrow.date_end == None).first()
            if borrow is not None:
                return False
            book = conn.query(Book).filter(Book.book_id == book_id).first()
            book.date_deleted = datetime.now()
            conn.commit()
            return True

    def list_books(self):
        with self.Session() as conn:
            books = conn.query(Book).all()
            return [{'title': book.title, 'author': book.author, 'published': book.published, 'deleted': book.date_deleted == None} for book in books]

    def get_book(self, title, author, published):
        with self.Session() as conn:
            book = conn.query(Book).filter(func.lower(Book.title) == func.lower(title), func.lower(Book.author) == func.lower(author), Book.published == published).first()
            if book is None:
                return None
            return book.book_id if book.date_deleted is None else None

    def borrow(self, book_id, user_id):
        with self.Session() as conn:
            borrow = conn.query(Borrow).filter(Borrow.book_id == book_id, Borrow.date_end == None).first()
            if borrow is not None:
                return False
            borrow = conn.query(Borrow).filter(Borrow.user_id == user_id, Borrow.date_end == None).first()
            if borrow is not None:
                return False
            borrow = Borrow(book_id=book_id, user_id=user_id)
            conn.add(borrow)
            conn.commit()
            return borrow.borrow_id

    def get_borrow(self, user_id):
        with self.Session() as conn:
            borrow = conn.query(Borrow).filter(Borrow.user_id == user_id, Borrow.date_end == None).first()
            if borrow is None:
                return None
            return borrow.borrow_id

    def retrieve(self, borrow_id):
        with self.Session() as conn:
            borrow = conn.query(Borrow).filter(Borrow.borrow_id == borrow_id, Borrow.date_end == None).first()
            if borrow is None:
                return None
            borrow.date_end = datetime.now()
            conn.commit()
            return {'title': borrow.book.title, 'author': borrow.book.author, 'published': borrow.book.published}