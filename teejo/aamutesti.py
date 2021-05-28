from flask import Flask, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, validators
app = Flask(__name__)
app.secret_key = "arfhgqary04t4t9qg4qg9"
db = SQLAlchemy(app)

class Task(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)

TaskForm = model_form(Task, base_class=FlaskForm, db_session=db.session)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String, nullable=False, unique=True)
  passwordHash = db.Column(db.String, nullable=False)

  def setPassword(self, password)
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
        flash("Login failed")
        return redirect("/user/login")
      if not user.checkPassword(password):
        flash("Login failed")
        return redirect("/user/login")

      session ["uid"]=user.id
      flash("suycces")
      return redirect("/")
  return render_template("login.html", form=form)

@app.route("/user/register", methods=["GET", "POST"])
def registerView():
  form = UserForm()

  if  form.validate_on_submit():
      email = form.email.data
      password = form.password.data

      if User.query.filter_by(email=email).first():
        flash("User alreday exists")
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
  flash("cya")
  return redirect("/")

@app.before_first_request
def initDb():
  db.create_all()

  task = Task(name="A lot")
  db.session.add(task)
  db.session.commit()

@app.errorhandler(404)
def custom404(e):
  return render_template("404.html")

@app.route("/task/<int:id>/edit", methods=["GET", "POST"])
@app.route ("/task/add", methods=["GET", "POST"])
def addView(id=None):
  task = Task()
  if id:
    task = Task.query.get_or_404(id)
  form = TaskForm(obj=task)

  if form.validate_on_submit():
    form.populate_obj(task)
    db.session.add(task)
    db.session.commit()

    flash("ph mo")
    return redirect("/")

  return render_template("add.html", form=form)

@app.route("/task/<int:id>/delete")
def deleteView(id):
  task = Task.query.get_or_404(id)
  db.session.delete(task)
  db.session.commit()

  flash("Deleted")
  return redirect("/")

@app.route("/")
def indexView():
  tasks = Task.query.all()
  return render_template("index.html", tasks=tasks)

if __name__=="__main__":
  app.run(debug=True)
