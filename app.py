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
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://cw_exchg160715:1@10.10.3.143:1521/asupp11'
app.config['TESTING'] = True
db = SQLAlchemy(app)

class User_table():
    table_name = ''
    table_comments=''
    cols=[]
    cons=[]
    

    def __init__(self, table_name, table_comments):
        self.table_name = table_name
        self.table_comments = table_comments

    def __repr__(self):
        return '<User_table %r>' % self.table_name

@app.route('/')
def index():
    name={}

    sql_tab=text("select table_name,decode(comments,null,(select res_na from as_lang_trans a \
       where a.res_id=t.table_name),comments) comments \
       from user_tab_comments t where table_type='TABLE' order by table_name")
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
       c.DATA_DEFAULT,
       decode(cc.comments,null,(select res_na from as_lang_trans a where a.res_id=cc.column_name),cc.comments) col_comments
       FROM user_tab_cols c, user_col_comments cc, user_tab_comments t
       WHERE c.table_name = t.table_name
       and c.table_name = cc.table_name
       and c.column_name = cc.column_name
       and c.hidden_column = 'NO'
       and t.table_type = 'TABLE'
       and t.table_name=:table
       order by t.table_name, c.column_id
       ''')
    sql_cons=text(
      "select c.constraint_name,\
       decode(c.constraint_type,\
              'P',\
              'Primary Key',\
              'R',\
              'Referential AKA Foreign Key',\
              'U',\
              'Unique Key') constraint_type,\
       cc.column_name\
       from user_constraints c, user_cons_columns cc\
       where c.owner = cc.owner\
         AND c.constraint_name = cc.constraint_name\
         AND c.table_name = cc.table_name\
         and c.constraint_type in ('P', 'R', 'U')\
         AND C.table_name = :table\
       ORDER BY constraint_name, cc.column_name\
      ")  
    tabs= db.session.execute(sql_tab).fetchall() 
    tables=[]
    for tab in tabs:
        t=User_table(tab.table_name,tab.comments)
        t.cols = db.session.execute(sql_cols,{'table':tab.table_name}).fetchall() 
        t.cons = db.session.execute(sql_cons,{'table':tab.table_name}).fetchall() 
        print t
        tables.append(t)
    return render_template('datadict.html', tabs=tables)

if __name__ == '__main__':
    app.run()
