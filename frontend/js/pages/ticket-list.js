import { listTickets } from "../api/tickets.api.js";
import { showEmpty, showError, showLoading } from "../components/data-state.js";
import { clear, dueChip, formatTime, h, PRIORITY_LABEL, statusBadge } from "../components/dom.js";
import { canWrite, mountLayout, requireLogin } from "../components/layout.js";

const TABS = [
  { key: "ALL", label: "Tất cả", query: {} },
  { key: "MOI", label: "Mới tiếp nhận", query: { status: "MOI" } },
  { key: "DANG_XU_LY", label: "Đang xử lý", query: { status: "DANG_XU_LY" } },
  { key: "HOAN_TAT", label: "Hoàn tất", query: { status: "HOAN_TAT" } },
  { key: "OVERDUE", label: "Quá hạn", query: { overdue: true } },
];
const SIZE = 10;

const user = requireLogin();
if (user) {
  const main = mountLayout("tickets", user);
  let tab = "ALL";
  let page = 1;

  main.append(h("div", { class: "page-head" },
    h("div", {}, h("h1", {}, "Danh sách phiếu"), h("div", { class: "muted" }, "Phiếu mới nhất hiện trước")),
    canWrite(user) ? h("a", { class: "btn", href: "ticket-new.html" }, "+ Tạo phiếu mới") : null));
  const tabsBox = h("div", { class: "tabs", role: "tablist" });
  const body = h("div", { class: "card" });
  main.append(tabsBox, body);
  drawTabs();
  load();

  function drawTabs() {
    clear(tabsBox).append(...TABS.map((t) => h("button", {
      class: "tab" + (t.key === tab ? " active" : ""), type: "button", role: "tab",
      onclick: () => { tab = t.key; page = 1; drawTabs(); load(); },
    }, t.label)));
  }

  async function load() {
    showLoading(body);
    const query = { ...TABS.find((t) => t.key === tab).query, page, size: SIZE };
    try {
      render(await listTickets(query));
    } catch (err) {
      showError(body, err.message, load);
    }
  }

  function render(data) {
    if (data.total === 0) {
      if (tab === "ALL") {       // thật sự chưa có dữ liệu
        showEmpty(body, "Chưa có phiếu bảo hành nào", "Phiếu được tạo sẽ xuất hiện ở đây.",
          canWrite(user) ? "Tạo phiếu mới" : null, () => (location.href = "ticket-new.html"));
      } else {                   // có dữ liệu nhưng bộ lọc không khớp
        showEmpty(body, "Không có phiếu nào phù hợp với bộ lọc", "Thử chọn bộ lọc khác.",
          "Xóa bộ lọc", () => { tab = "ALL"; page = 1; drawTabs(); load(); });
      }
      return;
    }
    const pages = Math.max(1, Math.ceil(data.total / SIZE));
    clear(body).append(
      h("div", { class: "table-wrap" }, h("table", {},
        h("thead", {}, h("tr", {}, ["Mã phiếu", "Khách hàng", "Số điện thoại", "Ưu tiên", "Trạng thái", "Kỹ thuật viên", "Hạn cam kết"].map((t) => h("th", {}, t)))),
        h("tbody", {}, data.items.map((t) => h("tr", {},
          h("td", {}, h("a", { class: "code", href: `ticket-detail.html?id=${t.ticket_id}` }, t.ticket_code)),
          h("td", {}, t.customer_name),
          h("td", {}, t.customer_phone),
          h("td", {}, PRIORITY_LABEL[t.priority]),
          h("td", {}, statusBadge(t.status)),
          h("td", {}, t.technician_name || h("span", { class: "muted" }, "Chưa gán")),
          h("td", {}, h("div", {}, formatTime(t.due_date)), dueChip(t.due_state)))))),
      ),
      h("div", { class: "pager" },
        h("span", { class: "muted" }, `${data.total} phiếu · Trang ${page}/${pages}`),
        h("div", {},
          h("button", { class: "btn btn-outline", type: "button", disabled: page <= 1, onclick: () => { page--; load(); } }, "Trước"),
          " ",
          h("button", { class: "btn btn-outline", type: "button", disabled: page >= pages, onclick: () => { page++; load(); } }, "Sau"))));
  }
}
