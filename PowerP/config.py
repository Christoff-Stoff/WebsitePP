import os

#Configuration class. Includes the connection to current database.
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PowerPartners21'
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://root:PowerPartners1@127.0.0.1:3306/PP_DB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False