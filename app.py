#!/usr/bin/python3
from flask import Flask, request, render_template, make_response, redirect, url_for, session, g
from selenium import webdriver
import urllib
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

try:
    FLAG = open('./flag.txt', 'r').read()
except:
    FLAG = '[**FLAG**]'

def read_url(url, cookie={'name': 'name', 'value': 'value'}):
    cookie.update({'domain':'127.0.0.1'})
    try:
        options = webdriver.ChromeOptions()
        for _ in ['headless', 'window-size=1920x1080', 'disable-gpu', 'no-sandbox', 'disable-dev-shm-usage']:
            options.add_argument(_)
        driver = webdriver.Chrome('/chromedriver', options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)
        driver.get('http://127.0.0.1:8000/')
        driver.add_cookie(cookie)
        driver.get(f'http://127.0.0.1:8000/csrf?csrf={urllib.parse.quote(url)}')
    except:
        driver.quit()
        return False
    driver.quit()
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/csrf')
def csrf():
    csrf = request.args.get('csrf', '').lower()
    xss_filter = ['frame', 'script', 'on']
    for _ in xss_filter:
        csrf = csrf.replace(_, '*')
    return csrf

@app.route('/flag', methods=['GET', 'POST', 'PUT'])
def flag():
    if request.method == 'GET':
        return render_template('flag.html')
    elif request.method == 'POST':
        csrf = request.form.get('csrf', '')
        if not read_url(csrf):
            return '<script>alert("wrong??");history.go(-1);</script>'

        return '<script>alert("good");history.go(-1);</script>'

memo_text = ''
@app.route('/memo')
def memo():
    global memo_text
    text = request.args.get('memo', None)
    if text:
        memo_text += text.replace('<', '&lt;') + '\n'
    return render_template('memo.html', memo=memo_text)

@app.route('/admin/notice_flag')
def admin_notice_flag():
    global memo_text
    if request.remote_addr != '127.0.0.1':
        return 'Access Denied'
    if request.args.get('userid', '') != 'admin':
        return 'Your not admin'
    memo_text += f'[Notice] flag is {FLAG}\n'
    return 'Ok'

app.run(host='0.0.0.0', port=8000)