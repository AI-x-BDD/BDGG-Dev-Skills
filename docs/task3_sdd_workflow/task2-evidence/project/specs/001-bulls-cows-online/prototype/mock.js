const PREVIEW_PLAYERS = [
  { seat: 1, nickname: "小羊", host: true, conn: "online", inGame: true, secret: "3906" },
  { seat: 2, nickname: "阿哲", host: false, conn: "online", inGame: true, secret: "5803" },
  { seat: 3, nickname: "週五晚上只想猜數字的人類", host: false, conn: "online", inGame: true, secret: "9461" },
  { seat: 4, nickname: "小明", host: false, conn: "online", inGame: true, secret: "2759" },
];

const PREVIEW_ROUND_1 = [
  { round: 1, from: 1, to: 2, digits: "5132" },
  { round: 1, from: 2, to: 3, digits: "4096" },
  { round: 1, from: 3, to: 4, digits: "0371" },
  { round: 1, from: 4, to: 1, digits: "1357" },
];

const withSecrets = (secrets) => PREVIEW_PLAYERS.map((p) => ({ ...p, secret: secrets[p.seat - 1] }));

const MOCK = {
  lobby: [],
  room: {
    me: 1,
    players: [{ seat: 1, nickname: "小羊", host: true, conn: "online" }],
    incoming: [
      { after: 3000, nickname: "Mina 米娜" },
      { after: 7000, nickname: "小明" },
      { after: 12000, nickname: "小明" },
    ],
    notice: "你開了一間新房間,坐 1 號座位",
  },
  game: {
    phase: "setup",
    round: 1,
    turn: null,
    mySeat: 1,
    players: withSecrets([null, null, null, null]),
    log: [],
    notice: "",
    autoSecret: false,
    winner: null,
    reason: null,
  },
  joiners: [
    { after: 3000, nickname: "Mina 米娜" },
    { after: 7000, nickname: "小明" },
    { after: 12000, nickname: "小明" },
  ],
  secretPool: ["5803", "9461", "2759"],
  guessPool: ["1234", "5678", "0291", "8463", "7105", "3480", "6917", "2058", "4729", "9312", "0846", "1597"],
  preview: {
    index: {
      normal: { nickname: "" },
      "nickname-empty": { nickname: "   " },
      "nickname-long": { nickname: "我是一個很長很長很長的暱稱喔" },
      loading: { nickname: "小羊" },
      error: { nickname: "小羊" },
    },
    room: {
      alone: {
        me: 1,
        players: [{ seat: 1, nickname: "小羊", host: true, conn: "online" }],
        notice: "你開了一間新房間,坐 1 號座位",
      },
      "host-ready": {
        me: 1,
        players: [
          { seat: 1, nickname: "小羊", host: true, conn: "online" },
          { seat: 2, nickname: "Mina 米娜", host: false, conn: "online" },
          { seat: 3, nickname: "小明", host: false, conn: "online" },
          { seat: 4, nickname: "小明 (2)", host: false, conn: "online" },
        ],
        notice: "小明 (2) 加入,坐 4 號座位",
      },
      guest: {
        me: 3,
        players: [
          { seat: 1, nickname: "阿哲", host: true, conn: "online" },
          { seat: 2, nickname: "週五晚上只想猜數字的人類", host: false, conn: "online" },
          { seat: 3, nickname: "小羊", host: false, conn: "online" },
        ],
        notice: "你加入了阿哲的房間,坐 3 號座位",
      },
      "host-transferred": {
        me: 2,
        players: [
          { seat: 2, nickname: "小羊", host: true, conn: "online" },
          { seat: 3, nickname: "阿哲", host: false, conn: "online" },
        ],
        notice: "1 號 Mina 米娜 離開了房間,房主改由座位最前面的你擔任",
      },
      "seat-refill": {
        me: 1,
        players: [
          { seat: 1, nickname: "小羊", host: true, conn: "online" },
          { seat: 2, nickname: "Jessie 潔西", host: false, conn: "online" },
          { seat: 3, nickname: "阿哲", host: false, conn: "online" },
        ],
        notice: "Jessie 潔西 加入,坐進空出來的 2 號座位",
      },
      disconnected: {
        me: 1,
        players: [
          { seat: 1, nickname: "小羊", host: true, conn: "online" },
          { seat: 2, nickname: "阿哲", host: false, conn: "offline" },
          { seat: 3, nickname: "小明", host: false, conn: "online" },
        ],
        notice: "2 號 阿哲 斷線中,座位先幫他保留",
      },
      loading: {
        me: 1,
        players: [
          { seat: 1, nickname: "小羊", host: true, conn: "online" },
          { seat: 2, nickname: "Mina 米娜", host: false, conn: "online" },
          { seat: 3, nickname: "小明", host: false, conn: "online" },
          { seat: 4, nickname: "小明 (2)", host: false, conn: "online" },
        ],
        notice: "",
      },
    },
    game: {
      setup: {
        phase: "setup", round: 1, turn: null, remaining: 47, mySeat: 1,
        players: withSecrets([null, null, "9461", null]), log: [], notice: "", autoSecret: false,
      },
      "setup-invalid": {
        phase: "setup", round: 1, turn: null, remaining: 41, mySeat: 1, inputValue: "1123",
        players: withSecrets([null, null, "9461", null]), log: [], notice: "", autoSecret: false,
      },
      "setup-done": {
        phase: "setup", round: 1, turn: null, remaining: 31, mySeat: 1,
        players: withSecrets(["3906", null, "9461", "2759"]), log: [], notice: "", autoSecret: false,
      },
      "setup-auto": {
        phase: "setup", round: 1, turn: null, remaining: 0, mySeat: 1,
        players: withSecrets(["7024", "5803", "9461", "2759"]), log: [],
        notice: "60 秒到了,所有人都設定好了,馬上從 1 號開始猜", autoSecret: true,
      },
      "my-turn": {
        phase: "guessing", round: 2, turn: 1, remaining: 52, mySeat: 1,
        players: PREVIEW_PLAYERS, log: PREVIEW_ROUND_1, notice: "", autoSecret: false,
      },
      "guess-invalid": {
        phase: "guessing", round: 2, turn: 1, remaining: 38, mySeat: 1, inputValue: "12a4",
        players: PREVIEW_PLAYERS, log: PREVIEW_ROUND_1, notice: "", autoSecret: false,
      },
      "waiting-turn": {
        phase: "guessing", round: 2, turn: 2, remaining: 44, mySeat: 1,
        players: PREVIEW_PLAYERS, log: [...PREVIEW_ROUND_1, { round: 2, from: 1, to: 2, digits: "5830" }],
        notice: "", autoSecret: false,
      },
      timeout: {
        phase: "guessing", round: 2, turn: 4, remaining: 58, mySeat: 1,
        players: PREVIEW_PLAYERS,
        log: [
          ...PREVIEW_ROUND_1,
          { round: 2, from: 1, to: 2, digits: "5830" },
          { round: 2, from: 2, to: 3, digits: "9640" },
          { round: 2, from: 3, to: 4, timeout: true },
        ],
        notice: "3 號 週五晚上只想猜數字的人類 60 秒內沒有猜,視為放棄這一次(不會出局)",
        autoSecret: false,
      },
      disconnected: {
        phase: "guessing", round: 2, turn: 3, remaining: 36, mySeat: 1,
        players: PREVIEW_PLAYERS.map((p) => (p.seat === 3 ? { ...p, conn: "offline" } : p)),
        log: [
          ...PREVIEW_ROUND_1,
          { round: 2, from: 1, to: 2, digits: "5830" },
          { round: 2, from: 2, to: 3, digits: "9640" },
        ],
        notice: "3 號 週五晚上只想猜數字的人類 斷線中",
        autoSecret: false,
      },
      eliminated: {
        phase: "guessing", round: 3, turn: 2, remaining: 55, mySeat: 1,
        players: PREVIEW_PLAYERS.map((p) => (p.seat === 3 ? { ...p, conn: "left", inGame: false } : p)),
        log: [
          ...PREVIEW_ROUND_1,
          { round: 2, from: 1, to: 2, digits: "5830" },
          { round: 2, from: 2, to: 3, digits: "9640" },
          { round: 2, from: 3, to: 4, timeout: true },
          { round: 2, from: 4, to: 1, digits: "3960" },
          { round: 3, from: 1, to: 2, digits: "5870" },
        ],
        notice: "3 號 週五晚上只想猜數字的人類 已離開(斷線超過 60 秒),2 號 阿哲 改猜 4 號 小明",
        autoSecret: false,
      },
      reconnecting: {
        phase: "guessing", round: 2, turn: 2, remaining: 44, mySeat: 1,
        players: PREVIEW_PLAYERS, log: [...PREVIEW_ROUND_1, { round: 2, from: 1, to: 2, digits: "5830" }],
        notice: "", autoSecret: false,
      },
      "leave-confirm": {
        phase: "guessing", round: 2, turn: 2, remaining: 44, mySeat: 1,
        players: PREVIEW_PLAYERS, log: [...PREVIEW_ROUND_1, { round: 2, from: 1, to: 2, digits: "5830" }],
        notice: "", autoSecret: false,
      },
    },
    result: {
      lose: {
        phase: "ended", mySeat: 1, winner: 3, reason: "guess",
        players: PREVIEW_PLAYERS,
        log: [
          ...PREVIEW_ROUND_1,
          { round: 2, from: 1, to: 2, digits: "5830" },
          { round: 2, from: 2, to: 3, digits: "9640" },
          { round: 2, from: 3, to: 4, digits: "2795" },
          { round: 2, from: 4, to: 1, digits: "3960" },
          { round: 3, from: 1, to: 2, digits: "5870" },
          { round: 3, from: 2, to: 3, digits: "9604" },
          { round: 3, from: 3, to: 4, digits: "2759" },
        ],
      },
      win: {
        phase: "ended", mySeat: 1, winner: 1, reason: "guess",
        players: PREVIEW_PLAYERS,
        log: [
          ...PREVIEW_ROUND_1,
          { round: 2, from: 1, to: 2, digits: "5830" },
          { round: 2, from: 2, to: 3, digits: "9640" },
          { round: 2, from: 3, to: 4, digits: "2795" },
          { round: 2, from: 4, to: 1, digits: "3960" },
          { round: 3, from: 1, to: 2, digits: "5803" },
        ],
      },
      "last-one": {
        phase: "ended", mySeat: 1, winner: 1, reason: "last-one",
        players: PREVIEW_PLAYERS.map((p) => (p.seat === 1 ? p : { ...p, conn: "left", inGame: false })),
        log: PREVIEW_ROUND_1,
      },
      "early-end": {
        phase: "ended", mySeat: 1, winner: 1, reason: "last-one",
        players: [
          { seat: 1, nickname: "小羊", host: true, conn: "online", inGame: true, secret: "3906" },
          { seat: 2, nickname: "阿哲", host: false, conn: "left", inGame: false, secret: "5803" },
          { seat: 3, nickname: "週五晚上只想猜數字的人類", host: false, conn: "left", inGame: false, secret: null },
        ],
        log: [],
      },
    },
  },
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
