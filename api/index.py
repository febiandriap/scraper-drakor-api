from flask import Flask, jsonify
from bs4 import BeautifulSoup
import cloudscraper
import os

app = Flask(__name__)

TARGET_URL = os.environ.get('WEB_DRAKOR_URL', 'https://xdrakor71.kita.mom')

@app.route('/')
def home():
    return jsonify({
        "status": "aktif",
        "pesan": "Mesin Scraper Python Berjalan dengan Cloudscraper!",
        "target_saat_ini": TARGET_URL
    })

@app.route('/drakor/terbaru')
def get_terbaru():
    try:
        # Membuat mesin pengeruk yang menyamar sebagai browser asli
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Mengunjungi web menggunakan cloudscraper (bukan requests lagi)
        response = scraper.get(TARGET_URL, timeout=15)
        
        if response.status_code != 200:
            return jsonify({
                "status": "gagal",
                "kode_http": response.status_code,
                "pesan": "Masih diblokir Cloudflare.",
                "potongan_html": response.text[:200]
            })

        soup = BeautifulSoup(response.text, 'html.parser')
        daftar_drakor = []
        
        kotak_kotak_film = soup.select('.card.mx-auto')
        
        for kotak in kotak_kotak_film:
            # Ambil Judul
            tag_judul = kotak.select_one('.titit')
            if tag_judul:
                teks_list = list(tag_judul.stripped_strings)
                judul_bersih = teks_list[0] if len(teks_list) > 0 else "Judul Tidak Diketahui"
            else:
                judul_bersih = ""
            
            # Ambil Link Gambar Poster
            tag_gambar = kotak.select_one('img.poster')
            link_poster = tag_gambar.get('src') if tag_gambar else ""
            
            # Ambil Link Detail Film
            tag_link = kotak.select_one('a.poster')
            link_detail_path = tag_link.get('href') if tag_link else ""
            
            # Ambil Status/Episode
            tag_eps = kotak.select_one('.rate')
            episode_saat_ini = tag_eps.text.strip() if tag_eps else ""
            
            if link_detail_path and judul_bersih:
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
