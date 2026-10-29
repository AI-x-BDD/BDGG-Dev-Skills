const MOCK = {
  {{資料集名稱}}: [
    { {{欄位名稱與假資料的值,用逗號分隔;有圖片的資料加上 image: 依 id 固定的佔位照片網址}} },
  ],
};

const Proto = {
  load(key) {
    try {
      return JSON.parse(localStorage.getItem(`proto:${key}`)) ?? structuredClone(MOCK[key]);
    } catch {
      return structuredClone(MOCK[key]);
    }
  },
  save(key, value) {
    try {
      localStorage.setItem(`proto:${key}`, JSON.stringify(value));
    } catch {
      if (!document.querySelector(".proto-warn")) {
        document.body.insertAdjacentHTML("beforeend", "<p class=\"proto-warn\">這個預覽不允許儲存,換頁後資料會回到初始值,請改用瀏覽器開啟</p>");
      }
    }
    Proto.badge();
  },
  reset() {
    try {
      Object.keys(MOCK).forEach((key) => localStorage.removeItem(`proto:${key}`));
    } catch {}
    location.reload();
  },
  showState(name) {
    document.querySelectorAll("[data-state]").forEach((el) => {
      el.hidden = el.dataset.state !== name;
    });
  },
  badge() {
    {{跨畫面共用的數字:從 Proto.load 算出來寫進導覽列的徽章;沒有就留空}}
  },
  thumb(item) {
    return `<img class="thumb" src="${item.image}" alt="${item.name ?? ""}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'), { className: 'thumb' }))">`;
  },
  later(ms, fn) {
    return setTimeout(fn, ms);
  },
  money(n) {
    return `{{貨幣符號}}${n.toLocaleString("{{地區代碼,例如 zh-TW}}")}`;
  },
};

document.addEventListener("DOMContentLoaded", () => {
  Proto.showState(new URLSearchParams(location.search).get("state") ?? "normal");
  Proto.badge();
});
