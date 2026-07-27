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
    # 韩国综艺（旧源）
    "맛있는 녀석들",
    "나는 자연인이다",
    "도시어부",
    "백반기행",
    # korea2.m3u8 源里的全部频道（该源已停止同步，此处防止未来其它源重复带入）
    "CCTV1综合",
    "CCTV3综艺",
    "CCTV4中文国际",
    "CCTV5体育",
    "CCTV5+体育赛事",
    "CCTV11戏曲",
    "CCTV12社会与法",
    "CCTV13新闻",
    "CCTV14少儿",
    "CCTV16奥林匹克",
    "湖南卫视",
    "浙江卫视",
    "江苏卫视",
    "深圳卫视",
    "湖北卫视",
    "山东卫视",
    "辽宁卫视",
    "东南卫视",
    "重庆卫视",
    "吉林卫视",
    "江西卫视",
    "兵团卫视",
    "广东珠江",
    "广东影视",
    "长沙县新闻综合",
    "衡山综合",
    "龙山综合",
    "平江综合",
    "津市综合",
    "花垣综合",
    "临武综合",
    "桂东融媒",
    "衡阳县电视台",
    "新化电视台",
    "桂阳新闻综合",
    "屈原融媒体",
    "新邵新闻综合",
    "耒阳电视台",
    "永兴电视台",
    "沅江电视台",
    "蓝山电视台",
    "芷江综合",
    "靖州综合",
    "双峰电视台",
    "嘉禾新闻综合",
    "城步电视台",
    "衡东电视台",
    "汝城台",
    "中方台",
    "吉首综合",
    "安化综合",
    "古丈1",
    "浙江少儿",
    "浙江钱江都市",
    "浙江经济生活",
    "浙江民生休闲",
    "浙江新闻",
    "浙江教科影视",
    "浙江国际",
    "嵊州综合",
    "象山综合",
    "新昌综合",
    "平湖新闻综合",
    "平湖民生休闲",
    "青田电视台",
    "余姚新闻综合",
    "萧山综合",
    "萧山生活",
    "上虞新闻综合",
    "上虞文化影视",
    "普陀电视台",
    "庆元电视台",
    "东阳影视生活",
    "兰溪新闻综合",
    "缙云新闻综合",
    "龙泉电视台",
    "南京新闻综合",
    "南京教科",
    "南京文旅纪录",
    "南京十八生活",
    "南京少儿",
    "海门新闻综合",
    "海门教育人文",
    "海门经济生活",
    "大丰二套",
    "如东1",
    "无锡新闻综合",
    "无锡都市资讯",
    "无锡生活",
    "无锡娱乐",
    "无锡经济",
    "涟水综合",
    "哈尔滨新闻综合",
    "哈尔滨生活",
    "哈尔滨资讯",
    "哈尔滨娱乐",
    "哈尔滨影视",
    "伊春综合",
    "漠河综合",
    "大庆新闻综合",
    "东宁综合",
    "黑河新闻综合",
    "鹤岗综合",
    "富锦综合",
    "尚志电视台",
    "佳木斯新闻综合",
    "齐齐哈尔新闻综合",
    "七台河新闻综合",
    "勃利综合",
    "绥化新闻综合",
    "安达综合",
    "海伦市综合",
    "大兴安岭新闻综合",
    "崇仁电视台",
    "宁都综合",
    "万载电视台1",
    "广丰电视台",
    "陕西新闻资讯",
    "陕西都市青春",
    "陕西银龄",
    "陕西秦腔",
    "陕西体育休闲",
    "农林卫视",
    "陕西西部电影",
    "保定1",
    "保定2",
    "保定3",
    "邯郸新闻",
    "邯郸公共",
    "邯郸科教",
    "兴隆综合",
    "兴隆影视",
    "迁西综合",
    "迁西农业",
    "青县综合",
    "海峡卫视",
    "济源综合",
    "兰考综合",
    "伊川综合",
    "长垣综合",
    "开封新闻",
    "开封文化旅游",
    "内黄综合",
    "新县电视台",
    "淇县电视台",
    "汤阴综合",
    "新乡县综合",
    "舞钢综合",
    "灵宝新闻综合",
    "淮滨综合",
    "光山综合",
    "滑县TV1",
    "滑县TV2",
    "清丰电视台",
    "通许综合",
    "沈丘新闻综合",
    "桐柏新闻综合",
    "夏邑综合",
    "平兴新闻综合",
    "偃师新闻",
    "上街电视台",
    "沁阳新闻综合",
    "项城电视台",
    "汝阳新闻综合",
    "新安新闻综合",
    "罗山电视台",
    "潢川电视台",
    "上蔡1",
    "荥阳1",
    "温县融媒",
    "建安新闻",
    "封丘新闻综合",
    "林州电视台",
    "鄢陵综合",
    "邓州新闻",
    "社旗电视台",
    "镇平新闻综合",
    "孟州1",
    "郏县综合",
    "浚县电视台",
    "舞阳新闻综合",
    "渑池新闻综合",
    "武陟新闻综合",
    "新郑1",
    "辉县新闻综合",
    "永城新闻",
    "禹州综合",
    "杞县新闻综合",
    "林颖综合",
    "宝丰1",
    "新密新闻频道",
    "嘉峪关综合",
    "嘉峪关公共",
    "金昌综合",
    "张掖新闻",
    "定西综合",
    "定西文旅生活",
    "天祝电视台",
    "泰安综合",
    "静宁新闻综合",
    "景泰电视台",
    "西和综合",
    "古浪综合",
    "永昌电视台",
    "陇西电视台",
    "平川电视台",
    "岷县电视台",
    "庄浪电视台",
    "金川电视台",
    "安定电视台",
    "靖远电视台",
    "通渭电视台",
    "秦安电视台",
    "CCTV1超清",
    "CCTV6超清",
    "CCTV8超清",
    "CCTV11超清",
    "CCTV12超清",
    "CCTV13超清",
    "CCTV14超清",
    "湖南卫视超清",
    "浙江卫视超清",
    "江苏卫视超清",
    "湖北卫视超清",
    "山东卫视超清",
    "辽宁卫视超清",
    "重庆卫视超清",
    "东南卫视超清",
    "江西卫视超清",
    "湖南卫视4K",
    "浙江卫视4K",
}

