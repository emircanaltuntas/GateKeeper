# 🛡️ GateKeeper

**SimPy Tabanlı Ağ Geçidi Trafik ve Güvenlik Simülasyonu**

Mersin Üniversitesi — Bilişim Sistemleri ve Teknolojileri (CTIS) Bölümü  
Benzetim Programları Dersi | 2025–2026 Akademik Yılı

---

## 📌 Proje Hakkında

GateKeeper, sınırlı kapasiteli bir ağ geçidinde farklı öncelik seviyelerine sahip paketlerin nasıl yönetildiğini simüle eden bir ayrık olay simülasyonu (DES) projesidir. Katmanlı bir drop politikası uygulayarak, yük altında kritik trafiğin korunup korunmadığını test eder.

### Çözdüğü Problem

Gerçek hayatta ağ geçitleri sınırlı kapasiteye sahiptir. Trafik yoğunlaştığında bazı paketlerin düşürülmesi kaçınılmaz hale gelir. Rastgele düşürme yerine **öncelik tabanlı katmanlı drop politikası** uygulanarak kritik trafiğin (admin paketleri) her koşulda korunması sağlanır.

---

## 🗂️ Paket Türleri

| Paket Türü | Öncelik | Ort. Geliş Aralığı | Açıklama |
|------------|---------|---------------------|----------|
| Admin | 0 (en yüksek) | 8.0 birim | Yönetici komutları, asla drop edilmez |
| Normal | 1 | 2.0 birim | Standart kullanıcı trafiği |
| Şüpheli | 2 (en düşük) | 1.2 birim | Potansiyel tehdit, ilk drop edilen |

**Drop Eşikleri:** Kuyruk > 10 → şüpheli paketler düşürülür | Kuyruk > 13 → normal paketler de düşürülür | Admin paketlerine dokunulmaz.

---

## ⚙️ Kullanılan Teknolojiler

| Teknoloji | Kullanım Amacı |
|-----------|---------------|
| **Python 3** | Ana programlama dili |
| **SimPy** | Ayrık olay simülasyon motoru, PriorityResource ile öncelikli kuyruk yönetimi |
| **random** | Üstel dağılımla stokastik paket üretimi (`expovariate`) |
| **statistics** | Ortalama bekleme süresi, drop oranı hesaplama |
| **Streamlit** | Web tabanlı arayüz |
| **Plotly** | Grafik ve görselleştirmeler |

---

## 🖥️ Arayüz (Streamlit)

Kullanıcı arayüzü üzerinden şu parametreler ayarlanabilir:

- Sunucu kapasitesi (1–10)
- Kuyruk sınırı
- Paket geliş oranları (slider)
- Simülasyon süresi
- Seed değeri (tekrarlanabilirlik için)

---

## 📊 Görselleştirmeler

- **Kuyruk Doluluk Grafiği** — Zamana bağlı kuyruk dalgalanması ve eşik çizgileri
- **Isı Haritası (Heatmap)** — Paket türlerine göre zaman dilimlerindeki yoğunluk
- **Drop Oranı Pasta Grafiği** — Her paket türünün toplam drop içindeki payı
- **Bekleme Süresi Bar Chart** — Öncelik mekanizmasının bekleme süresine etkisi

---

## 🚀 Kurulum ve Çalıştırma

```bash
# Repoyu klonlayın
git clone https://github.com/emircanaltuntas/GateKeeper.git
cd GateKeeper

# Gereksinimleri yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
streamlit run app.py
```

---

## 👥 Ekip

| İsim | Öğrenci No |
|------|-----------|
| Ahmet Feyzi Gülmez | 21430070039 |
| Emircan Altuntaş | 22430070020 |
| Ahmet Duran Gökçe | 21430070043 |

---

## 📚 Kaynaklar

- [SimPy Documentation](https://simpy.readthedocs.io)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- Matloff, N. (2008). *Introduction to Discrete-Event Simulation and the SimPy Language*
- Stallings, W. (2017). *Network Security Essentials*, 6th Edition
- Gross, D. et al. (2008). *Fundamentals of Queueing Theory*, 4th Edition
