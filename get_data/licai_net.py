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

@app.route('/tb/jd')
def tbjd():
    ret = '<table border="1" width="100px">\n'
    jsn = jdjj()

    ret += "<tr>\n"
    for i in jsn[0]:
        try:
            it = "<td>" + str(i) + "</td>\n"
        except:
            it = "<td>" + i.encode("utf-8") + "</td>\n"

        ret += it
    ret += "</tr>\n"


    for itm in jsn:
        ret += "<tr>\n"
        for i in itm:
            try:
                it = "<td>" + str(itm[i]) + "</td>\n"
            except:
                it = "<td>" + itm[i].encode("utf-8") + "</td>\n"

            ret += it
        ret += "</tr>\n"
    ret += "</table>\n"
    return ret


@app.route('/jd2/<int:p>')
def jd2(p):
    return jsonify(jdjj2(p))

app.run(debug=True)
