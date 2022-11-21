
import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI= 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False
<<<<<<< HEAD
SECRET_KEY='lokalat3'
=======
SECRET_KEY='lokalat3'
>>>>>>> 4202876 ('done)
