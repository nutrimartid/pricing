from flask import Flask,render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class tbluser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))


@app.route('/',methods=['POST','GET'])
def index():
    # df=tbluser.query.all()
    # print(df)
    # if request.method=='POST':
    #     newuser=tbluser(first_name=request.form['fname'],last_name=request.form['lname'])
    #     db.session.add(newuser)
    #     db.session.commit()
    #     return redirect(url_for('index'))
    return render_template('home2.html')

# @app.route('/delete<id>',methods=['POST','GET'])
# def delete(id):
#     deluser=tbluser.query.get(id)
#     db.session.delete(deluser)
#     db.session.commit()
#     return redirect(url_for('index'))

@app.route('/form',methods=['POST','GET'])
def form():
    return render_template('form.html')

@app.route('/form2',methods=['POST','GET'])
def form2():
    return render_template('form2.html')

if __name__ == '__main__':
    app.run()
