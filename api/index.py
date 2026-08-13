from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)

TARGET_URL = os.environ.get('WEB_DRAKOR_URL', 'https://xdrakor71.kita.mom')

@app.route('/')
def home():
    return jsonify({
        "status": "aktif",
        "pesan": "Mesin Scraper Python Berjalan!",
        "target_saat_ini": TARGET_URL
    })

@app.route('/drakor/terbaru')
def get_terbaru():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=10)

        # Di sini nanti kita letakkan logika pencarian HTML-nya

        return jsonify({
            "status": "sukses",
            "sumber": TARGET_URL,
            "data_mentah_ditemukan": len(response.text)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "pesan": str(e)
        })
