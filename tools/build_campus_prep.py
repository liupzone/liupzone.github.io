#!/usr/bin/env python3
"""Build static article pages from the final campus-prep Markdown chapters."""

from html import escape
import json
from pathlib import Path
import re

import markdown


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path('/home/lpzone/content_creator/campus_content/docs/大厂校招备考攻略PDF')
AGGREGATE_SOURCE = Path('/home/lpzone/content_creator/campus_content/资料库/大厂备考攻略/大厂校招备考攻略PDF/合集-全文.md')
OUTPUT_DIR = ROOT / 'campus-prep'
SITE_URL = 'https://www.liupzone.cn'
SLUGS = {
    '01-腾讯-final.md': 'tencent',
    '02-阿里巴巴-final.md': 'alibaba',
    '03-字节跳动-final.md': 'bytedance',
    '04-百度-final.md': 'baidu',
    '05-美团-final.md': 'meituan',
    '06-京东-final.md': 'jd',
    '07-华为-final.md': 'huawei',
    '14-快手-final.md': 'kuaishou',
    '31-大疆创新-final.md': 'dji',
    '小米校招备考攻略': 'xiaomi',
    'vivo 校招备考攻略': 'vivo',
    'OPPO 校招备考攻略': 'oppo',
    '微软中国校招备考攻略': 'microsoft',
    '谷歌（Google）校招备考攻略': 'google',
    '蚂蚁集团校招备考攻略': 'ant',
    '哔哩哔哩校招备考攻略': 'bilibili',
    '小红书校招备考攻略': 'xiaohongshu',
    '滴滴校招备考攻略': 'didi',
    '携程校招备考攻略': 'ctrip',
    '拼多多校招备考攻略': 'pinduoduo',
    '科大讯飞校招备考攻略': 'iflytek',
    '米哈游校招备考攻略': 'mihoyo',
    '地平线校招备考攻略': 'horizon',
    'Momenta校招备考攻略': 'momenta',
    '小鹏汽车校招备考攻略（智能驾驶方向）': 'xpeng',
    '理想汽车校招备考攻略': 'lixiang',
    '华为智能驾驶校招备考攻略': 'huawei-intelligent-driving',
    '文远知行校招备考攻略': 'weride',
    '宇树科技校招备考攻略': 'unitree',
    '优必选科技校招备考攻略': 'ubtech',
    '追觅科技校招备考攻略': 'dreame',
}

AGGREGATE_SLUGS = {slug for source_name, slug in SLUGS.items() if not source_name.endswith('.md')}
AGGREGATE_HEADINGS = {source_name for source_name in SLUGS if not source_name.endswith('.md')}

COVER_SPECS = {
    'xiaomi': ('Xiaomi', '小米', '手机', 'IoT', '汽车', '#ff6900', '#2a1c17', '#3e2a22'),
    'vivo': ('vivo', 'vivo', '手机', '影像', 'OriginOS', '#4b78ff', '#151b2b', '#30436f'),
    'oppo': ('OPPO', 'OPPO', '手机', '影像', 'ColorOS', '#5cc8a3', '#13231f', '#2f6656'),
    'microsoft': ('Microsoft', '微软中国', 'Azure', 'Windows', 'AI', '#55a7ff', '#13202e', '#365a78'),
    'google': ('Google', '谷歌', 'Search', 'Cloud', 'AI', '#fbbc05', '#202126', '#665425'),
    'ant': ('Ant Group', '蚂蚁集团', '支付', '金融科技', '分布式', '#24b47e', '#10241e', '#347b60'),
    'bilibili': ('bilibili', '哔哩哔哩', '直播', '弹幕', '内容社区', '#00aeec', '#10212a', '#28627b'),
    'xiaohongshu': ('REDnote', '小红书', '社区', '推荐', '内容理解', '#ff4d67', '#28171d', '#74404c'),
    'didi': ('DiDi', '滴滴', '出行', '地图', '调度', '#ff7a28', '#281b16', '#70452f'),
    'ctrip': ('Trip.com', '携程', '旅行', '酒店', '全球化', '#2f8cff', '#142039', '#355d93'),
    'pinduoduo': ('PDD', '拼多多', '电商', '推荐', 'C++', '#e63b2e', '#291716', '#754039'),
    'iflytek': ('iFLYTEK', '科大讯飞', '语音', '大模型', 'AI', '#6d8cff', '#171a32', '#4a558c'),
    'mihoyo': ('miHoYo', '米哈游', '游戏', '引擎', 'C++', '#b084ff', '#21192e', '#634a89'),
    'horizon': ('Horizon', '地平线', 'BPU', '芯片', '量化', '#66c4a0', '#12241f', '#39715d'),
    'momenta': ('Momenta', 'Momenta', '数据飞轮', '自动驾驶', '共享内存', '#f0a45b', '#2a1d17', '#755330'),
    'xpeng': ('XPENG', '小鹏汽车', 'XNGP', 'BEV', '智能驾驶', '#4e9dff', '#142033', '#376693'),
    'lixiang': ('Li Auto', '理想汽车', 'AD Max', '智能座舱', '量产工程', '#f07c6d', '#281b20', '#75443f'),
    'huawei-intelligent-driving': ('HUAWEI ADS', '华为智能驾驶', 'MDC', '传感器融合', 'Autosar', '#e85b68', '#27191f', '#74404b'),
    'weride': ('WeRide', '文远知行', 'Robotaxi', 'SLAM', 'ROS2', '#63b6c9', '#13242a', '#376976'),
    'unitree': ('Unitree', '宇树科技', '四足机器人', '强化学习', 'FOC', '#9cce62', '#1b2817', '#56763d'),
    'ubtech': ('UBTECH', '优必选科技', '人形机器人', '具身智能', 'WBC', '#e9b65d', '#2b2116', '#806238'),
    'dreame': ('Dreame', '追觅科技', '清洁机器人', 'SLAM', 'RTOS', '#87a9c8', '#18222b', '#4a647b'),
}


