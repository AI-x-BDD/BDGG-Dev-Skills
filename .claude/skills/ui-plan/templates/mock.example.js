const MOCK = {
  products: [
    { id: "p-tea-01", name: "阿里山高山烏龍茶 150g", price: 680, stock: 24, category: "茶葉", image: "https://picsum.photos/seed/p-tea-01/240/240" },
    { id: "p-soap-02", name: "山茶花手工皂 3 入組(無香精,敏感肌適用)", price: 420, stock: 3, category: "洗沐", image: "https://picsum.photos/seed/p-soap-02/240/240" },
    { id: "p-cup-03", name: "鶯歌柴燒對杯", price: 1280, stock: 0, category: "器皿", image: "https://picsum.photos/seed/p-cup-03/240/240" },
    { id: "p-honey-04", name: "龍眼蜜 700g", price: 550, stock: 40, category: "食品", image: "https://picsum.photos/seed/p-honey-04/240/240" },
  ],
  cart: [
    { productId: "p-tea-01", name: "阿里山高山烏龍茶 150g", price: 680, quantity: 2, image: "https://picsum.photos/seed/p-tea-01/240/240" },
    { productId: "p-soap-02", name: "山茶花手工皂 3 入組(無香精,敏感肌適用)", price: 420, quantity: 4, image: "https://picsum.photos/seed/p-soap-02/240/240" },
  ],
  orders: [
    { orderId: "ORD-7K2M9QXA", status: "paid", total: 1780, createdAt: "2026-10-18T14:32:00+08:00", image: "https://picsum.photos/seed/p-honey-04/240/240" },
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
    const el = document.getElementById("cart-count");
    if (!el) return;
    const count = Proto.load("cart").reduce((sum, item) => sum + item.quantity, 0);
    el.textContent = count;
    el.hidden = count === 0;
  },
  thumb(item) {
    return `<img class="thumb" src="${item.image}" alt="${item.name ?? ""}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'), { className: 'thumb' }))">`;
  },
  later(ms, fn) {
    return setTimeout(fn, ms);
  },
  money(n) {
    return `NT$${n.toLocaleString("zh-TW")}`;
  },
};

document.addEventListener("DOMContentLoaded", () => {
  Proto.showState(new URLSearchParams(location.search).get("state") ?? "normal");
  Proto.badge();
});
