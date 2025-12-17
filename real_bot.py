import feedparser
import time
import ssl
import random
from datetime import datetime, timedelta
from time import mktime
from supabase import create_client, Client
from deep_translator import GoogleTranslator

# --- 1. AYARLAR ---
SUPABASE_URL = "https://frsgnspmuccvcrskzqis.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyc2duc3BtdWNjdmNyc2t6cWlzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU4MzE3MTcsImV4cCI6MjA4MTQwNzcxN30.SuQfuMenL41ACxTuD4baeo-_T7aZr6G0fF9g8WMF8uM"

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Bağlantı Hatası: {e}")
    exit()

# --- 2. RSS KAYNAKLARI ---
RSS_SOURCES = [
    {"name": "United Nations (UNGM)", "url": "https://www.ungm.org/Public/Feed/Notices", "region": "Global", "sector": "Genel"},
    {"name": "World Bank Projects", "url": "http://projects.worldbank.org/resources/procurement/notices/rss", "region": "Global", "sector": "Altyapı"},
    {"name": "TED (Avrupa)", "url": "https://ted.europa.eu/RSS/rss_DO_S_EN.xml", "region": "Avrupa", "sector": "Kamu"},
    {"name": "Asian Dev Bank", "url": "https://www.adb.org/rss/tenders", "region": "Asya", "sector": "Kalkınma"},
    {"name": "African Dev Bank", "url": "https://www.afdb.org/en/rss/corporate-procurement", "region": "Afrika", "sector": "Altyapı"},
    # Mercosur'u kaldırdık çünkü çok fazla "Haber" paylaşıyor, ilan az.
    {"name": "Canada BuyAndSell", "url": "https://buyandsell.gc.ca/procurement-data/tenders/feed/atom", "region": "Kuzey Amerika", "sector": "Devlet"},
    {"name": "AusTender", "url": "https://www.tenders.gov.au/Atm/Rss", "region": "Okyanusya", "sector": "Hizmet"}
]

# --- 3. AKILLI FİLTRE (Sadece Alım Talebi) ---
# Bu kelimeler geçiyorsa KESİN AL
POSITIVE_KEYWORDS = [
    "tender", "procurement", "supply", "purchase", "rfp", "rfq", "bid", 
    "invitation", "construction", "acquisition", "services", "goods", 
    "contract notice", "solicitation", "expression of interest", "buying"
]

# Bu kelimeler geçiyorsa KESİN REDDET (Haberler)
NEGATIVE_KEYWORDS = [
    "contract award", "awarded", "winner", "result", "news", "press release", 
    "report", "study", "meeting", "conference", "hiring", "job", "vacancy", 
    "policy", "announced", "eyes", "status", "investment plan", "launch", "ceremony"
]

def is_trade_lead(title, desc):
    """Metin analizine göre bu bir ilan mı yoksa haber mi?"""
    content = (title + " " + desc).lower()
    
    # Haber kelimeleri varsa reddet
    for bad in NEGATIVE_KEYWORDS:
        if bad in content:
            return False
            
    # İhale kelimeleri varsa kabul et
    for good in POSITIVE_KEYWORDS:
        if good in content:
            return True
            
    return False

def clean_text(html_text):
    import re
    if not html_text: return ""
    text = re.sub(re.compile('<.*?>'), '', html_text).replace('\n', ' ').strip()
    return text[:1000]

def translate_to_turkish(text):
    """Google Translate ile Türkçe'ye çevir"""
    if not text or len(text) < 3: return text
    try:
        # 1 saniye bekle ki Google engellemesin
        time.sleep(0.5)
        translated = GoogleTranslator(source='auto', target='tr').translate(text)
        return translated
    except:
        return text 