def flatten_tokens(tokens):
    for token in tokens:
        yield token
        yield from flatten_tokens(token.get('children', []))


def load_aggregate_sections():
    """Extract company chapters from the consolidated guide by exact H1 title."""
    source = AGGREGATE_SOURCE.read_text(encoding='utf-8')
    headings = list(re.finditer(r'^#\s+(.+?)\s*$', source, flags=re.MULTILINE))
    sections = {}
    for index, match in enumerate(headings):
        title = match.group(1).strip()
        if title in AGGREGATE_HEADINGS:
            end = headings[index + 1].start() if index + 1 < len(headings) else len(source)
            sections[title] = source[match.start():end].strip()
    missing = AGGREGATE_HEADINGS.difference(sections)
    if missing:
        raise ValueError(f'Aggregate guide chapters missing: {sorted(missing)}')
    return sections


def sanitize_aggregate_source(source: str) -> str:
    """Convert a consolidated chapter into evergreen, publication-ready Markdown."""
    source = re.sub(r'^#\s+(?:19|20)\d{2}\s*', '# ', source, count=1, flags=re.MULTILINE)
    source = re.sub(r'^#\s+常见追问：', '## 常见追问：', source, flags=re.MULTILINE)
    source = re.sub(r'^#\s+答：', '## 答：', source, flags=re.MULTILINE)
    source = re.sub(r'^> (.*?)(?:更新时间|更新于)[：:].*$', r'> \1版本：final', source, flags=re.MULTILINE)
    source = re.sub(r'^\*\*数据来源\*\*：([^\n]*?)(?:更新时间|更新于)[：:].*$', r'**数据来源**：\1', source, flags=re.MULTILINE)
    source = re.sub(r'^\*\*[^\n]*?(?:校招)?时间线[^\n]*\*\*.*$', '**校招节奏（参考）**：', source, flags=re.MULTILINE | re.IGNORECASE)
    source = re.sub(r'^###\s+(?:19|20)?\d{0,2}\s*届?[^\n]*时间线[^\n]*$', '### 校招节奏怎么理解？', source, flags=re.MULTILINE | re.IGNORECASE)
    source = re.sub(r'^##\s+(?:19|20)?\d{0,2}\s*届?[^\n]*时间线[^\n]*$', '## 校招节奏', source, flags=re.MULTILINE | re.IGNORECASE)
    source = re.sub(r'\n```(?:text)?\n(?:[^`\n]*?(?:19|20)\d{2}[^`\n]*\n)+```', '\n', source)
    source = re.sub(r'(?:19|20)\d{2}\s*年?', '', source)
    source = re.sub(r'\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?', '', source)
    source = re.sub(r'\d{1,2}\s*月(?:\s*[-~至]\s*\d{1,2}\s*月)?', '', source)
    source = re.sub(r'Day\s*\d+(?:\s*[-~]\s*\d+)?', '', source, flags=re.IGNORECASE)
    source = re.sub(r'第\s*\d+\s*天', '', source)
    source = re.sub(r'\d+(?:\.\d+)?\s*(?:小时|分钟|天|周|月)', '', source)
    source = re.sub(r'\d+\s*[hH]', '', source)
    source = re.sub(r'更新时间[：:].*$', '', source, flags=re.MULTILINE)
    source = source.replace('30天', '备考').replace('30 天', '备考')
    source = source.replace('时间线', '校招节奏')
    source = re.sub(r'^\s*<div style="page-break-after: always;"></div>\s*$', '', source, flags=re.MULTILINE)
    source = re.sub(r'^\s*\*更多大厂备考攻略详见本合集后续章节\*\s*$', '', source, flags=re.MULTILINE)
    source = normalize_table_separators(source)
    source = re.sub(r'^\s*\n{3,}', '\n\n', source)
    return source.strip()


def normalize_table_separators(source: str) -> str:
    """Make each Markdown table delimiter match the preceding header width."""
    lines = source.splitlines()
    for index in range(len(lines) - 1):
        if not lines[index].lstrip().startswith('|'):
            continue
        if not re.match(r'^\s*\|?\s*:?-{2,}', lines[index + 1]):
            continue
        header_cells = lines[index].strip().strip('|').split('|')
        if len(header_cells) < 2:
            continue
        lines[index + 1] = '|' + '|'.join('---' for _ in header_cells) + '|'
    return '\n'.join(lines)


