from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import os
import pymysql
from django.core.files.storage import FileSystemStorage
from cryptosteganography import CryptoSteganography
from Daugman import find_iris
import cv2
from datetime import date
import pyaes, pbkdf2, binascii, os, secrets
import base64
from hashlib import sha256

global username
crypto_steganography = CryptoSteganography('securehiding')

def ExtractMessage(username, message):
    secret = "not exists"
    if os.path.exists('IrisAuthApp/static/watermark/'+username+".png"):
        img1 = open("IrisAuthApp/static/test.png","rb").read()
        img2 = open('IrisAuthApp/static/watermark/'+username+"_original.png","rb").read()
        if img1 == img2:
            secret = crypto_steganography.retrieve('IrisAuthApp/static/watermark/'+username+".png")
        os.remove("IrisAuthApp/static/test.png")        
    return secret

def getKey(): #generating key with PBKDF2 for AES
    password = "s3cr3t*c0d3"
    passwordSalt = '76895'
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    return key

def encrypt(plaintext): #AES data encryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

def decrypt(enc): #AES data decryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    decrypted = aes.decrypt(enc)
    return decrypted 

def ViewMessage(request):
    if request.method == 'GET':
        global username
        font = '<font size="" color="black">'
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Message ID</font></th>'
        output+='<th><font size=3 color=black>Sender Name</font></th>'
        output+='<th><font size=3 color=black>Receiver Name</font></th>'
        output+='<th><font size=3 color=black>Encrypted Message</font></th>'
        output+='<th><font size=3 color=black>Decrypted Message</font></th>'
        output+='<th><font size=3 color=black>Message Date/font></th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'irisauth',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM messages where receiver='"+username+"' or sender='"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                enc = row[3]
                enc = base64.b64decode(enc)
                decrypted = decrypt(enc)
                decrypted = decrypted.decode("utf-8")
                output += "<tr><td>"+font+str(row[0])+"</td>"
                output += "<td>"+font+row[1]+"</td>"
                output += "<td>"+font+row[2]+"</td>"
                output += "<td>"+font+row[3]+"</td>"
                output += "<td>"+font+decrypted+"</td>"
                output += "<td>"+font+row[4]+"</td></tr>" 
        output+="<br/><br/><br/><br/><br/><br/>"
        context= {'data': output} 
        return render(request, 'UserScreen.html', context) 
                


def PostMessage(request):
    if request.method == 'GET':
        global username
        output = '<select name="t1">'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'irisauth',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] != username:
                    output += '<option value="'+row[0]+'">'+row[0]+'</option>'
        context= {'receivers': output}            
        return render(request, 'PostMessage.html', context)

def PostMessageAction(request):
    global username
    if request.method == 'POST':
        receiver = request.POST.get('t1', False)
        msg = request.POST.get('t2', False)
        today = str(date.today())
        msg = encrypt(msg)
        msg = str(base64.b64encode(msg),'utf-8')
        msg_id = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'irisauth',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select max(msg_id) FROM messages")
            rows = cur.fetchall()
            for row in rows:
                msg_id = row[0]
        if msg_id is not None:
            msg_id = msg_id + 1
        else:
            msg_id = 1
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'irisauth',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO messages(msg_id,sender,receiver,message,msg_date) VALUES('"+str(msg_id)+"','"+username+"','"+receiver+"','"+msg+"','"+today+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        output = "Encrypted Msg = "+msg+"<br/>"
        output += "Message ID = "+str(msg_id)+"<br/>"
        output += "Message Sent to Receiver : "+receiver+"<br/>"
        context= {'data':output}
        return render(request, 'PostMessage.html', context)
        

def UserLogin(request):
    global username
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        image = request.FILES['t3']
        message = request.POST.get('t4', False)
        if os.path.exists("IrisAuthApp/static/test.png"):
            os.remove("IrisAuthApp/static/test.png")
        fs = FileSystemStorage()
        fs.save("IrisAuthApp/static/test.png", image)
        status = "failed"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'irisauth',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,password FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    status = 'success'
                    break
        if status == 'success':
            output = 'Login Details Matched'
            extract_msg = ExtractMessage(username, message)
            if extract_msg == message:
                status = 'Welcome username : '+username+"<br/>Both Logging & Iris Watermark Authentication Successfull"
                context= {'data':status}
                return render(request, 'UserScreen.html', context)
            else:
                context= {'data':'Watermark Authentication Failed'}
                return render(request, 'Login.html', context)
        else:
            context= {'data':'Invalid username'}
            return render(request, 'Login.html', context)

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})


def watermarkImage(user, message):
    img = cv2.imread('IrisAuthApp/static/watermark/'+user+"_original.png")
    img = cv2.resize(img,(128,128), interpolation=cv2.INTER_CUBIC)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    answer = find_iris(gray_img, daugman_start=10, daugman_end=30, daugman_step=1, points_step=3)
    iris_center, iris_rad = answer
    start = iris_center[0]
    end = iris_center[1]
    radius = iris_rad
    result = img[start-radius:start+radius,end-radius:end+radius]
    result = cv2.resize(result, (64,64), interpolation=cv2.INTER_CUBIC)
    segmented = result
    if os.path.exists('IrisAuthApp/static/watermark/'+username+".png"):
        os.remove('IrisAuthApp/static/watermark/'+username+".png")
    cv2.imwrite('IrisAuthApp/static/watermark/iris.png', segmented)    
    crypto_steganography.hide('IrisAuthApp/static/watermark/iris.png', 'IrisAuthApp/static/watermark/'+user+".png", message)
    if os.path.exists("IrisAuthApp/static/watermark/iris.png"):
        os.remove("IrisAuthApp/static/watermark/iris.png")

def RegisterAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        image = request.FILES['t6']
        message = request.POST.get('t7', False)
        if os.path.exists('IrisAuthApp/static/watermark/'+username+"_original.png"):
            os.remove('IrisAuthApp/static/watermark/'+username+"_original.png")
        fs = FileSystemStorage()
        fs.save('IrisAuthApp/static/watermark/'+username+"_original.png", image)
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'irisauth',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = username+" Username already exists"                    
        if output == "none":                      
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'irisauth',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                watermarkImage(username, message)
                context= {'data':'Signup Process Completed'}
                return render(request, 'Register.html', context)
            else:
                context= {'data':'Error in signup process'}
                return render(request, 'Register.html', context)
        else:
            context= {'data':output}
            return render(request, 'Register.html', context)    
    

