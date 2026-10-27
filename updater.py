#!/usr/bin/env python3
"""
Canli TV - Akıllı IPTV Güncelleyici ve Doğrulayıcı
Bu script listelerdeki akışları test eder, yedek linkleri devreye sokar ve GitHub'a otomatik pushlar.
"""

import os
import re
import sys
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_stream(url, timeout=3.5):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0",
                "Referer": "https://www.google.com/",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 301, 302)
    except Exception:
        return False

def update_playlist():
    tv_path = BASE_DIR / "tv.m3u"
    if not tv_path.exists():
        print("❌ tv.m3u bulunamadı!")
        return False

    with open(tv_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    channels = []
    curr_meta = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            curr_meta = line
        elif line.startswith("http"):
            if curr_meta:
                backup = None
                m = re.search(r'tvg-backup="([^"]+)"', curr_meta)
                if m:
                    backup = m.group(1).strip()
                channels.append({"meta": curr_meta, "url": line, "backup": backup})
                curr_meta = None

    print(f"📡 Toplam {len(channels)} kanal test ediliyor...")

    def test_ch(ch):
        is_ok = check_stream(ch["url"])
        if not is_ok and ch.get("backup"):
            if check_stream(ch["backup"]):
                print(f"🔄 Yedek akışa geçildi: {ch['meta'][:40]}")
                ch["url"] = ch["backup"]
                is_ok = True
        return is_ok, ch

    alive = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(test_ch, c) for c in channels]
        for f in as_completed(futures):
            ok, ch = f.result()
            if ok:
                alive.append(ch)

    print(f"✅ {len(alive)}/{len(channels)} kanal aktif ve çalışıyor.")

    # Re-write tv.m3u
    header = [
        '#EXTM3U name="Turk Canli TV - VIP Guncel Liste"\n',
        f'# Son Güncelleme: {subprocess.getoutput("date \'+%Y-%m-%d %H:%M\'")}\n\n'
    ]
    with open(tv_path, "w", encoding="utf-8") as f:
        f.writelines(header)
        for ch in alive:
            f.write(ch["meta"] + "\n")
            f.write(ch["url"] + "\n\n")

    # Update spor.m3u
    sports_keywords = ["spor", "bein", "exxen", "tivibu", "tabii", "euro", "futbol", "nba", "formula"]
    sports = [c for c in alive if any(k in c["meta"].lower() for k in sports_keywords)]
    with open(BASE_DIR / "spor.m3u", "w", encoding="utf-8") as f:
        f.write('#EXTM3U name="VIP Canli Spor Kanallari"\n\n')
        for c in sports:
            f.write(c["meta"] + "\n")
            f.write(c["url"] + "\n\n")

    # Update ulusal.m3u
    ulusal = [c for c in alive if any(k in c["meta"] for k in ["ULUSAL", "HABER", "BELGESEL", "MÜZİK"])]
    with open(BASE_DIR / "ulusal.m3u", "w", encoding="utf-8") as f:
        f.write('#EXTM3U name="Turk Ulusal & Haber Kanallari"\n\n')
        for c in ulusal:
            f.write(c["meta"] + "\n")
            f.write(c["url"] + "\n\n")

    return True

def git_push():
    print("🚀 Değişiklikler GitHub'a gönderiliyor...")
    os.chdir(BASE_DIR)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Kanal listesi otomatik güncellendi"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🎉 GitHub başarıyla güncellendi! TV'nizdeki liste anında yenilendi.")

if __name__ == "__main__":
    if update_playlist():
        git_push()