def write_generated_cover(slug):
    """Write a compact company-specific SVG cover for chapters from the aggregate guide."""
    if slug not in COVER_SPECS:
        return
    logo, name, item_one, item_two, item_three, accent, paper, border = COVER_SPECS[slug]
    cover = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 480" role="img" aria-labelledby="title desc">
  <title id="title">{name}校招备考攻略</title>
  <desc id="desc">横向公司专项校招备考攻略封面，包含 {logo} 标识与 {item_one}、{item_two}、{item_three} 业务元素</desc>
  <rect width="1200" height="480" fill="#10131a"/><path d="M0 392H1200M0 424H1200M0 456H1200" stroke="#252b35" stroke-width="2"/><path d="M772 0v480M1048 0v480" stroke="#202630" stroke-width="2"/>
  <rect x="54" y="52" width="1092" height="376" rx="22" fill="{paper}" stroke="{border}" stroke-width="2"/>
  <path d="M92 338C172 311 231 327 302 268s128-20 198 28 133 24 210-50 142-55 230-4" fill="none" stroke="{accent}" stroke-width="4"/><path d="M92 338C172 311 231 327 302 268s128-20 198 28 133 24 210-50 142-55 230-4" fill="none" stroke="{accent}" stroke-width="15" opacity=".18"/>
  <circle cx="302" cy="268" r="8" fill="#fff" stroke="{accent}" stroke-width="4"/><circle cx="500" cy="296" r="8" fill="#fff" stroke="{accent}" stroke-width="4"/><circle cx="940" cy="234" r="8" fill="#fff" stroke="{accent}" stroke-width="4"/>
  <text x="92" y="105" fill="{accent}" font-size="15" font-weight="700" letter-spacing="3" font-family="Arial, sans-serif">LIUPZONE / CAMPUS PREP</text>
  <text x="92" y="182" fill="#f5f7fb" font-size="50" font-weight="700" font-family="PingFang SC, Microsoft YaHei, sans-serif">{name}校招备考攻略</text>
  <text x="95" y="220" fill="#c4cad5" font-size="21" font-family="PingFang SC, Microsoft YaHei, sans-serif">{item_one} · {item_two} · {item_three} · 工程实战</text>
  <text x="95" y="386" fill="#89929f" font-size="14" letter-spacing="2" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">FINAL ARTICLE / COMPANY GUIDE</text>
  <g transform="translate(808 88)"><rect width="280" height="250" rx="18" fill="#0e1218" stroke="{border}" stroke-width="2"/><g transform="translate(20 14)"><rect x="2" y="3" width="38" height="32" rx="7" fill="{accent}"/><text x="8" y="26" fill="#10131a" font-size="14" font-weight="700" font-family="Arial, sans-serif">{logo[:8]}</text><text x="58" y="19" fill="#f5f7fb" font-size="17" font-weight="700" font-family="Arial, sans-serif">{logo}</text><text x="58" y="37" fill="{accent}" font-size="12" font-family="PingFang SC, Microsoft YaHei, sans-serif">{name}</text></g><text x="22" y="64" fill="{accent}" font-size="13" letter-spacing="2" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">COMPANY GUIDE</text><g transform="translate(28 88)" font-family="PingFang SC, Microsoft YaHei, sans-serif"><rect x="0" y="0" width="54" height="35" rx="8" fill="{accent}"/><text x="8" y="24" fill="#10131a" font-size="14" font-weight="700">{item_one}</text><text x="75" y="23" fill="#dce1e8" font-size="16">{item_two}</text><rect x="0" y="56" width="54" height="35" rx="8" fill="#f5f7fb"/><text x="8" y="80" fill="#10131a" font-size="14" font-weight="700">{item_two}</text><text x="75" y="79" fill="#dce1e8" font-size="16">{item_three}</text><rect x="0" y="112" width="54" height="35" rx="8" fill="{accent}" opacity=".8"/><text x="8" y="136" fill="#10131a" font-size="14" font-weight="700">{item_three}</text><text x="75" y="135" fill="#dce1e8" font-size="16">岗位 · 技术</text></g></g>
