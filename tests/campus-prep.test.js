const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');
const siteUrl = 'https://www.liupzone.cn';

const robots = read('robots.txt');
if (!robots.includes(`Sitemap: ${siteUrl}/sitemap.xml`)) throw new Error('robots sitemap missing');
const sitemap = read('sitemap.xml');
const publishedSlugs = [
  'tencent', 'alibaba', 'bytedance', 'baidu', 'meituan', 'jd', 'huawei', 'kuaishou', 'dji',
  'xiaomi', 'vivo', 'oppo', 'microsoft', 'google', 'ant', 'bilibili', 'xiaohongshu', 'didi',
  'ctrip', 'pinduoduo', 'iflytek', 'mihoyo', 'horizon', 'momenta', 'xpeng', 'lixiang',
  'huawei-intelligent-driving', 'weride', 'unitree', 'ubtech', 'dreame',
];
for (const url of [`${siteUrl}/`, `${siteUrl}/campus-prep.html`, ...publishedSlugs.map((slug) => `${siteUrl}/campus-prep/${slug}.html`)]) {
  if (!sitemap.includes(`<loc>${url}</loc>`)) throw new Error(`sitemap URL missing: ${url}`);
}
if (sitemap.includes('liupzone.github.io') || robots.includes('liupzone.github.io')) {
  throw new Error('SEO entry points still reference the old GitHub Pages domain');
}

