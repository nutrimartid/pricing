
import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI= 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY='lokalat3'
UPLOAD_FOLDER='static/upload'
PRIKEYIMGKIT="private_EJ1X2wEqxTbf647Lf9KEdUayw5E="
PUBKEYIMGKIT='public_GZm9njJXmrcaOR96i2v821Rx3Fg='
URLENDIMGKIT='https://ik.imagekit.io/z83ycl28q'
SQLALCHEMY_ENGINE_OPTIONS ={'pool_pre_ping': True}
# pool_pre_ping