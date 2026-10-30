const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');

const robots = read('robots.txt');
if (!robots.includes('Sitemap: https://liupzone.github.io/sitemap.xml')) throw new Error('robots sitemap missing');
const sitemap = read('sitemap.xml');
for (const url of ['https://liupzone.github.io/', 'https://liupzone.github.io/campus-prep.html', 'https://liupzone.github.io/campus-prep/tencent.html', 'https://liupzone.github.io/campus-prep/alibaba.html']) {
  if (!sitemap.includes(`<loc>${url}</loc>`)) throw new Error(`sitemap URL missing: ${url}`);
}

const overview = read('campus-prep.html');
const home = read('index.html');
if (!overview.includes('校招稳稳拿OFFER')) throw new Error('overview title missing');
if (!overview.includes('大厂校招备考攻略')) throw new Error('overview subtitle missing');
if (!overview.includes('内容筹备中')) throw new Error('remaining layout placeholders missing');
if (!overview.includes('id="prepSearch"')) throw new Error('search control missing');
if ((overview.match(/class="company-card/g) || []).length !== 9) {
  throw new Error('expected 9 layout cards');
}
if (!home.includes('href="campus-prep.html"') || !home.includes('data-topic="大厂校招备考攻略"')) {
  throw new Error('homepage menu link missing');
}
if (!overview.includes('href="campus-prep/tencent.html"')) throw new Error('Tencent article link missing');
if (!overview.includes('href="campus-prep/alibaba.html"')) throw new Error('Alibaba article link missing');
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
if (overview.includes('campus-prep/bytedance.html')) throw new Error('unpublished article page link should not be present');

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

console.log('campus prep publication verification passed (Tencent and Alibaba)');
