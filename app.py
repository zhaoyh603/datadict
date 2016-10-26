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
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://gdmid:1@127.0.0.1:1521/orcl'
app.config['TESTING'] = True
db = SQLAlchemy(app)

class User_table():
    table_name = ''
    table_comments=''
    cols=[]
    

    def __init__(self, table_name, table_comments):
        self.table_name = table_name
        self.table_comments = table_comments

    def __repr__(self):
        return '<User_table %r>' % self.table_name

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
       and t.table_name=:table
       order by t.table_name, c.column_id
       ''')

    tabs= db.session.execute(sql_tab).fetchall() 
    tables=[]
    for tab in tabs:
        t=User_table(tab.table_name,tab.comments)
        print t
        t.cols = db.session.execute(sql_cols,{'table':tab.table_name}).fetchall() 
        tables.append(t)
    print tables

    return render_template('datadict.html', tabs=tables)

if __name__ == '__main__':
    app.run()
