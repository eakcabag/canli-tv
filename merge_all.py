#!/usr/bin/env python3
"""
Canlı TV - Tüm Kaynakları Birleştiren Akıllı Paket Oluşturucu
tv.m3u, by_iptv.m3u, by_iptv_full.m3u, ardatv_live.m3u ve anthology_raw.m3u
kaynaklarındaki canlı ve çalışan tüm yayınları tek bir temiz M3U paketinde birleştirir.
"""

from __future__ import annotations

import re
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HOME_DIR = Path("/data/data/com.termux/files/home")

SOURCES = [
    ("CanliTV", BASE_DIR / "tv.m3u"),
    ("BY-iPTV", BASE_DIR / "by_iptv.m3u"),
    ("BY-Full", BASE_DIR / "by_iptv_full.m3u"),
    ("ArdaTV", HOME_DIR / "ardatv_live.m3u"),
    ("Anthology", HOME_DIR / "anthology_raw.m3u"),
]

ADULT_FILTER_RE = re.compile(
    r"(adult|\+18|18\+|porn|xxx|erotik|erotic|brazzer|playboy|penthouse|hustler|"
    r"dorcel|redlight|vivid|beate\s*uhse|babes\s*hd|gay\s*tv|bsx24|superone|"
    r"s[uü]pr[iİ]z\s*tv|sexnet|sex\s*net|cam\s*show|redtraffic\.xyz|stream\.mcquack\.net/52/|"
    r"test_erox|test_extasy|test_brazzers|test_desire|test_basbes|19upsexer|findmy\.cam|"
    r"/(?:pov|bigtits|blowjob|gay|russian)\.m3u8|\bsex\b|\bsx\b|\berox+\b)",
    re.I,
)

# BY iPTV'de "kanal" olarak düşen bilinen Türk kanalları için isim tamamlama
URL_TITLE_HINTS = [
    (r"/kanald/", "Kanal D HD"),
    (r"androstreamliveatv|/atv/", "ATV HD"),
    (r"/startv/", "Star TV HD"),
    (r"/tv8/", "TV8 HD"),
    (r"/beyaztv/", "Beyaz TV HD"),
    (r"trtcocuk", "TRT Çocuk HD"),
    (r"/haberturktv/", "Habertürk TV HD"),
    (r"trtspor1|trtspor/", "TRT Spor HD"),
    (r"trtspor-yildiz", "TRT Spor Yıldız HD"),
    (r"trtbelgesel", "TRT Belgesel HD"),
    (r"trthaber", "TRT Haber HD"),
    (r"/aspor", "A Spor HD"),
    (r"htspor|ht-spor", "HT Spor HD"),
    (r"/dmax/", "DMAX HD"),
    (r"/tlc/", "TLC HD"),
    (r"fenerbahcetv", "FB TV HD"),
    (r"tjktv", "TJK TV HD"),
]

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def parse_m3u(path: Path, tag: str) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    curr_meta = None
    curr_ua = ""
    curr_ref = ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#EXTINF"):
                curr_meta = line
                m_ua = re.search(r'http-user-agent="([^"]+)"', line)
                curr_ua = m_ua.group(1) if m_ua else ""
                curr_ref = ""
            elif line.startswith("#EXTVLCOPT:http-user-agent="):
                curr_ua = line.split("=", 1)[1].strip()
            elif line.startswith("#EXTVLCOPT:http-referrer="):
                curr_ref = line.split("=", 1)[1].strip()
            elif re.match(r"^https?://", line, re.I):
                if curr_meta:
                    entries.append({
                        "source": tag,
                        "meta": curr_meta,
                        "ua": curr_ua,
                        "ref": curr_ref,
                        "url": line,
                    })
                curr_meta = None
                curr_ua = ""
                curr_ref = ""
    return entries


def infer_title(raw_title: str, url: str) -> str:
    title = raw_title.strip()
    if title.lower() in ("", "kanal", "tv", "yayin", "canli"):
        low_url = url.lower()
        for pat, nice in URL_TITLE_HINTS:
            if re.search(pat, low_url):
                return nice
    return title or "Canlı Kanal"


