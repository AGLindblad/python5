from flask import Flask, render_template, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, validators

app = Flask(__name__)
app.secret_key = "ohpiH5ahy7ohg%u4ieb%aep5aehaos"
db = SQLAlchemy(app)

class Book(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String, nullable=False)
  author = db.Column(db.String, nullable=False)
  plot = db.Column(db.String(160), nullable=False) #considered text type, but seems it cant be limited to 160 chrs reliably?

BookForm = model_form(Book, base_class=FlaskForm, db_session=db.session)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String, nullable=False, unique=True)
  passwordHash = db.Column(db.String, nullable=False)

  def setPassword(self, password):
    self.passwordHash = generate_password_hash(password)

  def checkPassword(self, password):
    return check_password_hash(self.passwordHash, password)

class UserForm(FlaskForm):
  email = StringField("email", validators=[validators.Email()])
  password = PasswordField("password", validators=[validators.InputRequired()])

def currentUser():
  try:
    uid = int(session["uid"])
  except:
    return None
  return User.query.get(uid)

app.jinja_env.globals["currentUser"] = currentUser

@app.route("/user/login", methods =["GET", "POST"])
def loginView():
  form = UserForm()

  if  form.validate_on_submit():
      email = form.email.data
      password = form.password.data

      user = User.query.filter_by(email=email).first()
      if not user:
        flash("Login failed. Please create an account if you haven't done so yet.")
        return redirect("/user/login")
      if not user.checkPassword(password):
        flash("Login failed")
        return redirect("/user/login")

      session ["uid"] = user.id
      flash("Welcome!")
      return redirect("/")

  return render_template("login.html", form=form)

@app.route("/user/register", methods=["GET", "POST"])
def registerView():
  form = UserForm()

  if  form.validate_on_submit():
      email = form.email.data
      password = form.password.data

      if User.query.filter_by(email=email).first():
        flash("User alreday exists - please log in!")
        return redirect("/user/login")

      user = User(email=email)
      user.setPassword(password)

      db.session.add(user)
      db.session.commit()
      flash("Register")
      return redirect("/user/login")

  return render_template("register.html", form=form)

@app.route("/user/logout")
def logoutView():
  session["uid"] = None
  flash("Bye until next time!")
  return redirect("/")

@app.before_first_request
def initDb():
  db.create_all()

  book = Book(title="A farewell to Arms", author="E. Hemingway", plot="There is a war and a boy and a girl fall in love. The war sucks and he bumbles around in the rain towards the end. The arms do not bid any farewell though.")
  db.session.add(book)

  book = Book(title="The Great Gatsby", author="F.S. Fitzgerald", plot="Rich guy feels lonely despite throwing parties. There is a green light, jazz, an unfortunate swimming pool  and an elusive girl.")
  db.session.add(book)

  db.session.commit()

@app.errorhandler(404)
def custom404(e):
  return render_template("404.html")

@app.route("/book/<int:id>/edit", methods=["GET", "POST"])
@app.route ("/book/add", methods=["GET", "POST"])
def addView(id=None):
  book = Book()
  if id:
    book = Book.query.get_or_404(id)

  form = BookForm(obj=book)

  if form.validate_on_submit():
    form.populate_obj(book)
    db.session.add(book)
    db.session.commit()

    flash("Your entry has been recorded!")
    return redirect("/")

  return render_template("add.html", form=form)

@app.route("/book/<int:id>/delete")
def deleteView(id):
  book = Book.query.get_or_404(id)
  db.session.delete(book)
  db.session.commit()

  flash("Deleted")
  return redirect("/")

@app.route("/")
def indexView():
  books = Book.query.all()
  return render_template("index.html", books=books)

if __name__=="__main__":
  app.run(debug=True)