def fetch_global_data():
    print(f"\n🌍 %100 TÜRKÇE & GERÇEK İLAN TARAMASI BAŞLADI... [{datetime.now().strftime('%H:%M:%S')}]")
    print("==================================================")
    
    cutoff_date = datetime.now() - timedelta(days=60)
    total_added = 0
    skipped_news = 0
    
    for source in RSS_SOURCES:
        print(f"📡 {source['name']} ({source['region']}) Taranıyor...")
        
        try:
            feed = feedparser.parse(source['url'])
            if not feed.entries: continue
            
            # Her kaynaktan 5 ilan dene
            for entry in feed.entries[:5]:
                
                # Tarih
                try:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        entry_date = datetime.fromtimestamp(mktime(entry.published_parsed))
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        entry_date = datetime.fromtimestamp(mktime(entry.updated_parsed))
                    else:
                        entry_date = datetime.now()
                except:
                    entry_date = datetime.now()

                if entry_date < cutoff_date: continue

                # Veri
                raw_title = entry.title
                raw_desc = ""
                if 'description' in entry: raw_desc = entry.description
                elif 'summary' in entry: raw_desc = entry.summary
                elif 'content' in entry: raw_desc = entry.content[0].value
                
                clean_desc = clean_text(raw_desc)

                # --- FİLTRE ---
                if not is_trade_lead(raw_title, clean_desc):
                    skipped_news += 1
                    continue
                
                # --- ÇEVİRİ (BAŞLIK + AÇIKLAMA) ---
                print(f"      ...Çeviriliyor: {raw_title[:30]}...")
                final_title = translate_to_turkish(raw_title)
                final_desc = translate_to_turkish(clean_desc)
                
                if not final_desc: final_desc = "Detaylar için lütfen kaynak linke gidiniz."

                link = entry.link
                
                # --- İLETİŞİM (SAHTE YOK) ---
                contact_email = None
                contact_phone = None
                
                # Sadece kesin bilinen gerçek mailler
                if "ungm.org" in link: contact_email = "registry@ungm.org"
                
                # Ülke Tespiti (Türkçe)
                detected_country = source['region']
                common_countries = ["Turkey", "Germany", "France", "USA", "China", "India", "Brazil", "Russia", "Japan", "UK", "Italy", "Spain", "Canada", "Australia", "Egypt"]
                for c in common_countries:
                    if c in raw_title or c in clean_desc:
                        tr_map = {"Turkey":"Türkiye", "Germany":"Almanya", "France":"Fransa", "USA":"ABD", "China":"Çin", "India":"Hindistan", "Brazil":"Brezilya", "Russia":"Rusya", "Japan":"Japonya", "UK":"İngiltere", "Italy":"İtalya", "Spain":"İspanya", "Canada":"Kanada", "Australia":"Avustralya", "Egypt":"Mısır"}
                        detected_country = tr_map.get(c, c)
                        break

                lead = {
                    "title": final_title,
                    "country": detected_country,
                    "description": final_desc,
                    "quantity": "İhale Dosyasında",
                    "sector": source['sector'],
                    "payment_terms": "Resmi Prosedür",
                    "source_name": source['name'],
                    "original_link": link,
                    "website": None, # Web sitesi YOK
                    "company_name": source['name'], # Kaynak Kurum Adı
                    "contact_email": contact_email, # Varsa gerçek, yoksa BOŞ
                    "contact_phone": contact_phone, # BOŞ
                    "trust_score": 100,
                    "is_verified": True,
                    "premium_only": True,
                    "published": True,
                    "created_at": entry_date.isoformat(),
                    "publish_date": entry_date.isoformat()
                }

                try:
                    supabase.table("leads").insert(lead).execute()
                    print(f"      📥 [EKLENDİ] {final_title[:40]}...")
                    total_added += 1
                except:
                    pass
                
                time.sleep(1) # Çeviri API'sini yormamak için bekle

        except Exception as e:
            print(f"Hata: {e}")

    print("--------------------------------------------------")
    print(f"🎉 TEMİZLİK BİTTİ! {skipped_news} adet haber elendi.")
    print(f"✅ {total_added} adet TÜRKÇE ALIM TALEBİ eklendi.")

if __name__ == "__main__":
    fetch_global_data()