def normalize_group(raw_group: str, title: str, url: str) -> str:
    g = raw_group.upper()
    t = title.upper()
    u = url.lower()

    if any(k in g for k in ("SPOR", "LİG", "LIG", "MAÇ", "MAC")):
        return "⚽ SPOR KANALLARI"
    if any(k in t for k in ("BEIN", "BEİN", "S SPORT", "EXXEN", "TİVİBU", "TIVIBU", "TABİİ SPOR", "TABII SPOR", "TABİ SPOR", "TABI SPOR", "SMART SPOR", "EUROSPORT", "EURO SPOR", "TRT SPOR", "A SPOR", "A.SPOR", "HT SPOR", "FB TV", "GS TV", "TJK", "CBC SPORT", "FOX-SPORTS", "SKY-SPORTS", "ELEVEN SPORTS", "BT SPORT", "CANAL SPORT", "DUBAİ SPORT", "SPORTS", "MAC-SAAT", "MAC SAAT")):
        return "⚽ SPOR KANALLARI"
    if any(k in t for k in ("ÇOCUK", "COCUK", "MİNİKA", "MINIKA", "CARTOON", "DISNEY", "TRT EBA")):
        return "👶 ÇOCUK KANALLARI"
    if any(k in g for k in ("SİNEMA", "SINEMA", "FİLM", "FILM", "DİZİ", "DIZI")) or any(k in t for k in ("SİNE ", "LOCA", "SİNEMA")):
        return "🎬 SİNEMA & DİZİ"
    if any(k in g for k in ("BELGESEL", "DOĞA")) or any(k in t for k in ("BELGESEL", "BELGSEL", "DISCOVERY", "NATGEO", "VIASAT", "HISTORIY", "DOCUMAX", "TARİH", "BBCE", "TLC", "DMAX", "LOVENTR")):
        return "🦁 BELGESEL & DOĞA"
    if "ÇOCUK" in g or "COCUK" in g:
        return "👶 ÇOCUK KANALLARI"
    if "HABER" in g or any(k in t for k in ("HABER", "CNN", "NTV", "A HABER", "HALK TV", "SÖZCÜ", "TELE1", "BLOOMBERG", "TGRT")):
        return "📰 HABER KANALLARI"
    if "MÜZİK" in g or "MUZIK" in g or any(k in t for k in ("KRAL", "POWER", "NUMBER 1", "DREAM TÜRK")):
        return "🎵 MÜZİK & EĞLENCE"
    if "ULUSAL" in g or any(k in t for k in ("TRT 1", "TRT1", "ATV", "KANAL D", "SHOW TV", "STAR TV", "NOW", "FOX", "TV8", "BEYAZ TV", "KANAL 7", "A2")) or any(k in u for k in ("/kanald/", "/startv/", "/tv8/", "/beyaztv/")):
        return "🇹🇷 ULUSAL KANALLAR"
    if "TV+RADYO" in g:
        return "🇹🇷 ULUSAL KANALLAR"
    return "📺 DİĞER KANALLAR"


