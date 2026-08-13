from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)

# Mengambil URL utama dari brankas Vercel
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
        # 1. Menyamar sebagai browser PC agar tidak diblokir
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 2. Kunjungi web target
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        
        # 3. Ubah teks mentah menjadi objek HTML BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        daftar_drakor = []
        
        # 4. MULAI SCRAPING: Cari semua kotak drakor (div dengan class "card mx-auto")
        kotak_kotak_film = soup.find_all('div', class_='card mx-auto')
        
        for kotak in kotak_kotak_film:
            # Ambil Judul
            tag_judul = kotak.find('span', class_='titit')
            # Membersihkan tag <br> di dalam judul jika ada
            judul_bersih = tag_judul.contents[0].strip() if tag_judul else "Judul Tidak Diketahui"
            
            # Ambil Link Gambar Poster
            tag_gambar = kotak.find('img', class_='poster')
            link_poster = tag_gambar.get('src') if tag_gambar else ""
            
            # Ambil Link Detail Film (URL untuk diklik nanti)
            tag_link = kotak.find('a', class_='poster')
            link_detail_path = tag_link.get('href') if tag_link else ""
            
            # Ambil Status/Episode
            tag_eps = kotak.find('span', class_='rate')
            episode_saat_ini = tag_eps.text.strip() if tag_eps else "Completed"
            
            # Jika judul dan link ditemukan, masukkan ke dalam daftar hasil
            if link_detail_path and judul_bersih:
                daftar_drakor.append({
                    "judul": judul_bersih,
                    "poster": link_poster,
                    "endpoint": link_detail_path,
                    "episode": episode_saat_ini
                })
        
        # 5. Kembalikan data yang sudah rapi ke aplikasi Android dalam bentuk JSON
        return jsonify({
            "status": "sukses",
            "total_ditemukan": len(daftar_drakor),
            "data": daftar_drakor
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "pesan": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
