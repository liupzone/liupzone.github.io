(function () {
  const endpoint = 'https://liupzone.goatcounter.com/count';
  const site = 'https://liupzone.goatcounter.com';

  const tracker = document.createElement('script');
  tracker.async = true;
  tracker.src = 'https://gc.zgo.at/count.js';
  tracker.setAttribute('data-goatcounter', endpoint);
  document.head.appendChild(tracker);

  const count = document.getElementById('visitCount');
  const source = document.getElementById('visitSource');
  const day = document.getElementById('visitDay');
  if (!count || !source || !day) return;

  const now = new Date();
  const localDay = [now.getFullYear(), String(now.getMonth() + 1).padStart(2, '0'), String(now.getDate()).padStart(2, '0')].join('-');
  day.textContent = localDay;

  const fallbackKey = 'liupzone:daily-visit';
  let records = [];
  try {
    const stored = JSON.parse(localStorage.getItem(fallbackKey) || '[]');
    records = Array.isArray(stored) ? stored : [];
  } catch (error) {}
  let today = records.filter((item) => item && item.day === localDay);
  if (!today.length) {
    records.push({ day: localDay, at: now.toISOString() });
    today = [records[records.length - 1]];
    try { localStorage.setItem(fallbackKey, JSON.stringify(records)); } catch (error) {}
  }
  count.textContent = String(today.length);

  fetch(site + '/counter/TOTAL.json?start=day', { headers: { Accept: 'application/json' } })
    .then((response) => response.ok ? response.json() : Promise.reject(new Error('analytics request failed')))
    .then((data) => {
      const total = Number(String(data.count || data.count_unique || '').replace(/,/g, ''));
      if (!Number.isFinite(total)) throw new Error('analytics response missing count');
      count.textContent = String(total);
      source.textContent = '全站统计';
      source.classList.add('is-live');
    })
    .catch(() => {});
}());
