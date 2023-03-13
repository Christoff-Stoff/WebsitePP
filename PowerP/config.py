import os

#Configuration class. Includes the connection to current database.
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PowerPartners21'
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://sql7605345:cgKu75zzhf@sql7.freemysqlhosting.net:3306/sql7605345'
    SQLALCHEMY_TRACK_MODIFICATIONS = False