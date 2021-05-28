from flask import Flask, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = "arfhgqary04t4t9qg4qg9"
db = SQLAlchemy(app)

class Task(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)

TaskForm = model_form(Task, base_class=FlaskForm, db_session=db.session)

@app.before_first_request
def initDb():
  db.create_all()

  task = Task(name="Too much 2 dooooo :(")
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
