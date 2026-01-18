import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import urllib3

# 1. SAYFA AYARLARI (En üstte olmalı)
st.set_page_config(page_title="TOKİ İhale Takip", layout="wide")

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. GÖRSEL TASARIM (CSS - Füme Tonlar ve Kart Yapısı)
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Sol Menü Şehir Butonları */
    .stButton > button {
        width: 100%;
        text-align: left !important;
        border-radius: 6px;
        background-color: #ffffff;
        color: #555555;
        border: 1px solid #e0e0e0;
        margin-bottom: 4px;
        font-weight: 600;
    }

    /* İhale Çerçevesi (Kart Tasarımı) */
    .ihale-kart {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 10px solid #347083;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* İhale Tarih ve Saat (DEV BOYUT) */
    .ihale-tarih-saat {
        color: #2c3e50;
        font-weight: 900;
        font-size: 30px; 
        margin-bottom: 12px;
        display: block;
    }
    
    /* İşin Adı (BÜYÜK BOYUT) */
    .ihale-is-adi {
        color: #444444; 
        font-size: 24px; 
        font-weight: 600;
        line-height: 1.5;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. VERİ ÇEKME FONKSİYONU
@st.cache_data(ttl=300)
def veri_cek():
    url = "https://www.toki.gov.tr/ihale-tarihleri"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table:
            return []
        
        rows = table.find_all('tr')[1:]
        liste = []
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 4:
                isim = tds[1].get_text(strip=True)
                zaman = tds[3].get_text(strip=True)
                match = re.search(r"([A-ZÇĞİÖŞÜa-zçğıöşü]+)\s+İli", isim)
                sehir = match.group(1).upper() if match else "DİĞER"
                liste.append({"il": sehir, "is": isim, "zaman": zaman})
        return liste
    except Exception:
        return []

# 4. EKRAN DÜZENİ VE FİLTRELEME
data = veri_cek()

if not data:
    st.error("Verilere ulaşılamıyor. Lütfen interneti kontrol edin.")
else:
    sol, sag = st.columns([1, 4])
    
    with sol:
        st.markdown("### 📍 İLLER")
        if st.button("🌍 TÜM İLLER", key="all_btn"):
            st.session_state['f'] = "ALL"
            
        iller = sorted(list(set(d['il'] for d in data)))
        for il in iller:
            if st.button(il, key=f"btn_{il}"):
                st.session_state['f'] = il

    with sag:
        secili_il = st.session_state.get('f', 'ALL')
        st.markdown(f"### 📄 {secili_il} İHALE LİSTESİ")
        
        filtreli = data if secili_il == "ALL" else [d for d in data if d['il'] == secili_il]
        
        if not filtreli:
            st.info("Bu kriterlere uygun ihale bulunamadı.")
        else:
            for h in filtreli:
                # Kapanmamış parantez hatasını düzelten kısım:
                st.markdown(f"""
                    <div class="ihale-kart">
                        <span class="ihale-tarih-saat">🗓️ {h['zaman']}</span>
                        <div class="ihale-is-adi">{h['is']}</div>
                    </div>
                """, unsafe_allow_html=True)