const overview = read('campus-prep.html');
const home = read('index.html');
if (!overview.includes(`<link rel="canonical" href="${siteUrl}/campus-prep.html" />`)) {
  throw new Error('overview canonical URL is not the custom domain');
}
if (!home.includes(`<link rel="canonical" href="${siteUrl}/" />`)) {
  throw new Error('home canonical URL is not the custom domain');
}
const homeBody = home.slice(home.indexOf('<body'), home.lastIndexOf('</body>'));
if (/本周更新 12 篇|27届秋招内推信息|大厂笔试面试真题合集|内容整理进度|72%|已展示最新内容（示例）|正在查看：/.test(homeBody)) {
  throw new Error('homepage still contains simulated content or interactions');
}
if (!home.includes('31 篇') || !home.includes('900 份')) {
  throw new Error('homepage should show actual published guide and resource counts');
}
for (const label of ['校招稳稳拿OFFER', '宝藏资源', '考研之路', '生活福利']) {
  if (!home.includes(label)) throw new Error(`homepage theme missing: ${label}`);
}
if (!home.includes('resources.html?category=考研')) {
  throw new Error('homepage should link to the real graduate-exam resources');
}
if ((home.match(/class="update-card"/g) || []).length !== 5) {
  throw new Error('homepage should list exactly five latest updates');
}
if (!home.includes('内容贡献') || !home.includes('campus-prep/horizon.html') || !home.includes('campus-prep/unitree.html')) {
  throw new Error('homepage latest content should use published campus articles');
}
if (home.includes('topic-grid')) {
  throw new Error('homepage should replace scenario cards with latest updates');
}
if (!home.includes('href="search.html"') || !home.includes('搜索全站内容')) {
  throw new Error('homepage should use the site-wide search');
}
const siteSearch = read('search.html');
for (const marker of ['腾讯校招备考攻略', 'resources-data.js', '校招稳稳拿OFFER', '宝藏资源']) {
  if (!siteSearch.includes(marker)) throw new Error(`site search missing: ${marker}`);
}
for (const marker of ['考研之路', '生活福利', 'fuzzyMatch', 'queryTerms', 'examResults']) {
  if (!siteSearch.includes(marker)) throw new Error(`site-wide fuzzy search missing: ${marker}`);
}
if (!overview.includes('校招稳稳拿OFFER')) throw new Error('overview title missing');
if (!overview.includes('大厂校招备考攻略')) throw new Error('overview subtitle missing');
if (overview.includes('内容筹备中')) throw new Error('overview still contains unpublished placeholders');
if (!overview.includes('id="prepSearch"')) throw new Error('search control missing');
if ((overview.match(/class="company-card/g) || []).length !== publishedSlugs.length) {
  throw new Error(`expected ${publishedSlugs.length} layout cards`);
}
if (!home.includes('href="campus-prep.html"') || !home.includes('href="resources.html"')) {
  throw new Error('homepage menu link missing');
}
if (!overview.includes('href="campus-prep/tencent.html"')) throw new Error('Tencent article link missing');
if (!overview.includes('href="campus-prep/alibaba.html"')) throw new Error('Alibaba article link missing');
if (!overview.includes('href="campus-prep/bytedance.html"')) throw new Error('ByteDance article link missing');
if (!overview.includes('href="campus-prep/baidu.html"')) throw new Error('Baidu article link missing');
for (const slug of publishedSlugs) {
  if (!overview.includes(`href="campus-prep/${slug}.html"`)) throw new Error(`${slug} article link missing`);
}
const articlePath = path.join(root, 'campus-prep', 'tencent.html');
if (!fs.existsSync(articlePath)) throw new Error('Tencent article page missing');
const article = fs.readFileSync(articlePath, 'utf8');
for (const tag of ['rel="canonical"', 'property="og:title"', 'property="og:description"', 'application/ld+json']) {
  if (!article.includes(tag)) throw new Error(`Tencent SEO tag missing: ${tag}`);
}
  if (!article.includes('assets/tencent-campus-prep-cover.svg')) throw new Error('Tencent cover missing');
  if (!article.includes('<article class="article-body">')) throw new Error('Tencent article body missing');
  if (!article.includes('<h4')) throw new Error('Tencent question sections should render as h4 headings');
  if (article.includes('<p><strong>4. 合并两个有序链表')) throw new Error('Tencent question title is still merged into a paragraph');
  if (article.includes('<p>| # | 题号')) throw new Error('Tencent frequency table is still raw Markdown');
  const cover = read('assets/tencent-campus-prep-cover.svg');
  if (!cover.includes('viewBox="0 0 1200 480"')) throw new Error('Tencent cover should use a short Zhihu-style ratio');
  if (!cover.includes('企鹅') || !cover.includes('微信') || !cover.includes('QQ')) {
    throw new Error('Tencent cover should include company-specific elements');
  }
  if (!cover.includes('Tencent')) throw new Error('Tencent cover should include the company logo lockup');
  if (article.includes('来自大厂校招备考攻略 PDF 的 final 专稿，已去除具体日期，保留公司画像、JD 拆解、高频题、技术面考点与备考路线。')) {
    throw new Error('Tencent article intro line should be removed');
  }
  if (/2026|2024|2025|\d{1,2}月|Day \d|\d+小时|\d+分钟|更新时间/.test(article)) {
  throw new Error('Tencent article still contains concrete dates or times');
}
const alibabaPath = path.join(root, 'campus-prep', 'alibaba.html');
if (!fs.existsSync(alibabaPath)) throw new Error('Alibaba article page missing');
const alibaba = fs.readFileSync(alibabaPath, 'utf8');
for (const tag of ['rel="canonical"', 'property="og:title"', 'property="og:description"', 'application/ld+json']) {
  if (!alibaba.includes(tag)) throw new Error(`Alibaba SEO tag missing: ${tag}`);
}
if (!alibaba.includes('assets/alibaba-campus-prep-cover.svg')) throw new Error('Alibaba cover missing');
if (!alibaba.includes('阿里巴巴校招全攻略')) throw new Error('Alibaba article title missing');
if (!alibaba.includes('<article class="article-body">')) throw new Error('Alibaba article body missing');
if (!alibaba.includes('<h4')) throw new Error('Alibaba question sections should render as h4 headings');
if (alibaba.includes('<p>| # | 题号')) throw new Error('Alibaba frequency table is still raw Markdown');
if (alibaba.includes('2026') || alibaba.includes('2024') || alibaba.includes('2025') || /\d{1,2}月|Day \d|\d+小时|\d+分钟|\d+天|更新时间/.test(alibaba)) {
  throw new Error('Alibaba article still contains concrete dates or times');
}
const alibabaCover = read('assets/alibaba-campus-prep-cover.svg');
if (!alibabaCover.includes('viewBox="0 0 1200 480"')) throw new Error('Alibaba cover should use a short Zhihu-style ratio');
if (!alibabaCover.includes('Alibaba') || !alibabaCover.includes('阿里云') || !alibabaCover.includes('钉钉')) {
  throw new Error('Alibaba cover should include company-specific elements and logo');
}

const bytedancePath = path.join(root, 'campus-prep', 'bytedance.html');
if (!fs.existsSync(bytedancePath)) throw new Error('ByteDance article page missing');
const bytedance = fs.readFileSync(bytedancePath, 'utf8');
for (const tag of ['rel="canonical"', 'property="og:title"', 'property="og:description"', 'application/ld+json']) {
  if (!bytedance.includes(tag)) throw new Error(`ByteDance SEO tag missing: ${tag}`);
}
if (!bytedance.includes('assets/bytedance-campus-prep-cover.svg')) throw new Error('ByteDance cover missing');
if (!bytedance.includes('字节跳动校招备考全攻略')) throw new Error('ByteDance article title missing');
if (!bytedance.includes('<article class="article-body">')) throw new Error('ByteDance article body missing');
if (!bytedance.includes('<h4')) throw new Error('ByteDance question sections should render as h4 headings');
if (bytedance.includes('<p>| # | 题号')) throw new Error('ByteDance frequency table is still raw Markdown');
if (/2026|2024|2025|\d{1,2}月|Day \d|\d+小时|\d+分钟|\d+天|更新时间/.test(bytedance)) {
  throw new Error('ByteDance article still contains concrete dates or times');
}
const bytedanceCover = read('assets/bytedance-campus-prep-cover.svg');
if (!bytedanceCover.includes('viewBox="0 0 1200 480"')) throw new Error('ByteDance cover should use a short Zhihu-style ratio');
if (!bytedanceCover.includes('ByteDance') || !bytedanceCover.includes('抖音') || !bytedanceCover.includes('飞书')) {
  throw new Error('ByteDance cover should include company-specific elements and logo');
}

const baiduPath = path.join(root, 'campus-prep', 'baidu.html');
if (!fs.existsSync(baiduPath)) throw new Error('Baidu article page missing');
const baidu = fs.readFileSync(baiduPath, 'utf8');
for (const tag of ['rel="canonical"', 'property="og:title"', 'property="og:description"', 'application/ld+json']) {
  if (!baidu.includes(tag)) throw new Error(`Baidu SEO tag missing: ${tag}`);
}
if (!baidu.includes('assets/baidu-campus-prep-cover.svg')) throw new Error('Baidu cover missing');
if (!baidu.includes('百度校招全攻略')) throw new Error('Baidu article title missing');
if (!baidu.includes('<article class="article-body">')) throw new Error('Baidu article body missing');
if (!baidu.includes('<h4')) throw new Error('Baidu question sections should render as h4 headings');
if (baidu.includes('<p>| # | 题号')) throw new Error('Baidu frequency table is still raw Markdown');
if (/2026|2024|2025|\d{1,2}月|Day \d|\d+小时|\d+分钟|\d+天|更新时间|金三银四/.test(baidu)) {
  throw new Error('Baidu article still contains concrete dates or times');
}
const baiduCover = read('assets/baidu-campus-prep-cover.svg');
if (!baiduCover.includes('viewBox="0 0 1200 480"')) throw new Error('Baidu cover should use a short Zhihu-style ratio');
if (!baiduCover.includes('Baidu') || !baiduCover.includes('文心') || !baiduCover.includes('Apollo')) {
  throw new Error('Baidu cover should include company-specific elements and logo');
}

const laterArticles = [
  ['meituan', '美团校招全攻略', 'Meituan', '外卖'],
  ['jd', '京东校招全攻略', 'JD.com', '物流'],
  ['huawei', '华为校招备考攻略', 'HUAWEI', '鸿蒙'],
  ['kuaishou', '快手校招全攻略', 'Kuaishou', '直播'],
  ['dji', '大疆创新校招备考攻略', 'DJI', '无人机'],
];
for (const [slug, title, logo, element] of laterArticles) {
  const page = read(`campus-prep/${slug}.html`);
  for (const tag of ['rel="canonical"', 'property="og:title"', 'property="og:description"', 'application/ld+json']) {
    if (!page.includes(tag)) throw new Error(`${slug} SEO tag missing: ${tag}`);
  }
  if (!page.includes(`<article class="article-body">`)) throw new Error(`${slug} article body missing`);
  if (!page.includes('<h3') && !page.includes('<h4')) throw new Error(`${slug} article subheadings are missing`);
  if (page.includes('<p>| # | 题号')) throw new Error(`${slug} frequency table is still raw Markdown`);
  if (/2026|2024|2025|\d{1,2}月|Day \d|\d+小时|\d+分钟|\d+天|更新时间|金三银四/.test(page)) {
    throw new Error(`${slug} article still contains concrete dates or times`);
  }
  const cover = read(`assets/${slug}-campus-prep-cover.svg`);
  if (!cover.includes('viewBox="0 0 1200 480"') || !cover.includes(logo) || !cover.includes(element)) {
    throw new Error(`${slug} cover should include company-specific elements and logo`);
  }
}

const aggregateArticles = [
  ['xiaomi', '小米', 'Xiaomi', 'IoT'],
  ['vivo', 'vivo', 'vivo', '影像'],
  ['oppo', 'OPPO', 'OPPO', 'ColorOS'],
  ['microsoft', '微软中国', 'Microsoft', 'Azure'],
  ['google', '谷歌', 'Google', 'Search'],
  ['ant', '蚂蚁集团', 'Ant Group', '支付'],
  ['bilibili', '哔哩哔哩', 'bilibili', '直播'],
  ['xiaohongshu', '小红书', 'REDnote', '推荐'],
  ['didi', '滴滴', 'DiDi', '出行'],
  ['ctrip', '携程', 'Trip.com', '旅行'],
  ['pinduoduo', '拼多多', 'PDD', '电商'],
  ['iflytek', '科大讯飞', 'iFLYTEK', '语音'],
  ['mihoyo', '米哈游', 'miHoYo', '游戏'],
  ['horizon', '地平线', 'Horizon', 'BPU'],
  ['momenta', 'Momenta', 'Momenta', '自动驾驶'],
  ['xpeng', '小鹏汽车', 'XPENG', 'XNGP'],
  ['lixiang', '理想汽车', 'Li Auto', 'AD Max'],
  ['huawei-intelligent-driving', '华为智能驾驶', 'HUAWEI', 'MDC'],
  ['weride', '文远知行', 'WeRide', 'Robotaxi'],
  ['unitree', '宇树科技', 'Unitree', '四足机器人'],
  ['ubtech', '优必选科技', 'UBTECH', '人形机器人'],
  ['dreame', '追觅科技', 'Dreame', '清洁机器人'],
];
for (const [slug, title, logo, element] of aggregateArticles) {
  const page = read(`campus-prep/${slug}.html`);
  for (const tag of ['rel="canonical"', 'property="og:title"', 'property="og:description"', 'application/ld+json']) {
    if (!page.includes(tag)) throw new Error(`${slug} SEO tag missing: ${tag}`);
  }
  if (!page.includes(`<article class="article-body">`)) throw new Error(`${slug} article body missing`);
  if (!page.includes('<h3') && !page.includes('<h4')) throw new Error(`${slug} article subheadings are missing`);
  if (page.includes('<p>|')) throw new Error(`${slug} article still contains raw Markdown table rows`);
  if (/2026|2025|2024|\b19\d{2}\b|\d{1,2}月|Day \d|\d+小时|\d+分钟|\d+天|更新时间|金三银四|618|双十一/.test(page)) {
    throw new Error(`${slug} article still contains concrete dates or times`);
  }
  const cover = read(`assets/${slug}-campus-prep-cover.svg`);
  if (!cover.includes('viewBox="0 0 1200 480"') || !cover.includes(logo) || !cover.includes(element)) {
    throw new Error(`${slug} cover should include company-specific elements and logo`);
  }
}

console.log(`campus prep publication verification passed for all ${publishedSlugs.length} guides`);