EXCLUDE_URLS = {
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_235_DCEF4BAE.m3u8",
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_262_03C4258B.m3u8",
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_261_3638405F.m3u8",
    "https://tistory1.daumcdn.net/tistory/2864485/skin/images/CATV_269_96C359FF.m3u8",
}

# ---- 手动补充的频道：源里经常缺失/不稳定，这里保证每次合并都一定会写入 ----
MANUAL_CHANNELS = [
    # (分类, 频道名, 播放地址)
    ("韩国频道", "KBS1", "http://124.222.153.240/kakaotv/get_channel.php?channel=kbs1"),
    ("韩国频道", "KBS2", "http://124.222.153.240/kakaotv/get_channel.php?channel=kbs2"),
]


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


def parse_m3u(content, genres, genre_order, seen, default_genre="韩国频道"):
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


def prioritize_channels(genres, genre, priority_names):
    """把 priority_names 里的频道按顺序排到该分类列表最前面，其余频道保持原有顺序不变。"""
    if genre not in genres:
        return
    channels = genres[genre]
    priority_map = {name: idx for idx, name in enumerate(priority_names)}
    priority = [None] * len(priority_names)
    rest = []
    for name, addr in channels:
        if name in priority_map:
            priority[priority_map[name]] = (name, addr)
        else:
            rest.append((name, addr))
    priority = [item for item in priority if item is not None]
    genres[genre] = priority + rest


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

    for genre, name, addr in MANUAL_CHANNELS:
        add_channel(genres, genre_order, seen, genre, name, addr)

    prioritize_channels(genres, "韩国频道", ["KBS1", "KBS2"])

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
