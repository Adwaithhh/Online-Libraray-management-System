from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =====================
# DATABASE MODELS
# =====================
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    available = db.Column(db.Boolean, default=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Issued(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

# =====================
# ROUTES
# =====================
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        book = Book(title=title, author=author, genre=genre, available=True)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('view_books'))
    return render_template("add_book.html")

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        member = Member(name=name)
        db.session.add(member)
        db.session.commit()
        return redirect(url_for('view_members'))
    return render_template("add_member.html")

@app.route('/view_members')
def view_members():
    members = Member.query.all()
    return render_template("view_members.html", members=members)

@app.route('/issue_return', methods=['GET', 'POST'])
def issue_return():
    message = ""
    if request.method == 'POST':
        action = request.form['action']
        book_id = int(request.form['book_id'])
        member_id = request.form.get('member_id')

        book = Book.query.get(book_id)
        if action == 'issue':
            member = Member.query.get(int(member_id)) if member_id else None
            if book and member and book.available:
                book.available = False
                issue = Issued(book_id=book.id, member_id=member.id)
                db.session.add(issue)
                db.session.commit()
                message = "Book issued successfully!"
            else:
                message = "Book not available or member not found."

        elif action == 'return':
            if book:
                issued_record = Issued.query.filter_by(book_id=book.id).first()
                if issued_record:
                    book.available = True
                    db.session.delete(issued_record)
                    db.session.commit()
                    message = "Book returned successfully!"
                else:
                    message = "Book was not issued."
    return render_template("issue_return.html", message=message)

@app.route('/view_books')
def view_books():
    books = Book.query.all()
    return render_template("view_books.html", books=books)

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.genre = request.form['genre']
        db.session.commit()
        return redirect(url_for('view_books'))
    return render_template('edit_books.html', book=book)

# =====================
# CREATE DATABASE
# =====================
if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
       # db.drop_all()
        db.create_all()
    app.run(debug=True)

