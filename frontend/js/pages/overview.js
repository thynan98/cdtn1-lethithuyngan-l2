import { getOverview } from "../api/tickets.api.js";
import { showEmpty, showError, showLoading } from "../components/data-state.js";
import { clear, dueChip, formatTime, h, PRIORITY_LABEL, statusBadge } from "../components/dom.js";
import { mountLayout, requireLogin } from "../components/layout.js";

const user = requireLogin();
if (user) {
  const main = mountLayout("overview", user);
  main.append(h("div", { class: "page-head" }, h("div", {}, h("h1", {}, "Tổng quan"),
    h("div", { class: "muted" }, "Tình hình phiếu bảo hành hiện tại"))));
  const body = h("div", {});
  main.append(body);
  load();

  async function load() {
    showLoading(body);
    try {
      render(await getOverview());
    } catch (err) {
      showError(body, err.message, load);
    }
  }

  function render(data) {
    if (data.total === 0) {
      showEmpty(body, "Chưa có phiếu bảo hành nào", "Khi có phiếu được tạo, số liệu sẽ hiện ở đây.",
        user.role === "NHAN_VIEN" ? "Tạo phiếu mới" : null, () => (location.href = "ticket-new.html"));
      return;
    }
    const pct = (n) => `${Math.round((n / data.total) * 100)}% tổng số phiếu`;
    const stat = (cls, label, value, note) => h("div", { class: `stat ${cls}` },
      h("div", { class: "stat-label" }, label), h("div", { class: "stat-value" }, value), h("div", { class: "stat-note" }, note));
    clear(body).append(
      h("div", { class: "stats" },
        stat("", "Tổng số phiếu", data.total, "Không tính phiếu đã xóa"),
        stat("", "Mới tiếp nhận", data.by_status.MOI, pct(data.by_status.MOI)),
        stat("", "Đang xử lý", data.by_status.DANG_XU_LY, pct(data.by_status.DANG_XU_LY)),
        stat("", "Hoàn tất", data.by_status.HOAN_TAT, pct(data.by_status.HOAN_TAT)),
        stat("warn", "Quá hạn", data.overdue, `trên ${data.total - data.by_status.HOAN_TAT} phiếu chưa hoàn tất`),
        stat("soon", "Sắp đến hạn", data.near_due, "còn không quá 12 giờ")),
      h("div", { class: "card" }, h("h2", {}, "Phiếu cần chú ý"),
        data.attention.length === 0
          ? h("p", { class: "muted" }, "Không có phiếu nào quá hạn hoặc sắp đến hạn.")
          : h("div", { class: "table-wrap" }, h("table", {},
            h("thead", {}, h("tr", {}, ["Mã phiếu", "Khách hàng", "Ưu tiên", "Trạng thái", "Hạn cam kết", "Cảnh báo"].map((t) => h("th", {}, t)))),
            h("tbody", {}, data.attention.map((t) => h("tr", {},
              h("td", {}, h("a", { class: "code", href: `ticket-detail.html?id=${t.ticket_id}` }, t.ticket_code)),
              h("td", {}, t.customer_name),
              h("td", {}, PRIORITY_LABEL[t.priority]),
              h("td", {}, statusBadge(t.status)),
              h("td", {}, formatTime(t.due_date)),
              h("td", {}, dueChip(t.due_state)))))))),
    );
  }
}
