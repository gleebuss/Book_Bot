import os
from dotenv import load_dotenv
from flask import Flask, request, send_file
from sqlalchemy import create_engine
import pandas as pd
import tempfile

load_dotenv()

app = Flask(__name__)

USER_NAME = os.getenv('USER_NAME')

db_uri = f"postgresql+psycopg2://{USER_NAME}:@localhost:5432/{USER_NAME}"

engine = create_engine(db_uri)

@app.route('/download/<book_id>')
def download_book_stats(book_id):
    query = f"SELECT * FROM borrows WHERE book_id = '{book_id}'"
    df = pd.read_sql(query, con=engine)

    df.drop('user_id', axis=1, inplace=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        df.to_excel(tmp.name, index=False)

    return send_file(tmp.name, as_attachment=True, download_name=f"{book_id}_stats.xlsx")

if __name__ == '__main__':
    app.run(port=8080)