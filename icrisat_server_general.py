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
input_id="1Gxh18LRgRldvPne_6lQ-ktVxshrdcaMB9fSdQIRwB9Y"
output_id="1IOJhmfoHtd8dPbJKFsURUzwdOjg6E3RmxY6sHwaMwX4"
database_id=""
database=["1cHdh1XhNBzMUQULj0I5Guz90hN7n2RpzP-oX4OsWI0c","1v2-Y8rDO4KEvQPvafZC8IHJ6KFlcc8UvT7pa8hwvcDo"]


scope = ['https://www.googleapis.com/auth/spreadsheets']

credentials = ServiceAccountCredentials.from_json_keyfile_name('agri-data-culture.json', scope)

gc = gspread.authorize(credentials)


app = Flask(__name__)

database_range="A1:D5"
database_rows=2
database_columns=4

@app.route('/home')
def hello_world():
    return render_template('home.html')

@app.route('/check_inventory')
def hello_world1():
    return render_template('input.html')

@app.route('/add_entry')
def hello_world2():
    return render_template('entries.html')


@app.route('/seedname', methods=['POST','GET'])
def redirect():
    global database_id
    global database_range
    global database_rows
    global database_columns
    if request.form['seed'].lower()=="sorghum":
        database_id=database[0]
        database_range="A1:D5"
        database_rows=5
        database_columns=4
        return render_template('options.html')
    elif request.form['seed'].lower()=="valencia":
        database_id=database[1]
        database_range="A1:E3"
        database_rows=3
        database_columns=5
        return render_template('options.html')
    else:
        return render_template('error.html')

@app.route('/genotype', methods=['POST','GET'])
def get_values_from_spreadsheet_based_on_genotype():
    global credentials
    global sheets_id
    global gc
    try:
        worksheet = gc.open_by_key(sheets_id).sheet1
        start = time.time()
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
        return render_template('update_GWT.html', GAlias=str(data[0][0]), GWT=str(data[0][1]), Tray=str(data[0][2]), row=row)
        #return 'Time1 is %s  ;  Time2 is %s ' %(str(elapsed1),str(elapsed2))
    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        get_values_from_spreadsheet_based_on_genotype()



@app.route('/update_GWT', methods=['POST','GET'])
def update_genotype_value_in_spreadsheet():
    global credentials
    global sheets_id
    global gc

    try:
        wks = gc.open_by_key(sheets_id).sheet1
        row=str(request.form['row'])
        wks = gc.open_by_key(sheets_id).sheet1
        cell='C'+row
        value=str(request.form['GWT'])
        wks.update_acell(cell, value)

        return render_template('GWT_update_success.html')

    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        update_genotype_value_in_spreadsheet()

@app.route('/append_values', methods=['POST'])
def append_values_to_first_empty_row():
    global credentials
    global sheets_id
    global gc

    try:
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

    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        append_values_to_first_empty_row()

@app.route('/update_database', methods=['POST','GET'])
def update_database():
    start = time.time()
    global credentials
    global database_id
    global gc

    try:
        wks = gc.open_by_key(database_id).sheet1
        ID = wks.acell('I1').value
        ID = ID.split(',')
        for i in range(0,5):
            sheets_id=ID[i]
            sh = gc.open_by_key(sheets_id).sheet1
            cell='A'+str(i+1)
            wks.update_acell(cell, "updating!")
            column=sh.col_values(1)
            cell='B'+str(i+1)
            wks.update_acell(cell, "updating!")
            column=sh.col_values(2)
            wks.update_acell(cell, column)
            cell='C'+str(i+1)
            wks.update_acell(cell, "updating!")
            column=sh.col_values(3)
            wks.update_acell(cell, column)
            cell='D'+str(i+1)
            wks.update_acell(cell, "updating!")
            column=sh.col_values(4)
            wks.update_acell(cell, column)

        elapsed2 = time.time()-start
        return str(elapsed2)

    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        update_database()


