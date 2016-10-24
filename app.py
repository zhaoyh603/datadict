#!/usr/bin/env python
#coding=utf-8
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import text
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://scott:tiger@127.0.0.1:1521/sidname'
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
	sql=text(
		'''
		select t.table_name,t.column_name,t.data_type,t.data_length,t.nullable,t.column_id,c.comments, 
       (SELECT CASE WHEN t.column_name=m.column_name THEN 1 ELSE 0 END FROM DUAL) iskey 
       FROM user_tab_cols t, user_col_comments c, (select m.column_name from user_constraints s, user_cons_columns m 
             where lower(m.table_name)='us_cities' and m.table_name=s.table_name 
             and m.constraint_name=s.constraint_name and s.constraint_type='P') m 
       WHERE lower(t.table_name)='us_cities' 
             and c.table_name=t.table_name 
             and c.column_name=t.column_name 
             and t.hidden_column='NO' 
 		order by t.column_id
		''')

    result = db.session.execute(sql,{'val': 5}).fetchall() 
	return render_template('datadict.html', tables=tables,cols=cols)

if __name__ == '__main__':
    app.run()
