from flask import Flask, render_template
from flask import request, redirect
from flask import jsonify
import requests
from bs4 import BeautifulSoup
import urllib2, urllib, json, urlfetch
import cookielib
from getpass import getpass
import sys
import os
from stat import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time


scope = ['https://www.googleapis.com/auth/spreadsheets']

credentials = ServiceAccountCredentials.from_json_keyfile_name('agri-data-culture.json', scope)

gc = gspread.authorize(credentials)

app = Flask(__name__)

row=2
sheets_id=""
sheets_name=""

@app.route('/home')
def hello_world():
    return render_template('home.html')

@app.route('/check_inventory')
def hello_world1():
    return render_template('enter_genotype.html')

@app.route('/add_entry')
def hello_world2():
    return render_template('entries.html')


@app.route('/seedname', methods=['POST','GET'])
def redirect():
    global sheets_id
    global sheets_name
    if request.form['seed'].lower()=="sorghum":
        sheets_id='1iD7oaNs60syPyF72sSUxYiNkfcK6oBLx_zZbHfYSByg'
        sheets_name="Sorghum Ref set seed multiplication Entry list.xlsx"
        return render_template('options.html')
    elif request.form['seed'].lower()=="soya":
        sheets_id='1khTxY3Jpz7RrzJgG7OcGNpv7Hw4wcHCc86F--FCLdmw'
        sheets_name="Icrisat dummy data"
        return render_template('options.html')
    else:
        return render_template('error.html')

@app.route('/genotype_ascending', methods=['POST','GET'])
def get_values_from_spreadsheet_based_on_genotype_ascending():
    row=int(request.form['genotype'])+1
    r=requests.get('https://sheets.googleapis.com/v4/spreadsheets/%s/values/B%d:D%d?key=AIzaSyCcnQDCQGsTp4dofDS3fjbgGWM3mhBQw_c'%(sheets_id,row,row))
    data=r.json()
    data=data['values']
    #return jsonify(data['values'])
    #return 'G.Alias is %s  ;  GWT is %s  ;  Tray number is %s' %(str(data[0][0]),str(data[0][1]),str(data[0][2]))
    return render_template('update_GWT.html', GAlias=str(data[0][0]), GWT=str(data[0][1]), Tray=str(data[0][2]), row=row)

@app.route('/genotype', methods=['POST','GET'])
def get_values_from_spreadsheet_based_on_genotype():

    start = time.time()
    sh = gc.open_by_key(sheets_id)
    worksheet = sh.sheet1
    values_list = worksheet.col_values(1)
    row=values_list.index(request.form['genotype'])+1
    elapsed1 = time.time()-start

    start = time.time()
    r=requests.get('https://sheets.googleapis.com/v4/spreadsheets/%s/values/B%d:D%d?key=AIzaSyCcnQDCQGsTp4dofDS3fjbgGWM3mhBQw_c'%(sheets_id,row,row))
    data=r.json()
    data=data['values']
    elapsed2 = time.time()-start

    #return jsonify(data['values'])
    #return 'G.Alias is %s  ;  GWT is %s  ;  Tray number is %s' %(str(data[0][0]),str(data[0][1]),str(data[0][2]))
    return render_template('update_GWT.html', GAlias=str(data[0][0]), GWT=str(data[0][1]), Tray=str(data[0][2]), row=row, time1=elapsed1, time2=elapsed2)
    #return 'Time1 is %s  ;  Time2 is %s ' %(str(elapsed1),str(elapsed2))

@app.route('/update_GWT', methods=['POST','GET'])
def update_genotype_value_in_spreadsheet():
    row=str(request.form['row'])
    wks = gc.open_by_key(sheets_id).sheet1
    cell='C'+row
    value=str(request.form['GWT'])
    wks.update_acell(cell, value)

    return render_template('GWT_update_success.html')


@app.route('/append_values', methods=['POST'])
def append_values_to_first_empty_row():
    wks = gc.open_by_key(sheets_id).sheet1
    values_list = wks.col_values(1)
    row=values_list.index('')+1
    row=str(row)
    cell='A'+row
    value=str(request.form['genotype'])
    wks.update_acell(cell, value)
    cell='B'+row
    value=str(request.form['G.Alias'])
    wks.update_acell(cell, value)
    cell='C'+row
    value=str(request.form['GWT'])
    wks.update_acell(cell, value)
    cell='D'+row
    value=str(request.form['Tray'])
    wks.update_acell(cell, value)

    return render_template('new_entry_success.html')



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=2000,
        debug=True
    )
