// Dựng phần tử bằng textContent (không dùng innerHTML) nên dữ liệu từ máy chủ không chèn được mã lạ.
export function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") el.className = value;
    else if (key.startsWith("on") && typeof value === "function") el.addEventListener(key.slice(2), value);
    else el.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return el;
}

export function clear(el) { el.replaceChildren(); return el; }

// Xóa nội dung cũ rồi thêm các phần tử mới; bỏ qua null/false để không in chữ "null" ra trang.
export function fill(el, ...children) {
  el.replaceChildren();
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return el;
}

const FMT = new Intl.DateTimeFormat("vi-VN", {
  timeZone: "Asia/Ho_Chi_Minh", day: "2-digit", month: "2-digit", year: "numeric",
  hour: "2-digit", minute: "2-digit", hour12: false,
});
export const formatTime = (iso) => (iso ? FMT.format(new Date(iso)) : "—");

export const STATUS_LABEL = { MOI: "Mới tiếp nhận", DANG_XU_LY: "Đang xử lý", HOAN_TAT: "Hoàn tất" };
export const NEXT_STATUS = { MOI: "DANG_XU_LY", DANG_XU_LY: "HOAN_TAT" };
export const PRIORITY_LABEL = { CAO: "Cao", TRUNG_BINH: "Trung bình", THAP: "Thấp" };
export const DUE_LABEL = { CON_HAN: "Còn hạn", SAP_DEN_HAN: "Sắp đến hạn", QUA_HAN: "Quá hạn" };

export function statusBadge(status) {
  return h("span", { class: `badge badge-${status.toLowerCase()}` }, STATUS_LABEL[status] || status);
}

export function dueChip(state) {
  if (!state) return h("span", { class: "muted" }, "—");
  return h("span", { class: `chip chip-${state.toLowerCase()}` }, DUE_LABEL[state]);
}

export function remainingText(minutes) {
  if (minutes === null || minutes === undefined) return "";
  const abs = Math.abs(minutes);
  const days = Math.floor(abs / 1440), hours = Math.floor((abs % 1440) / 60), mins = abs % 60;
  const parts = [];
  if (days) parts.push(`${days} ngày`);
  if (hours) parts.push(`${hours} giờ`);
  if (!days && !hours) parts.push(`${mins} phút`);
  return (minutes < 0 ? "Trễ " : "Còn ") + parts.join(" ");
}
