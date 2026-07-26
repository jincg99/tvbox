import requests
import json
import re

# ---- 配置：不同格式的源分开填 ----

TXT_SOURCES = [
    "https://raw.githubusercontent.com/kimcg2212/tkbox/main/tv.txt",
]

M3U_SOURCES = [
    "https://raw.githubusercontent.com/daguanjian/tv-m3u8/main/korea2.m3u8",
]

JSON_SOURCES = [
    "https://raw.githubusercontent.com/kenpark76/kenpark76.github.io/main/koreatv.json",
]

OUTPUT_FILE = "live.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
}

# ---- 不想要的频道，按名称或地址过滤，源里再更新也会被自动排除 ----
EXCLUDE_NAMES = {
    "맛있는 녀석들",
    "나는 자연인이다",
    "도시어부",
    "백반기행",
}

EXCLUDE_URLS = {
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_235_DCEF4BAE.m3u8",
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_262_03C4258B.m3u8",
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_261_3638405F.m3u8",
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_269_96C359FF.m3u8",
}


def is_excluded(name, addr):
    if name and name.strip() in EXCLUDE_NAMES:
        return True
    if addr and addr.strip() in EXCLUDE_URLS:
        return True
    return False


def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print(f"下载失败: {url} - {e}")
        return ""


def add_channel(genres, genre_order, seen, genre, name, addr):
    if not name or not addr:
        return
    if is_excluded(name, addr):
        return
    key = (name, addr)
    if key in seen:
        return
    seen.add(key)
    if genre not in genres:
        genres[genre] = []
        genre_order.append(genre)
    genres[genre].append((name, addr))


def parse_txt(content, genres, genre_order, seen):
    current_genre = "默认分类"
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith("#genre#"):
            current_genre = line.split(",")[0].strip()
            continue
        if "," not in line:
            continue  # 跳过 parse=1、ua=xxx 等配置行
        name, addr = line.split(",", 1)
        add_channel(genres, genre_order, seen, current_genre, name.strip(), addr.strip())


def parse_m3u(content, genres, genre_order, seen, default_genre="国际频道"):
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            name = line.split(",", 1)[-1].strip() if "," in line else "未命名"
            m = re.search(r'group-title="([^"]*)"', line)
            genre = m.group(1) if m and m.group(1) else default_genre
            # 跳过 #EXTVLCOPT 等其它 # 开头的附加行，找到真正的播放地址
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
                j += 1
            if j < len(lines):
                addr = lines[j].strip()
                add_channel(genres, genre_order, seen, genre, name, addr)
                i = j + 1
                continue
        i += 1


def parse_json(content, genres, genre_order, seen):
    try:
        data = json.loads(content)
    except Exception as e:
        print(f"JSON 解析失败: {e}")
        return
    for item in data:
        genre = item.get("group") or "默认分类"
        name = item.get("name") or item.get("title") or ""
        uris = item.get("uris") or []
        if uris:
            add_channel(genres, genre_order, seen, genre, name, uris[0])


def merge():
    genres = {}
    genre_order = []
    seen = set()

    for url in TXT_SOURCES:
        content = fetch(url)
        print(f"TXT 源 {url} 长度: {len(content)}")
        parse_txt(content, genres, genre_order, seen)

    for url in M3U_SOURCES:
        content = fetch(url)
        print(f"M3U 源 {url} 长度: {len(content)}")
        parse_m3u(content, genres, genre_order, seen)

    for url in JSON_SOURCES:
        content = fetch(url)
        print(f"JSON 源 {url} 长度: {len(content)}")
        parse_json(content, genres, genre_order, seen)

    lines_out = []
    for genre in genre_order:
        lines_out.append(f"{genre},#genre#")
        for name, addr in genres[genre]:
            lines_out.append(f"{name},{addr}")
        lines_out.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_out).rstrip() + "\n")

    total = sum(len(v) for v in genres.values())
    print(f"合并完成，共 {total} 个频道，{len(genre_order)} 个分类")


if __name__ == "__main__":
    merge()
