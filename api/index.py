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
        # Menambahkan Headers ekstra agar menyamar lebih meyakinkan
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        
        # CEK SISTEM KEAMANAN: Jika bukan 200 (OK), berarti diblokir!
        if response.status_code != 200:
            return jsonify({
                "status": "gagal",
                "kode_http": response.status_code,
                "pesan": "Server Vercel diblokir oleh anti-bot web target (seperti Cloudflare).",
                "potongan_html": response.text[:200]
            })

        soup = BeautifulSoup(response.text, 'html.parser')
        daftar_drakor = []
        
        # MENGGUNAKAN CSS SELECTOR (Jauh lebih kuat untuk membaca class berspasi)
        kotak_kotak_film = soup.select('.card.mx-auto')
        
        for kotak in kotak_kotak_film:
            # 1. Ambil Judul
            tag_judul = kotak.select_one('.titit')
            if tag_judul:
                # Mengambil teks pertama saja sebelum ada tag <br>
                teks_list = list(tag_judul.stripped_strings)
                judul_bersih = teks_list[0] if len(teks_list) > 0 else "Judul Tidak Diketahui"
            else:
                judul_bersih = ""
            
            # 2. Ambil Link Gambar Poster
            tag_gambar = kotak.select_one('img.poster')
            link_poster = tag_gambar.get('src') if tag_gambar else ""
            
            # 3. Ambil Link Detail Film
            tag_link = kotak.select_one('a.poster')
            link_detail_path = tag_link.get('href') if tag_link else ""
            
            # 4. Ambil Status/Episode
            tag_eps = kotak.select_one('.rate')
            episode_saat_ini = tag_eps.text.strip() if tag_eps else ""
            
            if link_detail_path and judul_bersih:
                # Gabungkan dengan URL target agar menjadi link lengkap jika diperlukan
                daftar_drakor.append({
                    "judul": judul_bersih,
                    "poster": link_poster,
                    "endpoint": link_detail_path,
                    "episode": episode_saat_ini
                })
        
        return jsonify({
            "status": "sukses",
            "kode_http": response.status_code,
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