@app.route('/update_databasefast', methods=['POST','GET'])
def update_database_fast():
    start = time.time()
    global credentials
    global database_id
    global gc

    try:
        wks = gc.open_by_key(database_id).sheet1
        ID = wks.acell('I1').value
        ID = ID.split(',')
        data=[]
        for i in range(0,5):
            sheets_id=ID[i]
            sh = gc.open_by_key(sheets_id).sheet1
            column=sh.col_values(1)
            data.append(column)
            column=sh.col_values(2)
            data.append(column)
            column=sh.col_values(3)
            data.append(column)
            column=sh.col_values(4)
            data.append(column)

        ranges = wks.range('A1:D5')
        for i, val in enumerate(data):  #gives us a tuple of an index and value
                ranges[i].value = val    #use the index on cell_list and the val from cell_values
        wks.update_cells(ranges)

        elapsed2 = time.time()-start
        return str(elapsed2)

    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        update_database_fast()


@app.route('/update_databasesuperfast', methods=['POST','GET'])
def update_database_superfast():
    start = time.time()
    global credentials
    global database_id
    global gc
    global database_columns
    global database_rows
    global database_range

    try:
        wks = gc.open_by_key(database_id).sheet1
        ID = wks.acell('I1').value
        ID = ID.split(',')
        data = [[] for _ in range(database_columns*database_rows)]


        """for i in range(0,database_rows):
            sheets_id=ID[i]
            sh = gc.open_by_key(sheets_id).sheet1
            r=sh.range('A1:D600')
            D=[]
            L=[]
            M=[]
            N=[]
            for i in range(0,600):
                k=database_columns*i
                D.append(r[k].value)
                L.append(r[k+1].value)
                M.append(r[k+2].value)
                N.append(r[k+3].value)
            data.append(D)
            data.append(L)
            data.append(M)
            data.append(N)"""
        n=0
        for i in range(0,database_rows):
            sheets_id=ID[i]
            sh = gc.open_by_key(sheets_id).sheet1
            r=sh.range('A1:%s600'%(chr(64+database_columns)))
            j=0
            while(j<database_columns):
                for i in range(0,600):
                    k=database_columns*i
                    data[n].append(r[k+j].value)
                n=n+1
                j=j+1

        a=sh.row_values(1)
        a=a[0:7]
        namerange = wks.range('A10:G10')
        for i, val in enumerate(a):  #gives us a tuple of an index and value
            namerange[i].value = val    #use the index on cell_list and the val from cell_values
        wks.update_cells(namerange)

        ranges = wks.range(database_range)
        #return "%s,%s" %(str(len(data)),str(len(ranges)))
        for i, val in enumerate(data):  #gives us a tuple of an index and value
                ranges[i].value = val    #use the index on cell_list and the val from cell_values
        wks.update_cells(ranges)

        elapsed2 = time.time()-start
        return str(elapsed2)

    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        update_database_fast()


