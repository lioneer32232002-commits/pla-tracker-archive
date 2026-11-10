"""國防部「中共解放軍臺海周邊海、空域動態」公告存檔。

每天由 GitHub Actions 執行：讀清單頁，把還沒存過的公告（網頁原文＋附件圖片）
存進 mnd/{年}/{日期}_{公告編號}/，並在 mnd/index.jsonl 追加一行（含 SHA-256）。
只新增、不覆寫：同一則公告存過就跳過，所以存檔裡的檔案就是當初抓到的樣子。

用法：
  python scripts/archive.py              # 讀清單第 1 頁起，直到整頁都已存過（最多 5 頁）
  python scripts/archive.py --pages 3    # 最多讀 3 頁
"""
import argparse, hashlib, html, json, os, re, ssl, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARC = os.path.join(ROOT, 'mnd')
INDEX = os.path.join(ARC, 'index.jsonl')
BASE = 'https://www.mnd.gov.tw'

# 國防部網站的憑證鏈在部分環境驗證不過（主站 pla-tracker 的抓取器也是同樣處理）。
# 內容完整性靠 index.jsonl 的 SHA-256，而不是靠傳輸層。
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def get(url, binary=False, timeout=15, tries=3):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (pla-tracker-archive)'})
            with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
                b = r.read()
            return b if binary else b.decode('utf-8', 'replace')
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2 + 3 * i)
    raise err


def list_page(n):
    t = get(f'{BASE}/news/plaactlist/{n}')
    out = []
    for m in re.finditer(r'href="[^"]*plaact/(\d+)"[^>]*>(.*?)</a>', t, re.S):
        txt = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(2)))).strip()
        out.append((m.group(1), txt))
    return out


def ext_of(b):
    if b[:3] == b'\xff\xd8\xff':
        return 'jpg'
    if b[:4] == b'\x89PNG':
        return 'png'
    if b[:4] == b'%PDF':
        return 'pdf'
    if b[:4] == b'GIF8':
        return 'gif'
    return 'bin'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pages', type=int, default=5)
    a = ap.parse_args()
    os.makedirs(ARC, exist_ok=True)
    seen = set()
    if os.path.exists(INDEX):
        for line in open(INDEX, encoding='utf-8'):
            if line.strip():
                seen.add(json.loads(line)['id'])
    added = 0
    for p in range(1, a.pages + 1):
        items = list_page(p)
        new = [(i, t) for i, t in items if i not in seen]
        for aid, title in new:
            m = re.match(r'(\d{2,3})\.(\d{2})\.(\d{2})', title)
            pub = f'{int(m.group(1)) + 1911}-{m.group(2)}-{m.group(3)}' if m else 'unknown'
            d = os.path.join(ARC, pub[:4], f'{pub}_{aid}')
            os.makedirs(d, exist_ok=True)
            page = get(f'{BASE}/news/plaact/{aid}')
            open(os.path.join(d, 'page.html'), 'w', encoding='utf-8').write(page)
            files = {}
            for fid in sorted(set(re.findall(r'File/(\d+)', page))):
                b = get(f'{BASE}/File/{fid}', binary=True)
                fn = f'File_{fid}.{ext_of(b)}'
                open(os.path.join(d, fn), 'wb').write(b)
                files[fn] = hashlib.sha256(b).hexdigest()
            rec = {'id': aid, 'page': p, 'pub': pub, 'title': title.split(' 點閱')[0],
                   'dir': os.path.relpath(d, ARC).replace(os.sep, '/'),
                   'html_sha256': hashlib.sha256(page.encode('utf-8')).hexdigest(),
                   'files': files, 'fetched_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
            with open(INDEX, 'a', encoding='utf-8') as f:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            seen.add(aid)
            added += 1
            print(f'[OK] {pub} {aid} ({len(files)} files)', flush=True)
            time.sleep(0.5)
        if not new:
            break   # 整頁都存過了，更舊的頁也一定存過
    print(f'[DONE] added {added}')


if __name__ == '__main__':
    sys.exit(main())