</svg>\n'''
    (ROOT / 'assets' / f'{slug}-campus-prep-cover.svg').write_text(cover, encoding='utf-8')


def sanitize_tencent_source(source: str) -> str:
    """Remove calendar-specific dates while keeping the evergreen interview advice."""
    source = source.replace('2026腾讯校招备考全攻略：高频题、面试风格、30天计划', '腾讯校招备考全攻略：高频题、面试风格、备考计划')
    source = source.replace('数据来源：真实面经整理 | 更新时间：2026年3月', '数据来源：真实面经整理 | 版本：final')
    source = source.replace('这篇文章把腾讯校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、30天备考计划。', '这篇文章把腾讯校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、备考计划。')
    source = re.sub(r'\*\*2026届校招时间线（参考）\*\*：\n\n```[\s\S]*?```', '**校招节奏（参考）**：\n\n- 预热与网申：关注官方招聘入口和内推信息\n- 笔试阶段：熟悉平台规则，保持稳定的解题状态\n- 面试阶段：准备技术面、项目面与 HR 面\n- Offer 阶段：结合岗位方向、团队和发展路径做选择', source)
    source = source.replace('腾讯技术面通常 2-3 轮，每轮 60-90 分钟。', '腾讯技术面通常有多轮，每轮会在手写代码后继续深挖基础知识。')
    source = source.replace('**考试时长**：约 2 小时', '**考试安排**：以官方通知和具体岗位要求为准')
    source = source.replace('先花 10 分钟看清楚题意，想好思路再动手', '先看清楚题意，想好思路再动手')
    source = source.replace('## 30 天备考计划', '## 备考计划')
    source = source.replace('适合已有 LeetCode 200+ 刷题量的同学，冲刺备考腾讯。', '适合已经有一定 LeetCode 刷题基础、准备冲刺腾讯的同学。')
    source = source.replace('| 阶段 | 时间 | 重点任务 |', '| 阶段 | 准备重点 |')
    source = source.replace(
        '| 阶段 | 准备重点 |\n|------|------|---------|',
        '| 阶段 | 准备重点 |\n|------|---------|',
    )
    plan_rows = {
        '| **链表专项** | Day 1-5 |': '| **链表专项** |',
        '| **排序专项** | Day 6-9 |': '| **排序专项** |',
        '| **树专项** | Day 10-13 |': '| **树专项** |',
        '| **动态规划** | Day 14-19 |': '| **动态规划** |',
        '| **字符串+双指针** | Day 20-22 |': '| **字符串+双指针** |',
        '| **系统知识** | Day 23-27 |': '| **系统知识** |',
        '| **冲刺收尾** | Day 28-30 |': '| **冲刺收尾** |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('**每天时间分配建议**：', '**每天准备建议**：')
    source = source.replace('- 上午 2h：刷题（2-3 道 Medium，1 道 Hard）', '- 刷题时段：保持 Medium 题为主，穿插 Hard 题')
    source = source.replace('- 下午 1h：复习系统知识（OS 和网络轮流）', '- 基础复习时段：OS 和网络交替复习')
    source = source.replace('- 晚上 1h：看面经 + 写总结笔记', '- 复盘时段：看面经并写总结笔记')
    source = source.replace('百度2026校招避坑指南', '百度校招避坑指南')
    source = re.sub(r'覆盖2024-2026年腾讯校招面经，更新时间：2026年3月', '覆盖历年腾讯校招面经', source)
    return source


def sanitize_alibaba_source(source: str) -> str:
    """Remove calendar-specific dates while keeping evergreen Alibaba advice."""
    source = source.replace('2026阿里校招全攻略：高频题、考点，一篇搞定', '阿里巴巴校招全攻略：高频题、考点，一篇搞定')
    source = source.replace('数据来源：真实面经整理 | 更新时间：2026年3月', '数据来源：真实面经整理 | 版本：final')
    source = source.replace('这篇文章把阿里校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、30天备考计划。', '这篇文章把阿里校招的核心信息全拆给你看：岗位要求、高频题Top20、技术考点、面试风格、备考计划。')
    source = re.sub(r'\*\*2026届校招时间线（参考）\*\*：\n\n```[\s\S]*?```', '**校招节奏（参考）**：\n\n- 预热与网申：关注官方招聘入口和内推信息\n- 笔试阶段：熟悉平台规则，准备编程题与能力测评\n- 面试阶段：准备技术面、项目面与 HR 面\n- Offer 阶段：结合岗位方向、团队和发展路径做选择', source)
    source = source.replace('阿里成立于1999年，总部杭州，2024财年营收超9400亿元，全球员工超20万人。', '阿里总部位于杭州，业务覆盖电商、云计算、物流、企业协作与本地生活等多个方向。')
    source = source.replace('## 30天备考计划', '## 备考计划')
    source = source.replace('适合Java方向后端或算法岗同学冲刺备考阿里。', '适合 Java 方向后端或算法岗同学准备阿里校招。')
    source = source.replace('| 阶段 | 时间 | 重点任务 |', '| 阶段 | 准备重点 |')
    source = source.replace(
        '| 阶段 | 准备重点 |\n|------|------|---------|',
        '| 阶段 | 准备重点 |\n|------|---------|',
    )
    plan_rows = {
        '| **链表+DP专项** | Day 1-6 |': '| **链表+DP专项** |',
        '| **Java八股** | Day 7-12 |': '| **Java八股** |',
        '| **分布式专项** | Day 13-18 |': '| **分布式专项** |',
        '| **系统设计** | Day 19-22 |': '| **系统设计** |',
        '| **数据库+算法** | Day 23-26 |': '| **数据库+算法** |',
        '| **冲刺收尾** | Day 27-30 |': '| **冲刺收尾** |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('能讲20分钟不重样', '能完整讲清楚且经得起追问')
    source = source.replace('能讲20分钟', '能完整讲清楚')
    source = source.replace('百度2026校招避坑指南', '百度校招避坑指南')
    source = re.sub(r'覆盖2024-2026年阿里校招面经，更新时间：2026年3月', '覆盖历年阿里校招面经', source)
    return source


def sanitize_bytedance_source(source: str) -> str:
    """Remove calendar-specific dates and clock durations from the ByteDance guide."""
    source = source.replace(
        '2026字节跳动校招备考全攻略：高频题、考点，看这篇就够了',
        '字节跳动校招备考全攻略：高频题、考点，看这篇就够了',
    )
    source = source.replace('数据来源：真实面经整理 | 更新时间：2026年3月', '数据来源：真实面经整理 | 版本：final')
    source = source.replace(
        '这篇文章把字节校招的核心信息全拆给你：岗位要求、高频题 Top 20、技术考点、面试风格、30 天备考计划。',
        '这篇文章把字节校招的核心信息全拆给你：岗位要求、高频题 Top 20、技术考点、面试风格、备考计划。',
    )
    source = re.sub(
        r'\*\*2026届校招时间线（参考）\*\*：\n\n```[\s\S]*?```',
        '**校招节奏（参考）**：\n\n- 预热与网申：关注官方招聘入口和内推信息\n- 笔试阶段：熟悉平台规则，保持稳定的解题状态\n- 面试阶段：准备算法题、基础知识与系统设计\n- Offer 阶段：结合岗位方向、团队和发展路径做选择',
        source,
    )
    source = source.replace(
        '笔试 → 面试 → Offer，全流程可能在 2-3 周内完成。这是好事，也意味着你没时间"边投边准备"。',
        '笔试 → 面试 → Offer，全流程节奏很快。这是好事，也意味着不能等到投递后才开始准备。',
    )
    source = source.replace('字节算法岗要求 20 分钟内解 Hard 题。是的，Hard，20 分钟。', '字节算法岗要求在限时内解 Hard 题，算法深度和稳定性都要过关。')
    source = source.replace('20 分钟内写完是基本要求', '快速写完是基本要求')
    source = source.replace('字节面试限时 45 分钟，解题速度不够会直接卡死', '字节面试节奏紧凑，解题速度不够会直接卡死')
    source = source.replace('字节技术面通常 2-3 轮，每轮约 45-60 分钟。算法题结束后，会深挖基础知识。', '字节技术面通常有多轮，算法题结束后会继续深挖基础知识。')
    source = source.replace('每一道要能讲 20 分钟，带高并发方案。', '每一道要能完整讲清楚，并给出高并发方案。')
    source = source.replace('**限时 45 分钟**：解题 + 讲思路 + 讨论优化，全在里面', '**节奏紧凑**：解题、讲思路与讨论优化需要连贯完成')
    source = source.replace('- **编程题为主**：3-5 道算法题，时间约 90-120 分钟', '- **编程题为主**：3-5 道算法题，题量和节奏都较紧')
    source = source.replace('## 30 天备考计划', '## 备考计划')
    source = source.replace('| 阶段 | 时间 | 重点任务 |', '| 阶段 | 准备重点 |')
    source = source.replace('|------|------|---------|', '|------|---------|')
    source = source.replace('|---|------|------|---------|', '|---|------|------|------|---------|')
    plan_rows = {
        '| **链表 Hard 专项** | Day 1-5 |': '| **链表 Hard 专项** |',
        '| **二叉树全系列** | Day 6-10 |': '| **二叉树全系列** |',
        '| **Hard 题专项** | Day 11-15 |': '| **Hard 题专项** |',
        '| **动态规划+股票** | Day 16-20 |': '| **动态规划+股票** |',
        '| **系统知识** | Day 21-24 |': '| **系统知识** |',
        '| **系统设计+冲刺** | Day 25-30 |': '| **系统设计+冲刺** |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('**每日时间分配**：', '**每日准备建议**：')
    source = source.replace('- 上午 2.5h：2-3 道 Medium + 1 道 Hard', '- 刷题时段：2-3 道 Medium，穿插 Hard 题')
    source = source.replace('- 下午 1.5h：系统知识 + 语言专项', '- 基础复习时段：系统知识与语言专项交替复习')
    source = source.replace('- 晚上 1h：看字节面经 + 整理错题本', '- 复盘时段：看字节面经并整理错题本')
    source = source.replace('10 分钟内写完，零 bug', '快速写完，零 bug')
    source = source.replace('在 45 分钟内解 Hard 题', '限时解 Hard 题')
    source = source.replace('百度2026校招避坑指南', '百度校招避坑指南')
    source = re.sub(r'覆盖2024-2026年字节跳动校招面经，更新时间：2026年3月', '覆盖历年字节跳动校招面经', source)
    return source


def sanitize_baidu_source(source: str) -> str:
    """Remove calendar-specific dates and seasonal timing from the Baidu guide."""
    source = source.replace('2026百度校招全攻略：高频题、考点、一篇搞定', '百度校招全攻略：高频题、考点、一篇搞定')
    source = source.replace(
        '数据来源：真实面经整理 + 百度官方招聘信息 | 更新时间：2026年3月',
        '数据来源：真实面经整理 + 百度官方招聘信息 | 版本：final',
    )
    source = source.replace(
        '以及一份 30 天备考路线。',
        '以及一份备考路线。',
    )
    source = source.replace('2026 届', '本届').replace('2026届', '本届')
    source = re.sub(r'\n---\n```\n金三银四招聘季\n大量内推来袭\nxxx\n```\n---\n', '\n', source)
    source = re.sub(
        r'\*\*本届校招时间线（以官网信息为准）\*\*：\n\n```[\s\S]*?```',
        '**校招节奏（以官网信息为准）**：\n\n- 关注官方招聘入口、内推和岗位变化\n- 网申与笔试阶段：熟悉平台规则，保持稳定的解题状态\n- 面试阶段：准备算法题、基础知识与项目表达\n- Offer 阶段：结合岗位方向、团队和发展路径做选择',
        source,
    )
    source = source.replace('## 30 天备考时间线', '## 备考计划')
    source = source.replace('| 阶段                          | 时间      | 重点任务                                      |', '| 阶段                          | 准备重点                                      |')
    source = source.replace('| ----------------------------- | --------- | --------------------------------------------- |', '| ----------------------------- | --------------------------------------------- |')
    plan_rows = {
        '| **树题专项**            | Day 1-6   |': '| **树题专项**            |',
        '| **链表专项**            | Day 7-10  |': '| **链表专项**            |',
        '| **C++ / 语言深度**      | Day 11-16 |': '| **C++ / 语言深度**      |',
        '| **难题突破**            | Day 17-20 |': '| **难题突破**            |',
        '| **AI / 自动驾驶加分项** | Day 21-24 |': '| **AI / 自动驾驶加分项** |',
        '| **冲刺阶段**            | Day 25-30 |': '| **冲刺阶段**            |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('前 20 天', '前期')
    source = source.replace('后端开发大厂面经合集 2025-2026', '后端开发大厂面经合集')
    source = re.sub(
        r'\*\*数据来源\*\*：真实面经整理，结合百度官方校园招聘主页、校招项目页及公开岗位信息交叉校验，更新时间：2026年3月。',
        '**数据来源**：真实面经整理，结合百度官方校园招聘主页、校招项目页及公开岗位信息交叉校验。',
        source,
    )
    return source


def sanitize_meituan_source(source: str) -> str:
    """Remove calendar dates and fixed day counts from the Meituan guide."""
    source = source.replace('2026美团校招全攻略：链表高频题、并发场景、30天备考计划', '美团校招全攻略：链表高频题、并发场景、备考计划')
    source = source.replace(
        '数据来源：真实面经整理 + 美团校招公开资料交叉校验 | 更新时间：2026年3月',
        '数据来源：真实面经整理 + 美团校招公开资料交叉校验 | 版本：final',
    )
    source = source.replace('以及一份 30 天备考路线。', '以及一份备考路线。')
    source = re.sub(
        r'从公开校招资料看，2026 届美团校招对外释放的是[\s\S]*?毕业人群。',
        '从公开校招资料看，美团校招岗位覆盖广，业务方向和岗位类型都比较丰富。准备时应先明确目标方向，再对照官方岗位要求安排复习。',
        source,
    )
    source = source.replace('## 30 天备考时间线', '## 备考计划')
    source = source.replace('| 阶段 | 时间 | 重点任务 |', '| 阶段 | 准备重点 |')
    source = source.replace('|------|------|---------|', '|------|---------|')
    source = source.replace('|---|------|------|---------|', '|---|------|------|------|---------|')
    plan_rows = {
        '| **链表专项** | Day 1-5 |': '| **链表专项** |',
        '| **数组/排序/字符串** | Day 6-10 |': '| **数组/排序/字符串** |',
        '| **Java / 后端基础** | Day 11-16 |': '| **Java / 后端基础** |',
        '| **高并发场景** | Day 17-20 |': '| **高并发场景** |',
        '| **方向加练** | Day 21-24 |': '| **方向加练** |',
        '| **冲刺阶段** | Day 25-30 |': '| **冲刺阶段** |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('后端开发大厂面经合集 2025-2026', '后端开发大厂面经合集')
    source = re.sub(r'\*\*数据来源\*\*：真实面经整理，结合美团校招公开资料、官方网申入口及公开岗位信息交叉校验，更新时间：2026年3月。', '**数据来源**：真实面经整理，结合美团校招公开资料、官方网申入口及公开岗位信息交叉校验。', source)
    return source


def sanitize_jd_source(source: str) -> str:
    """Remove calendar references and seasonal promotion dates from the JD guide."""
    source = source.replace('2026京东校招全攻略：笔试面试、高频题、看这一篇就够了', '京东校招全攻略：笔试面试、高频题、看这一篇就够了')
    source = source.replace(
        '数据来源：真实面经整理 + 京东校招公开信息交叉校验 | 更新时间：2026年3月',
        '数据来源：真实面经整理 + 京东校招公开信息交叉校验 | 版本：final',
    )
    source = source.replace('以及一份 30 天备考路线。', '以及一份备考路线。')
    source = source.replace('### 2026 届时间线怎么理解？', '### 校招节奏怎么理解？')
    source = source.replace('618 大促', '大促').replace('618、双十一、大促', '大促')
    source = source.replace('618 / 秒杀 / 库存', '大促 / 秒杀 / 库存')
    source = source.replace('618 / 秒杀 / 库存场景', '大促 / 秒杀 / 库存场景')
    source = source.replace('围绕 618 / 秒杀场景', '围绕大促 / 秒杀场景')
    source = source.replace('## 30 天备考时间线', '## 备考计划')
    source = source.replace('| 阶段                         | 时间      | 重点任务                                                        |', '| 阶段                         | 准备重点                                                        |')
    source = source.replace('| ---------------------------- | --------- | --------------------------------------------------------------- |', '| ---------------------------- | --------------------------------------------------------------- |')
    plan_rows = {
        '| **链表 + 窗口专项**    | Day 1-5   |': '| **链表 + 窗口专项**    |',
        '| **Java 基本盘**        | Day 6-12  |': '| **Java 基本盘**        |',
        '| **Redis / MySQL 专项** | Day 13-17 |': '| **Redis / MySQL 专项** |',
        '| **高并发系统设计**     | Day 18-21 |': '| **高并发系统设计**     |',
        '| **方向补强**           | Day 22-25 |': '| **方向补强**           |',
        '| **冲刺阶段**           | Day 26-30 |': '| **冲刺阶段**           |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('后端开发大厂面经合集 2025-2026', '后端开发大厂面经合集')
    source = re.sub(r'\*\*数据来源\*\*：真实面经整理，结合京东校招公开信息、官方网申入口及公开岗位资料交叉校验，更新时间：2026年3月。', '**数据来源**：真实面经整理，结合京东校招公开信息、官方网申入口及公开岗位资料交叉校验。', source)
    return source


def sanitize_huawei_source(source: str) -> str:
    """Remove report years and fixed countdown language from the Huawei guide."""
    source = source.replace(
        '数据来源：华为官方招聘信息、华为 2024 年年报、公开岗位信息与近年公开面经整理 | 更新时间：2026 年 3 月',
        '数据来源：华为官方招聘信息、华为年度报告、公开岗位信息与近年公开面经整理 | 版本：final',
    )
    source = source.replace('如果只剩 30 天，时间怎么排最划算', '如果准备时间有限，时间怎么排最划算')
    source = source.replace('如果只剩 30 天，建议这样排', '如果准备时间有限，建议这样排')
    source = source.replace('华为 2024 年年报', '华为年度报告')
    source = source.replace('华为 2024 年实现', '华为近年实现')
    source = source.replace('华为 2024 年年度报告', '华为年度报告')
    source = source.replace('截至 2024 年底', '根据公开年度数据')
    source = source.replace('在 3-5 分钟内把一个点讲清楚', '在几分钟内把一个点讲清楚')
    source = re.sub(r'^### Day 1-7：先冲机考$', '### 第一阶段：先冲机考', source, flags=re.MULTILINE)
    source = re.sub(r'^### Day 8-14：补 C\+\+ 深度和 OS$', '### 第二阶段：补 C++ 深度和 OS', source, flags=re.MULTILINE)
    source = re.sub(r'^### Day 15-21：网络 \+ 方向专项$', '### 第三阶段：网络 + 方向专项', source, flags=re.MULTILINE)
    source = re.sub(r'^### Day 22-27：面经复盘 \+ 模拟面试$', '### 第四阶段：面经复盘 + 模拟面试', source, flags=re.MULTILINE)
    source = re.sub(r'^### Day 28-30：查漏补缺，别再乱开新坑$', '### 最后阶段：查漏补缺，别再乱开新坑', source, flags=re.MULTILINE)
    source = source.replace('最后 3 天', '最后阶段')
    source = re.sub(r'华为 2024 年年度报告、', '华为年度报告、', source)
    source = re.sub(r'华为 2024 年年报、', '华为年度报告、', source)
    source = re.sub(r'华为 2024 年实现', '华为近年实现', source)
    source = re.sub(r'\*\*数据来源\*\*：华为校园招聘官网与公开岗位信息、华为年度报告、近年公开面经与公开讨论交叉整理。具体岗位与招聘时间以 `career\.huawei\.com` 最新页面为准。', '**数据来源**：华为校园招聘官网与公开岗位信息、华为年度报告、近年公开面经与公开讨论交叉整理。具体岗位与招聘节奏以 `career.huawei.com` 页面为准。', source)
    return source


def sanitize_kuaishou_source(source: str) -> str:
    """Remove calendar references and fixed day counts from the Kuaishou guide."""
    source = source.replace('2026快手校招全攻略：Go 深挖、链表高频题、30天备考计划', '快手校招全攻略：Go 深挖、链表高频题、备考计划')
    source = source.replace(
        '数据来源：真实面经整理 + 快手校招公开信息交叉校验 | 更新时间：2026年3月',
        '数据来源：真实面经整理 + 快手校招公开信息交叉校验 | 版本：final',
    )
    source = source.replace('以及一份 30 天备考路线。', '以及一份备考路线。')
    source = source.replace('### 2026 届时间线怎么理解？', '### 校招节奏怎么理解？')
    source = source.replace('## 30 天备考时间线', '## 备考计划')
    source = source.replace('| 阶段 | 时间 | 重点任务 |', '| 阶段 | 准备重点 |')
    source = source.replace('|------|------|---------|', '|------|---------|')
    source = source.replace('|---|------|------|---------|', '|---|------|------|------|---------|')
    plan_rows = {
        '| **链表专项** | Day 1-6 |': '| **链表专项** |',
        '| **Go 基础** | Day 7-11 |': '| **Go 基础** |',
        '| **Go 深度** | Day 12-15 |': '| **Go 深度** |',
        '| **Redis / MySQL / Kafka** | Day 16-20 |': '| **Redis / MySQL / Kafka** |',
        '| **直播 / 推荐场景** | Day 21-25 |': '| **直播 / 推荐场景** |',
        '| **冲刺阶段** | Day 26-30 |': '| **冲刺阶段** |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('后端开发大厂面经合集 2025-2026', '后端开发大厂面经合集')
    source = re.sub(r'\*\*数据来源\*\*：真实面经整理，结合快手官方网申入口、公开岗位信息与本地题库资料交叉校验，更新时间：2026年3月。', '**数据来源**：真实面经整理，结合快手官方网申入口、公开岗位信息与本地题库资料交叉校验。', source)
    return source


def sanitize_dji_source(source: str) -> str:
    """Remove calendar dates, month ranges, and clock durations from the DJI guide."""
    source = source.replace('2026大疆创新校招备考攻略：嵌入式、C++、算法岗怎么准备', '大疆创新校招备考攻略：嵌入式、C++、算法岗怎么准备')
    source = source.replace(
        '数据来源：真实面经整理 + 公开资料交叉验证 | 更新时间：2026年3月',
        '数据来源：真实面经整理 + 公开资料交叉验证 | 版本：final',
    )
    source = source.replace('30 天备考路线', '备考路线')
    source = source.replace('### 2026届校招时间线怎么理解？', '### 校招节奏怎么理解？')
    source = re.sub(r'截至 2026 年 3 月，公开搜索结果显示，大疆 2026 届“拓疆者”秋季校园招聘仍有扩招批次在进行。', '公开招聘信息显示，大疆“拓疆者”校园招聘会根据岗位和团队滚动推进。', source)
    source = re.sub(
        r'\| 阶段 \| 大致时间 \| 你该做什么 \|\n\|------\|----------\|------------\|\n(?:\|.*\n){4}',
        '| 阶段 | 你该做什么 |\n|------|------------|\n| 提前批与实习转正 | 有实习和竞赛经历的同学优先关注 |\n| 秋招主批 | 尽早投递，不要等准备完再说 |\n| 笔试与面试 | 基础题只是开始，重点准备追问链 |\n| Offer 阶段 | 结合部门方向和发展路径做选择 |\n',
        source,
    )
    source = source.replace('## 30 天备考时间线', '## 备考计划')
    source = source.replace('| 阶段 | 时间 | 重点任务 | 每日时长 |', '| 阶段 | 准备重点 |')
    source = source.replace('|------|------|---------|---------|', '|------|---------|')
    plan_rows = {
        '| C++ 深度强化 | Day 1-8 |': '| C++ 深度强化 |',
        '| 网络与系统 | Day 9-13 |': '| 网络与系统 |',
        '| 算法高频题 | Day 14-20 |': '| 算法高频题 |',
        '| 嵌入式系统 | Day 21-24 |': '| 嵌入式系统 |',
        '| 控制 / 视觉专项 | Day 25-27 |': '| 控制 / 视觉专项 |',
        '| 冲刺收尾 | Day 28-30 |': '| 冲刺收尾 |',
    }
    for old, new in plan_rows.items():
        source = source.replace(old, new)
    source = source.replace('20 分钟内从零写出 LRU', '限时从零写出 LRU')
    source = source.replace('C++客户端大厂面经合集 2025-2026', 'C++客户端大厂面经合集')
    source = source.replace('后端开发大厂面经合集 2025-2026', '后端开发大厂面经合集')
    source = source.replace('算法工程师大厂面经合集 2025-2026', '算法工程师大厂面经合集')
    source = re.sub(r'更新时间：2026 年 3 月。', '版本：final。', source)
    return source


def convert_markdown(source: str):
    # The source uses bold numbered lines as visual labels and immediately
    # follows them with a dash line. Normalize those blocks before Markdown
    # parsing so the article keeps a readable heading/list hierarchy in HTML.
    source = re.sub(
        r'^\*\*(\d+\.\s+.+?)\*\*(.*)$',
        lambda match: f'#### {match.group(1)}{match.group(2)}',
        source,
        flags=re.MULTILINE,
    )
    engine = markdown.Markdown(
        extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'sane_lists'],
        extension_configs={'codehilite': {'guess_lang': False, 'noclasses': True}},
    )
    body = engine.convert(source)
    title_match = re.search(r'^#\s+(.+?)\s*$', source, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else '大厂校招备考攻略'
    body = re.sub(r'^<h1[^>]*>.*?</h1>\s*', '', body, count=1, flags=re.DOTALL)
    meta_match = re.search(r'版本：([^|\n]+)', source)
    updated = meta_match.group(1).strip() if meta_match else 'final'
    toc_items = [token for token in flatten_tokens(engine.toc_tokens) if token.get('level') == 2]
    return title, updated, body, toc_items


def render_page(title, updated, body, toc_items, cover_asset, cover_alt, slug):
    nav = ''.join(f'<a href="#{escape(item["id"])}">{escape(item["name"])}</a>' for item in toc_items)
    canonical = f'{SITE_URL}/campus-prep/{slug}.html'
    description = f'{title}：岗位方向、高频题、技术考点、面试风格与备考路线。'
    article_schema = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': title,
        'description': description,
        'image': [f'{SITE_URL}/assets/{cover_asset}'],
        'author': {'@type': 'Organization', 'name': 'liupzone', 'url': SITE_URL},
        'publisher': {'@type': 'Organization', 'name': 'liupzone', 'url': SITE_URL},
        'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical},
        'articleSection': '校招稳稳拿OFFER',
        'inLanguage': 'zh-CN',
    }
    breadcrumb_schema = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '首页', 'item': f'{SITE_URL}/'},
            {'@type': 'ListItem', 'position': 2, 'name': '大厂校招备考攻略', 'item': f'{SITE_URL}/campus-prep.html'},
            {'@type': 'ListItem', 'position': 3, 'name': title, 'item': canonical},
        ],
    }
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#f5f6fb" />
  <meta name="description" content="{escape(description)}" />
  <meta name="keywords" content="{escape(title)},校招,校招备考,大厂面试,高频题,技术面试,应届生求职" />
  <meta name="author" content="liupzone" />
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
  <meta name="applicable-device" content="pc,mobile" />
  <meta name="mobile-agent" content="format=html5;url={escape(canonical)}" />
  <title>{escape(title)} · 校招稳稳拿OFFER</title>
  <link rel="canonical" href="{escape(canonical)}" />
  <link rel="alternate" hreflang="zh-CN" href="{escape(canonical)}" />
  <link rel="sitemap" type="application/xml" href="{SITE_URL}/sitemap.xml" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="zh_CN" />
  <meta property="og:site_name" content="liupzone 人生路标小站" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(description)}" />
  <meta property="og:url" content="{escape(canonical)}" />
  <meta property="og:image" content="{SITE_URL}/assets/{escape(cover_asset)}" />
  <meta property="og:image:alt" content="{escape(cover_alt)}" />
  <meta property="article:section" content="校招稳稳拿OFFER" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{escape(title)}" />
  <meta name="twitter:description" content="{escape(description)}" />
  <meta name="twitter:image" content="{SITE_URL}/assets/{escape(cover_asset)}" />
  <script type="application/ld+json">{json.dumps(article_schema, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>
  <link rel="stylesheet" href="../campus-prep.css" />
</head>
<body class="light">
  <header class="topbar shell">
    <a class="brand" href="../index.html" aria-label="liupzone 首页"><span class="mark" aria-hidden="true"></span><span><span class="brand-cn">liupzone</span><span class="brand-en">人生路标小站</span></span></a>
    <nav class="nav" aria-label="主导航"><a href="../index.html">首页</a><a class="active" href="../campus-prep.html">校招稳稳拿OFFER</a><a href="../resources.html">精品资源</a><button class="icon-btn" id="themeToggle" aria-label="切换主题" title="切换主题">☾</button></nav>
  </header>
  <main class="article-page shell">
    <a class="article-back" href="../campus-prep.html">← 返回攻略目录</a>
    <header class="article-head"><div class="eyebrow">CAMPUS PREP / FINAL ARTICLE</div><h1>{escape(title)}</h1><img class="article-cover" src="../assets/{escape(cover_asset)}" alt="{escape(cover_alt)}" /><div class="article-meta"><span>版本：{escape(updated)}</span><span>内容类型：公司专项攻略</span><span>仅供学习参考</span></div></header>
    <div class="article-layout"><aside class="article-nav"><h2>本篇导航</h2>{nav}</aside><article class="article-body">{body}</article></div>
  </main>
  <script>
    document.getElementById('themeToggle').addEventListener('click', () => {{ const dark = document.body.classList.toggle('dark'); document.body.classList.toggle('light', !dark); document.getElementById('themeToggle').textContent = dark ? '☼' : '☾'; document.querySelector('meta[name="theme-color"]').setAttribute('content', dark ? '#0b1026' : '#f5f6fb'); }});
  </script>
</body>
</html>
'''


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    aggregate_sections = load_aggregate_sections()
    for source_name, slug in SLUGS.items():
        if source_name in AGGREGATE_HEADINGS:
            source = sanitize_aggregate_source(aggregate_sections[source_name])
            write_generated_cover(slug)
        else:
            source_path = SOURCE_DIR / source_name
            if not source_path.exists():
                raise FileNotFoundError(source_path)
            source = source_path.read_text(encoding='utf-8')
        if slug == 'tencent':
            source = sanitize_tencent_source(source)
            cover_asset = 'tencent-campus-prep-cover.svg'
            cover_alt = '腾讯校招备考攻略封面'
        elif slug == 'alibaba':
            source = sanitize_alibaba_source(source)
            cover_asset = 'alibaba-campus-prep-cover.svg'
            cover_alt = '阿里巴巴校招备考攻略封面'
        elif slug == 'bytedance':
            source = sanitize_bytedance_source(source)
            cover_asset = 'bytedance-campus-prep-cover.svg'
            cover_alt = '字节跳动校招备考攻略封面'
        elif slug == 'baidu':
            source = sanitize_baidu_source(source)
            cover_asset = 'baidu-campus-prep-cover.svg'
            cover_alt = '百度校招备考攻略封面'
        elif slug == 'meituan':
            source = sanitize_meituan_source(source)
            cover_asset = 'meituan-campus-prep-cover.svg'
            cover_alt = '美团校招备考攻略封面'
        elif slug == 'jd':
            source = sanitize_jd_source(source)
            cover_asset = 'jd-campus-prep-cover.svg'
            cover_alt = '京东校招备考攻略封面'
        elif slug == 'huawei':
            source = sanitize_huawei_source(source)
            cover_asset = 'huawei-campus-prep-cover.svg'
            cover_alt = '华为校招备考攻略封面'
        elif slug == 'kuaishou':
            source = sanitize_kuaishou_source(source)
            cover_asset = 'kuaishou-campus-prep-cover.svg'
            cover_alt = '快手校招备考攻略封面'
        elif slug == 'dji':
            source = sanitize_dji_source(source)
            cover_asset = 'dji-campus-prep-cover.svg'
            cover_alt = '大疆创新校招备考攻略封面'
        elif slug in AGGREGATE_SLUGS:
            cover_asset = f'{slug}-campus-prep-cover.svg'
            cover_alt = f'{aggregate_sections[source_name].splitlines()[0].lstrip("# ").strip()}封面'
        else:
            raise ValueError(f'Unknown campus prep slug: {slug}')
        title, updated, body, toc_items = convert_markdown(source)
        (OUTPUT_DIR / f'{slug}.html').write_text(render_page(title, updated, body, toc_items, cover_asset, cover_alt, slug), encoding='utf-8')
        print(f'generated {slug}.html')


if __name__ == '__main__':
    main()
