#!/usr/bin/env python
#coding=utf-8
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sys
reload(sys)
sys.setdefaultencoding('GBK')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://G1:1@10.10.3.143:1521/asupp11'
app.config['TESTING'] = True
db = SQLAlchemy(app)

class User_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
def index():
    name={}

    sql_tab=text("select table_name,comments from user_tab_comments where table_type='TABLE'")
    sql_cols=text(
	'''
       select t.table_name,
       t.comments table_comments,
       c.column_id,
       c.column_name,
       c.data_type || '(' ||
       decode(c.data_type, 'NUMBER', c.data_length - c.DATA_SCALE,c.data_length) ||
       decode(c.data_type, 'NUMBER', ',') || c.DATA_SCALE || ')' data_type,
       c.nullable,
       cc.comments col_comments
       FROM user_tab_cols c, user_col_comments cc, user_tab_comments t
       WHERE c.table_name = t.table_name
       and c.table_name = cc.table_name
       and c.column_name = cc.column_name
       and c.hidden_column = 'NO'
       and t.table_type = 'TABLE'
       order by t.table_name, c.column_id
       ''')

    tabs= db.session.execute(sql_tab).fetchall() 
    cols = db.session.execute(sql_cols).fetchall() 

    return render_template('datadict.html', tabs=tabs,cols=cols)

if __name__ == '__main__':
    app.run()
