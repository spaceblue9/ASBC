#Create By Sarawut Sittharod
from doctest import OutputChecker
from email import header
import xlrd
from xlrd.formula import rownamerel
from ast import Num
import configparser
from tkinter import N
from datetime import datetime
datenow = datetime.now()

read_config = configparser.ConfigParser()
read_config.read("Excel-ScriptBot.ini",encoding='UTF-8')
Namefile = read_config.get("Excel-Input","Namefile")
SheetName = read_config.get("Excel-Input","sheetname")
Numberofparameter = read_config.get("Parameter-Setting","NumberOfParameter")
Headerfile = read_config.get("Script-Setting","header-file")
Bodyfile = read_config.get("Script-Setting","body-file")
Footerfile = read_config.get("Script-Setting","footer-file")
OutPutfile = str(datenow.strftime('%Y-%m-%d_%H%M%S')) + "_" + read_config.get("Script-Setting","output-file")

book = xlrd.open_workbook(Namefile)
print(book.nsheets)
print (book.sheet_names())
#sheet = book.sheet_by_index(0)
sheet = book.sheet_by_name(SheetName)
#row = 0
#col = 1
#cell = sheet.cell(row,col) #where row=row number and col=column number
#print (cell.value) #to print the cell contents

#print(sheet)
num_rows=sheet.nrows
num_col=sheet.ncols
#print(num_rows)
#print(num_col)

with open(Headerfile, encoding='utf-8') as f:
    Headers = f.read()
    #print(Headers)

with open(Bodyfile, encoding='utf-8') as f:
    contents = f.read()
    #print(contents)

with open(Footerfile, encoding='utf-8') as f:
    Footers = f.read()
    #print(Footers)

ResultContents = ""
#Loop Data From Number of Parameter
'''for Parameter in range(int(Numberofparameter)):
    ColExcel  =  read_config.get("Parameter-Setting","@Parameter{}".format(str(Parameter)))
    print(str(ColExcel))
    #Loop Data From Number of Record
    for x in range(1, num_rows):
        p1 = sheet.cell(x,int(ColExcel))
        contents = contents.replace("@Parameter{}".format(str(Parameter)),str(p1.value))
        #contents = contents.replace("@Parameter1",str(p1.value))
        print(contents)
    ResultContents = contents '''

#Loop Data From Number of Record
for record_num in range(1, num_rows):
    tmp = contents
    for Parameter in range(int(Numberofparameter)):
        ColExcel  =  read_config.get("Parameter-Setting","@Parameter{}".format(str(Parameter)))
        #print(str(ColExcel))
        p1 = sheet.cell(record_num,int(ColExcel))
        tmp = tmp.replace("@Parameter{}".format(str(Parameter)),str(p1.value))
        #contents = contents.replace("@Parameter1",str(p1.value))
        #print(tmp)
    ResultContents = ResultContents + tmp + "\n"



#print(Namefile,Numberofparameter)
#print(ResultContents)
#print(Headerfile)
#print(Footerfile)

print("Program Excel-CreateScriptBot CreateBy Sarawut Sittharod 090-981-8314 sarawut.shi@mahidol.ac.th" + "\n")
substr = Headers + "\n" + ResultContents + "\n" + Footers
print(substr)

with open(OutPutfile, 'w+', encoding='utf-8') as f:
    f.write(substr + "\n")

print("Create OutPut-File : " + OutPutfile + "\n")
