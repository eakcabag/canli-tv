# 📺 Canlı TV & VIP Spor - Akıllı M3U Çalma Listesi

Bu proje, Akıllı Televizyonlar (Smart TV), Android TV Box, Apple TV, Tablet, Telefon ve Bilgisayarlarda kullanılmak üzere hazırlanmış **otomatik güncellenen ve doğrulanmış** Türkçe IPTV çalma listesidir.

TV'nize bu linki **yalnızca bir kez** eklersiniz; arka planda yapılan tüm güncellemeler ve kanal yenilemeleri televizyonunuza otomatik yansır.

---

## 🔗 Sabit M3U Linkleri (Televizyonunuza Ekleyin)

Kumanda ile kolay yazabilmeniz için hem **kısa linkler** hem de doğrudan **GitHub Raw linkleri** hazırlandı:

| Liste Türü | Kısa TV Linki (Kumanda için) | Doğrudan GitHub Raw URL | Kanal Sayısı |
| :--- | :--- | :--- | :--- |
| 🌟 **Tüm Kanallar (VIP)** | `https://tinyurl.com/27e82c3d` | `https://raw.githubusercontent.com/eakcabag/canli-tv/main/tv.m3u` | ~130 Kanal |
| ⚽ **Sadece VIP Spor** | `https://tinyurl.com/2bfwuqjm` | `https://raw.githubusercontent.com/eakcabag/canli-tv/main/spor.m3u` | ~53 Kanal |
| 🇹🇷 **Ulusal & Haber** | `https://tinyurl.com/24klajrm` | `https://raw.githubusercontent.com/eakcabag/canli-tv/main/ulusal.m3u` | ~74 Kanal |

---

## 📱 Hangi Uygulamalarda Çalışır?

* **Android TV & Google TV:** TiviMate, OTT Navigator, IPTV Smarters Pro, Televizo
* **Samsung (Tizen) & LG (webOS):** SS IPTV, Smart IPTV, Nanomid, IBO Player
* **Apple TV & iOS:** GSE Smart IPTV, IPTVX, UHF, VLC Player
* **PC / Mac:** VLC Media Player, PotPlayer, Kodi

### 💡 TV'ye Nasıl Eklenir?
1. Kullandığınız IPTV uygulamasını açın (Örn: *TiviMate* veya *IPTV Smarters*).
2. **"Çalma Listesi Ekle"** veya **"Add M3U Playlist"** seçeneğini seçin.
3. Çalma listesi URL'si kısmına yukarıdaki **Kısa TV Linki**'ni girin:
   ```text
   https://tinyurl.com/27e82c3d
   ```
4. Çalma listesini kaydedin. Uygulamanız tüm kanalları logoları ve kategorileriyle birlikte anında yükleyecektir!

---

## 📡 Mevcut Kanal Kategorileri

* 🇹🇷 **Ulusal Kanallar:** TRT 1, ATV, Kanal D, Show TV, Star TV, NOW (Fox), TV8, TV8.5, Kanal 7, Beyaz TV...
* ⚽ **VIP Spor Kanalları:** beIN Sports 1-5 & Max, S Sport 1-2, Exxen Spor 1-8, Tivibu Spor 1-4, Tabii Spor 1-6, Eurosport 1-2, TRT Spor...
* 📰 **Haber Kanalları:** NTV, CNN Türk, Habertürk, TRT Haber, A Haber, Sözcü TV, Halk TV, Tele1, Bloomberg HT...
* 🦁 **Belgesel & Çocuk:** TRT Belgesel, TRT Çocuk, Minika GO, Minika Çocuk, DMAX, TLC...
* 🎵 **Müzik & Eğlence:** Kral Pop, PowerTürk, Dream Türk, Number 1 TV...

---

## ⚡ Otomatik Güncelleme
Kanal linkleri veya yayın kaynakları değiştiğinde Termux üzerinden tek satırla:
```bash
python3 updater.py
```
komutu çalıştırıldığında linkler test edilir, yedek akışlar devreye alınır ve GitHub deposu anında güncellenir.
