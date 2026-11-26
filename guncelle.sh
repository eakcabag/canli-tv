#!/data/data/com.termux/files/usr/bin/bash
# Canlı TV & BY iPTV Otomatik Tek Tuş Güncelleyici
set -e

echo "🚀 [1/3] BY iPTV PR0 yayınları taranıyor ve test ediliyor..."
iptv-m3u --refresh --verify --only-live --split --report --dump-json

echo "📋 [2/3] Dosyalar repoya kopyalanıyor..."
cp /sdcard/Download/IPTV-M3U/iptv.m3u ~/canli-tv/by_iptv.m3u
cp /sdcard/Download/IPTV-M3U/iptv.m3u /sdcard/Download/by_iptv.m3u
rm -rf ~/canli-tv/bolumler
cp -r /sdcard/Download/IPTV-M3U/bolumler ~/canli-tv/

python3 - <<'PY' || true
import re, sys, urllib.request
sys.path.insert(0, "/data/data/com.termux/files/home/re/base2")
import iptv_m3u

req = urllib.request.Request(
    "https://config.e-droid.net/srv/config.php?v=133&vname=9.8&idapp=1899126&idusu=0&cod_g=0&gp=0&am=0&idl=tr&pa_env=1&pa=TR&pn=com.by.asambek.app&aid=1234567890abcdef",
    headers={"User-Agent": "Android Vinebre Software"}
)
content = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
_, items = iptv_m3u.parse_config(content)
roots, children, _ = iptv_m3u.build_tree(items)
blocked_ids = set()
def mark_adult(sid, parent_adult=False):
    it = items.get(sid, {})
    tit = it.get("tit", "")
    is_adult = parent_adult or iptv_m3u.is_adult_entry(title=tit, group=tit)
    if is_adult:
        blocked_ids.add(sid)
    for cid in children.get(sid, []):
        if is_adult:
            blocked_ids.add(cid)
        if items.get(cid, {}).get("tipo") == "12":
            mark_adult(cid, is_adult)
for r in roots:
    mark_adult(r)

m = ["#EXTM3U"]
for iid, d in items.items():
    if iid in blocked_ids:
        continue
    tit = d.get("tit", "").strip()
    if not tit or iptv_m3u.is_adult_entry(title=tit):
        continue
    ua = f' http-user-agent="{d["ua"]}"' if d.get("ua") else ""
    for u in sorted(set(re.findall(r'https?://[^\s<>"\'\)]+', d.get("url", "") + " " + d.get("k", "")))):
        if iptv_m3u.is_adult_entry(title=tit, url=u):
            continue
        m.append(f'#EXTINF:-1 tvg-name="{tit}"{ua},{tit}')
        m.append(u)
with open("/data/data/com.termux/files/home/canli-tv/by_iptv_full.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m) + "\n")
print(f"by_iptv_full.m3u yazildi ({(len(m)-1)//2} akis)")
PY

echo "📺 [3/3] Standart Canlı TV CDN listesi güncelleniyor ve GitHub'a pushlanıyor..."
cd ~/canli-tv
python3 updater.py || true

git add .
if ! git diff-index --quiet HEAD --; then
    git commit -m "auto: kanallar ve CDN linkleri güncellendi ($(date +'%d.%m.%Y %H:%M'))"
    git push origin main
    echo "🎉 BÜTÜN LİSTELER VE GİTHUB BAŞARIYLA GÜNCELLENDİ!"
else
    echo "ℹ️ Değişiklik yok, tüm yayınlar zaten en güncel halinde."
fi
