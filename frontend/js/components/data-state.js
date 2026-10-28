// Ba trạng thái dùng chung cho mọi màn: đang tải, rỗng, lỗi (có nút Thử lại).
import { h, clear } from "./dom.js";

export function showLoading(container, text = "Đang tải dữ liệu...") {
  clear(container).append(
    h("div", { class: "state state-loading", role: "status" },
      h("div", { class: "spinner", "aria-hidden": "true" }), h("p", {}, text)));
}

// actionLabel/onAction: nút gợi ý hành động, ví dụ "Xóa bộ lọc" hoặc "Tạo phiếu mới"
export function showEmpty(container, title, hint, actionLabel, onAction) {
  clear(container).append(
    h("div", { class: "state state-empty" },
      h("p", { class: "state-title" }, title),
      hint ? h("p", { class: "muted" }, hint) : null,
      actionLabel ? h("button", { class: "btn btn-outline", type: "button", onclick: onAction }, actionLabel) : null));
}

export function showError(container, message, onRetry) {
  clear(container).append(
    h("div", { class: "state state-error", role: "alert" },
      h("p", { class: "state-title" }, "Không tải được dữ liệu"),
      h("p", { class: "muted" }, message),
      onRetry ? h("button", { class: "btn", type: "button", onclick: onRetry }, "Thử lại") : null));
}