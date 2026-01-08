# CPU Zamanlama Algoritmaları Web Simülatörü

Bu proje, 6 farklı CPU zamanlama algoritmasını (FCFS, SJF, PJF, RR, Preemptive SJF, Preemptive PJF) simüle eden ve sonuçları etkileşimli bir web arayüzü üzerinden sunan bir uygulamadır.

## Özellikler
- **Web Arayüzü:** Streamlit tabanlı kolay kullanım.
- **Dosya Yükleme:** Kendi `.csv` süreç listenizi yükleyerek analiz yapma.
- **Görselleştirme:** Algoritmaların performansını karşılaştıran grafikler.
- **Raporlama:** "Zamanlama Tablolarını" (Gantt çizelgesi verileri) `.txt` veya `.csv` olarak indirme imkanı.

---

## Kurulum ve Çalıştırma

### 1. Projeyi Klonlayın
Öncelikle terminal veya CMD üzerinden projeyi bilgisayarınıza indirin:

```cmd
git clone https://github.com/yvetuya-Air/lisans_isletim_sistemi_dersi_odev1.git
cd lisans_isletim_sistemi_dersi_odev1
```

### 2. Gerekli Kütüphaneleri Yükleyin
Uygulamanın çalışması için gerekli olan Python kütüphanelerini yükleyin:
```cmd
pip install pandas matplotlib streamlit
```

### 3. Uygulamayı Başlatın
Web arayüzünü açmak için aşağıdaki komutu terminale yazın:
```cmd
python -m streamlit run Web_devoir.py
```

## Kullanım Adımları
- Uygulama açıldığında CSV dosyasını yukleyin.
- Algoritmaların hesaplanmasını butona basin.
- Zamanlama Tabloları indirin.
- Karşılaştırma Tabloları analiz edin.