@app.route('/output', methods=['POST','GET'])
def write_output_into_outputspreadsheet():
    global output_id
    global credentials
    global input_id
    global database_id
    global gc
    global database_range
    global database_rows
    global database_columns

    try:
        out_sheet = gc.open_by_key(output_id).sheet1
        in_sheet = gc.open_by_key(input_id).sheet1
        data_sheet = gc.open_by_key(database_id).sheet1
        inputs=in_sheet.col_values(1)
        length=inputs.index('')
        #inputs=inputs[1:length]
        a=data_sheet.row_values(10)
        a=a[0:7]
        namerange = out_sheet.range('A1:G1')
        for i, val in enumerate(a):  #gives us a tuple of an index and value
            namerange[i].value = val    #use the index on cell_list and the val from cell_values
        out_sheet.update_cells(namerange)

        out= data_sheet.range(database_range)
        data=[]
        out_geno=[]
        out_galias=[]
        out_gwt=[]
        out_tray=[]
        out_all = [[] for _ in range(database_columns-1)]
        for i in range(0,database_rows*database_columns):
            t=out[i].value
            t=t.split(',')
            t = [x.strip(' ') for x in t]
            data.append(t)


        for i in range(1,length):
            p=0
            a="\'%s\'" %(inputs[i])
            z=0
            while(a not in data[p]):
                z=z+1
                if(z==database_rows):
                    break
                p=p+database_columns
                #return str(p)
            if(z!=database_rows):
                n=1
                idx=data[p].index(a)
                out_geno.append(inputs[i])
                """while(n<database_columns):
                    out_all[n-1].append(data[p+n][idx])

                out_galias.append(data[p+1][idx])
                out_gwt.append(data[p+2][idx])
                out_tray.append(data[p+3][idx])
            else:
                out_geno.append(inputs[i])
                out_galias.append("entry doesn't exist")
                out_gwt.append("entry doesn't exist")
                out_tray.append("entry doesn't exist")"""

                while(n<database_columns):
                    out_all[n-1].append(data[p+n][idx])
                    n=n+1
            else:
                n=1
                out_geno.append(inputs[i])
                while(n<database_columns):
                    out_all[n-1].append("entry doesn't exist")
                    n=n+1


        """geno_range = out_sheet.range('A2:A%d' %(length))
        galias_range = out_sheet.range('B2:B%d' %(length))
        gwt_range = out_sheet.range('C2:C%d' %(length))
        tray_range = out_sheet.range('D2:D%d'%(length))

        for i, val in enumerate(out_geno):  #gives us a tuple of an index and value
                geno_range[i].value = "\'%s" %(val)    #use the index on cell_list and the val from cell_values
        out_sheet.update_cells(geno_range)

        for i, val in enumerate(out_galias):  #gives us a tuple of an index and value
                galias_range[i].value = "\'%s" %(val)    #use the index on cell_list and the val from cell_values
        out_sheet.update_cells(galias_range)

        for i, val in enumerate(out_gwt):  #gives us a tuple of an index and value
                gwt_range[i].value = "\'%s" %(val)    #use the index on cell_list and the val from cell_values
        out_sheet.update_cells(gwt_range)

        for i, val in enumerate(out_tray):  #gives us a tuple of an index and value
                tray_range[i].value = "\'%s" %(val)    #use the index on cell_list and the val from cell_values
        out_sheet.update_cells(tray_range)"""

        geno_range = out_sheet.range('A2:A%d' %(length))
        for i, val in enumerate(out_geno):  #gives us a tuple of an index and value
                geno_range[i].value = "\'%s" %(val)    #use the index on cell_list and the val from cell_values
        out_sheet.update_cells(geno_range)

        n=0
        a='B'
        while(n<database_columns-1):
            out_range=out_sheet.range('%s2:%s%d' %(a,a,length))
            for i, val in enumerate(out_all[n]):  #gives us a tuple of an index and value
                    out_range[i].value = "\'%s" %(val)    #use the index on cell_list and the val from cell_values
            out_sheet.update_cells(out_range)
            n=n+1
            a=chr(ord(a) + 1)

        return "done!"


    except gspread.RequestError:

        gc = gspread.authorize(credentials)
        write_output_into_outputspreadsheet()



@app.route('/clear_inputsheet', methods=['POST','GET'])
def clears_inputsheet():
    global credentials
    global input_id
    global gc

    try:
        wks = gc.open_by_key(input_id).sheet1
        cell_list = wks.range('A2:A500')
        for cell in cell_list:
            cell.value = ""
        wks.update_cells(cell_list)
        return "cleared!"

    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        clears_inputsheet()


@app.route('/clear_outputsheet', methods=['POST','GET'])
def clears_outputsheet():
    global credentials
    global output_id
    global gc

    try:
        wks = gc.open_by_key(output_id).sheet1
        cell_list = wks.range('A1:G500')
        for cell in cell_list:
            cell.value = ""
        wks.update_cells(cell_list)
        return "cleared!"

    except gspread.RequestError:
        gc = gspread.authorize(credentials)
        clears_outputsheet()


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=2000,
        debug=True
    )
