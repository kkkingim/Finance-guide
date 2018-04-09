# coding: utf-8
from bs4 import BeautifulSoup
import requests
import json
from flask import Flask, jsonify

def jdjj():
    header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0'}
    req = requests.get("http://dq.jd.com/getDalicai?pageSize=100&pageNo=1", headers = header)
    infojson = json.loads(req.content[5:-1])["datas"]
    return infojson

def jdjj2(page):
    url = 'http://fund.jd.com/getLeftTab?callback=jQuery1830030959870814108448_1522401004985&page=' + str(page)
    header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0'}
    req = requests.get(url, headers = header)
    s = req.content.find("{")
    e = req.content.rfind("}")
    jsontext = req.content[s:e+1]
    # print jsontext
    # with open("temp.json", "w") as f:
    #     f.write(jsontext)
    infojson = json.loads(jsontext)["items"]
    return infojson


app = Flask(__name__)

@app.route('/jd')
def jd():
    return jsonify(jdjj())

@app.route('/jd2/<int:p>')
def jd2(p):
    return jsonify(jdjj2(p))

app.run(debug=True)
