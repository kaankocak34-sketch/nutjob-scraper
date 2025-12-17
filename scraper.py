import time
import random
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. AYARLAR ---
SUPABASE_URL = "https://frsgnspmuccvcrskzqis.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyc2duc3BtdWNjdmNyc2t6cWlzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU4MzE3MTcsImV4cCI6MjA4MTQwNzcxN30.SuQfuMenL41ACxTuD4baeo-_T7aZr6G0fF9g8WMF8uM"

# Bağlantıyı kur
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Bağlantı Hatası: {e}")
    exit()

# --- 2. PROFESYONEL VERİ HAVUZU ---
COUNTRIES = ["Almanya", "ABD", "Fransa", "Katar", "İngiltere", "Hollanda", "İtalya", "İspanya", "Rusya", "BAE", "Suudi Arabistan", "Çin"]
SECTORS = ["Gıda & Tarım", "İnşaat & Yapı", "Tekstil", "Otomotiv", "Makine", "Kimya", "Mobilya", "Elektronik"]
QUANTITIES = ["1 Konteyner (20ft)", "2 Tır (Full)", "5.000 Adet", "25 Ton", "Yıllık 100.000 Adet", "Numune Alımı", "Aylık 2 Konteyner", "10.000 Metre"]
PAYMENT_TERMS = ["Akreditif (L/C)", "Peşin (T/T)", "%30 Avans - %70 Yüklemede", "Vesaik Mukabili (CAD)", "Vadeli Çek"]
SOURCES = ["Global Trade Plaza", "TurkishExporter", "Alibaba", "ThomasNet", "EuroPages", "Kompass", "Direct Inquiry"]

# Şablon İlan Başlıkları
TEMPLATES = [
    "{country} firması acil {product} tedarikçisi arıyor",
    "{product} için yıllık alım anlaşması ({country})",
    "{country} merkezli firma {product} ithal edecek",
    "Yüksek tonajlı {product} alımı - {country}",
    "{country} otel projesi için {product} ihtiyacı",
    "{country} pazarı için {product} distribütörü aranıyor"
]

PRODUCTS = {
    "Gıda & Tarım": ["Kuru Kayısı", "Fındık", "Zeytinyağı", "Domates Salçası", "Dondurulmuş Tavuk", "Makarna", "Un", "Mercimek", "Konserve Balık"],
    "İnşaat & Yapı": ["Mermer Blok", "Seramik Karo", "Çelik Kapı", "Alçıpan", "İnşaat Demiri", "PVC Pencere", "Boya", "Çimento"],
    "Tekstil": ["Pamuklu Kumaş", "Bebek Giyim", "Havlu & Bornoz", "Kot Pantolon", "İplik", "Ev Tekstili", "Spor Giyim"],
    "Makine": ["CNC Tezgahı", "Paketleme Makinesi", "Tarım Aletleri", "Jeneratör", "Konveyör Bant", "Gıda İşleme Hattı"],
    "Kimya": ["Plastik Hammadde", "Gübre", "Endüstriyel Boya", "Deterjan", "Kozmetik Ürünleri"],
    "Mobilya": ["Ofis Koltuğu", "Otel Mobilyası", "Mutfak Dolabı", "Bahçe Mobilyası"],
    "Otomotiv": ["Fren Diski", "Lastik", "Akü", "Yedek Parça", "Motor Yağı"],
    "Elektronik": ["Fiber Kablo", "Güvenlik Kamerası", "Güneş Paneli", "LED Aydınlatma"]
}

# --- 3. BOT FONKSİYONU ---
def generate_lead():
    sector = random.choice(list(PRODUCTS.keys()))
    product = random.choice(PRODUCTS[sector])
    country = random.choice(COUNTRIES)
    qty = random.choice(QUANTITIES)
    source = random.choice(SOURCES)
    
    title = random.choice(TEMPLATES).format(country=country, product=product)
    
    # İletişim bilgisi oluştur
    has_contact = random.random() > 0.1 
    comp_suffix = random.choice(["Gmbh", "LLC", "Ltd", "S.A.", "Co.", "Trading"])
    company = f"{country} {product.split()[0]} {comp_suffix}" if has_contact else None
    
    phone = f"+{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}" if has_contact else None
    
    clean_name = "example"
    if company:
        clean_name = (company.lower()
                      .replace(' ', '')
                      .replace('.', '')
                      .replace('ü', 'u')
                      .replace('ı', 'i')
                      .replace('ş', 's')
                      .replace('ç', 'c')
                      .replace('ö', 'o')
                      .replace('ğ', 'g')
                      .replace('İ', 'i'))
    
    web = f"www.{clean_name}.com" if company else None
    email = f"info@{clean_name}.com" if company else None

    # Tarih
    fake_date = datetime.now() - timedelta(hours=random.randint(1, 48))

    # Link oluştur (Boş kalmaması için)
    fake_link = f"https://www.{source.lower().replace(' ', '')}.com/lead/{random.randint(100000, 999999)}"

    data = {
        "title": title,
        "country": country,
        "description": f"{country} bölgesindeki toptancılarımız için düzenli olarak {product} tedarik etmek istiyoruz. Toplam {qty} miktarında alım planlanmaktadır. Ürün spekleri ve fiyat teklifi için iletişime geçiniz.",
        "quantity": qty,
        "sector": sector,
        "payment_terms": random.choice(PAYMENT_TERMS),
        "source_name": source,
        "original_link": fake_link, # EKLENEN SATIR BURASI
        
        # İletişim
        "company_name": company,
        "contact_phone": phone,
        "contact_email": email,
        "website": web,
        
        "trust_score": random.randint(75, 99),
        "is_verified": random.random() > 0.4,
        "premium_only": random.random() > 0.6,
        "published": True,
        
        # Tarih Alanları
        "created_at": fake_date.isoformat(),
        "publish_date": fake_date.isoformat() 
    }
    return data

def run_bot():
    print(f"\n🚀 Nutjob V3.4 Veri Botu Başlatıldı... [{datetime.now().strftime('%H:%M:%S')}]")
    print("--------------------------------------------------")
    print("Veritabanına profesyonel ilanlar gönderiliyor...\n")
    
    count = 0
    try:
        while True:
            lead = generate_lead()
            
            # Supabase'e Yaz
            response = supabase.table("leads").insert(lead).execute()
            
            count += 1
            status = "👑 PREMIUM" if lead['premium_only'] else "🌍 HERKES"
            print(f"✅ [{count}] {lead['country']} -> {lead['sector']} ({status})")
            
            wait_time = random.randint(3, 8)
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n🛑 Bot durduruldu. İyi çalışmalar!")
    except Exception as e:
        print(f"\n❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    run_bot()