def fetch_probe(url: str, ua: str = "", timeout: float = 4.5) -> tuple[bool, str]:
    clean_ua = ua.encode("ascii", "ignore").decode() if ua else ""
    headers = {
        "User-Agent": clean_ua or DEFAULT_UA,
        "Referer": "https://www.google.com/",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            if resp.status >= 400:
                return False, ""
            ct = resp.headers.get("Content-Type", "").lower()
            body = resp.read(2048).decode("utf-8", errors="ignore")
            low_body = body.lower()
            if "<html" in low_body or "<!doctype html" in low_body:
                return False, ""
            ok = (
                "#extm3u" in low_body
                or "#ext" in low_body
                or "mpegurl" in ct
                or "video" in ct
                or "audio" in ct
            )
            return ok, body
    except Exception:
        return False, ""


def verify_entry(entry: dict) -> tuple[bool, dict]:
    url = entry["url"]
    if "youtube.com" in url or "youtu.be" in url:
        return False, entry

    ok, body = fetch_probe(url, entry.get("ua", ""))
    if not ok:
        return False, entry

    # GitHub raw .m3u8 wrapper'lari bazen iceride olu bir andro domaini tutar; ic hedefi de dogrula
    if "raw.githubusercontent.com" in url and "#EXT-X-STREAM-INF" in body:
        inner_urls = re.findall(r"https?://[^\s\r\n]+", body)
        if len(inner_urls) == 1:
            inner_ok, _ = fetch_probe(inner_urls[0], entry.get("ua", ""))
            if not inner_ok:
                return False, entry

    return True, entry


def build_clean_meta(entry: dict, title: str, group: str) -> str:
    meta = entry["meta"]
    # Orijinal tvg-id, tvg-logo, tvg-backup alanlarini koru
    m_id = re.search(r'tvg-id="([^"]*)"', meta)
    m_logo = re.search(r'tvg-logo="([^"]*)"', meta)
    m_backup = re.search(r'tvg-backup="([^"]*)"', meta)

    tvg_id = m_id.group(1) if m_id else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if tvg_id == "kanal":
        tvg_id = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    attrs = [f'tvg-id="{tvg_id}"', f'tvg-name="{title}"']
    if m_logo and m_logo.group(1):
        attrs.append(f'tvg-logo="{m_logo.group(1)}"')
    if m_backup and m_backup.group(1):
        attrs.append(f'tvg-backup="{m_backup.group(1)}"')
    attrs.append(f'group-title="{group}"')

    return f"#EXTINF:-1 {' '.join(attrs)},{title}"


def merge_all() -> Path:
    candidates = []
    seen_urls = set()

    for tag, path in SOURCES:
        for item in parse_m3u(path, tag):
            if ADULT_FILTER_RE.search(item["meta"] + " " + item["url"]):
                continue
            norm_url = item["url"].strip()
            if norm_url in seen_urls:
                continue
            seen_urls.add(norm_url)
            candidates.append(item)

    print(f"🔎 Toplam {len(candidates)} benzersiz aday akış doğrulanıyor...")

    alive = []
    with ThreadPoolExecutor(max_workers=24) as ex:
        for ok, item in ex.map(verify_entry, candidates):
            if ok:
                alive.append(item)

    print(f"✅ {len(alive)}/{len(candidates)} akış canlı ve çalışıyor!")

    group_order = [
        "🇹🇷 ULUSAL KANALLAR",
        "⚽ SPOR KANALLARI",
        "📰 HABER KANALLARI",
        "🎬 SİNEMA & DİZİ",
        "🦁 BELGESEL & DOĞA",
        "👶 ÇOCUK KANALLARI",
        "🎵 MÜZİK & EĞLENCE",
        "📺 DİĞER KANALLAR",
    ]
    rank = {g: i for i, g in enumerate(group_order)}

    formatted = []
    for idx, item in enumerate(alive):
        raw_title = item["meta"].split(",")[-1].strip()
        title = infer_title(raw_title, item["url"])
        m_grp = re.search(r'group-title="([^"]*)"', item["meta"])
        raw_grp = m_grp.group(1) if m_grp else ""
        group = normalize_group(raw_grp, title, item["url"])

        # Aynı kanal adının ikincil kaynaklarda karışmaması için sadece gerekirse kaynak etiketi eklemiyor, temiz tutuyoruz
        meta_line = build_clean_meta(item, title, group)
        formatted.append({
            "rank": rank.get(group, 99),
            "idx": idx,
            "group": group,
            "title": title,
            "meta": meta_line,
            "ua": item["ua"],
            "ref": item["ref"],
            "url": item["url"],
        })

    formatted.sort(key=lambda x: (x["rank"], x["idx"]))

    out_lines = ['#EXTM3U name="Canli TV - Tum Kaynaklar Tek Paket"\n\n']
    counts = {}
    for ch in formatted:
        counts[ch["group"]] = counts.get(ch["group"], 0) + 1
        out_lines.append(ch["meta"] + "\n")
        if ch["ua"]:
            out_lines.append(f"#EXTVLCOPT:http-user-agent={ch['ua']}\n")
        if ch["ref"]:
            out_lines.append(f"#EXTVLCOPT:http-referrer={ch['ref']}\n")
        out_lines.append(ch["url"] + "\n\n")

    out_path = BASE_DIR / "paket.m3u"
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

    for copy_dest in (HOME_DIR / "paket_iptv.m3u", Path("/sdcard/Download/paket_iptv.m3u")):
        try:
            with open(copy_dest, "w", encoding="utf-8") as f:
                f.writelines(out_lines)
        except Exception:
            pass

    print(f"📦 Tek paket oluşturuldu: {out_path} ({len(formatted)} canlı akış)")
    for g in group_order:
        if g in counts:
            print(f"   {counts[g]:3d}  {g}")
    return out_path


if __name__ == "__main__":
    merge_all()
