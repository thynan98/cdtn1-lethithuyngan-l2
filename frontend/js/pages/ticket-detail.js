import { ApiError } from "../api/client.js";
import { assignTechnician, changeStatus, deleteTicket, getTicket, listCategories, setCategory } from "../api/tickets.api.js";
import { listTechnicians } from "../api/technicians.api.js";
import { showError, showLoading } from "../components/data-state.js";
import { fill, dueChip, formatTime, h, NEXT_STATUS, PRIORITY_LABEL, remainingText, STATUS_LABEL, statusBadge } from "../components/dom.js";
import { canDelete, canWrite, mountLayout, requireLogin } from "../components/layout.js";

const user = requireLogin();
if (user) {
  const main = mountLayout("tickets", user);
  const id = Number(new URLSearchParams(location.search).get("id"));
  const body = h("div", {});
  main.append(body);
  load();

  async function load() {
    if (!Number.isInteger(id) || id <= 0) {
      showError(body, "Đường dẫn phiếu không hợp lệ.", null);
      return;
    }
    showLoading(body);
    try {
      const needLists = canWrite(user);
      const [ticket, categories, technicians] = await Promise.all([
        getTicket(id),
        needLists ? listCategories() : null,
        needLists ? listTechnicians() : null,
      ]);
      render(ticket, categories && categories.items, technicians && technicians.items);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        showError(body, "Không tìm thấy phiếu này. Có thể phiếu đã bị xóa.", null);
        body.firstChild.append(h("a", { class: "btn btn-outline", href: "tickets.html" }, "Về danh sách phiếu"));
      } else {
        showError(body, err.message, load);
      }
    }
  }

  function kv(label, value) {
    return h("div", {}, h("div", { class: "kv-label" }, label), h("div", { class: "kv-value" }, value));
  }

  function render(t, categories, technicians) {
    const message = h("div", { class: "alert hidden", role: "status" });
    const notify = (text, ok) => {
      message.className = "alert " + (ok ? "alert-ok" : "alert-error");
      message.textContent = text;
    };
    // Chạy một thao tác ghi: thành công thì tải lại phiếu, thất bại thì hiện lỗi rõ ràng
    const act = (fn, okText) => async () => {
      try { await fn(); await load(); } catch (err) { notify(err.message, false); return; }
      // sau load() trang đã dựng lại, nên thông báo thành công không cần hiện
    };

    const closed = t.status === "HOAN_TAT";
    const categorySel = categories && h("select", { id: "category" },
      h("option", { value: "" }, "-- Chọn loại lỗi --"),
      categories.map((c) => h("option", { value: c.category_id, selected: t.category && t.category.category_id === c.category_id }, c.category_name)));
    const techSel = technicians && h("select", { id: "technician", disabled: closed },
      h("option", { value: "" }, "-- Chọn kỹ thuật viên --"),
      technicians.map((x) => h("option", { value: x.technician_id, selected: t.technician && t.technician.technician_id === x.technician_id },
        `${x.full_name} (${x.technician_code})`)));
    const next = NEXT_STATUS[t.status];

    fill(body,
      h("div", { class: "page-head" },
        h("div", {}, h("h1", {}, t.ticket_code), h("div", {}, statusBadge(t.status), " ", dueChip(t.due_state), " ",
          h("span", { class: "muted" }, remainingText(t.remaining_minutes)))),
        h("div", {},
          h("a", { class: "btn btn-outline", href: "tickets.html" }, "← Danh sách"),
          canDelete(user) ? [" ", h("button", { class: "btn btn-danger", type: "button", onclick: () => confirmDelete(t, notify) }, "Xóa phiếu")] : null)),
      message,
      h("div", { class: "card" }, h("h2", {}, "Thông tin phiếu"),
        h("div", { class: "detail-grid" },
          kv("Khách hàng", t.customer.full_name), kv("Số điện thoại", t.customer.phone),
          kv("Mức ưu tiên", PRIORITY_LABEL[t.priority]), kv("Loại lỗi", t.category ? t.category.category_name : "Chưa phân loại"),
          kv("Kỹ thuật viên", t.technician ? t.technician.full_name : "Chưa gán"),
          kv("Tiếp nhận lúc", formatTime(t.received_at)), kv("Hạn cam kết", formatTime(t.due_date))),
        h("p", { style: "margin:14px 0 0" }, h("span", { class: "kv-label" }, "Mô tả lỗi"), h("br"), t.issue_desc)),
      canWrite(user) ? h("div", { class: "card" }, h("h2", {}, "Xử lý phiếu"),
        h("div", { class: "inline-form", style: "margin-bottom:14px" },
          h("div", { class: "field" }, h("label", { for: "category" }, "Loại lỗi"), categorySel),
          h("button", { class: "btn", type: "button", onclick: act(() => {
            if (!categorySel.value) throw new ApiError(400, "INVALID_FORMAT", "Vui lòng chọn loại lỗi");
            return setCategory(id, Number(categorySel.value));
          }) }, "Lưu loại lỗi")),
        h("div", { class: "inline-form", style: "margin-bottom:14px" },
          h("div", { class: "field" }, h("label", { for: "technician" }, "Kỹ thuật viên"), techSel),
          h("button", { class: "btn", type: "button", disabled: closed, onclick: act(() => {
            if (!techSel.value) throw new ApiError(400, "INVALID_FORMAT", "Vui lòng chọn kỹ thuật viên");
            return assignTechnician(id, Number(techSel.value));
          }) }, "Gán / Đổi")),
        closed ? h("p", { class: "muted" }, "Phiếu đã hoàn tất, không thể gán hoặc đổi kỹ thuật viên.")
          : h("button", { class: "btn btn-outline", type: "button", onclick: act(() => changeStatus(id, next)) },
            `Chuyển sang "${STATUS_LABEL[next]}"`)) : null,
      h("div", { class: "two-col" },
        h("div", { class: "card" }, h("h2", {}, "Lịch sử trạng thái"),
          h("ul", { class: "history" }, t.status_history.map((r) => h("li", {},
            r.from_status ? `${STATUS_LABEL[r.from_status]} → ${STATUS_LABEL[r.to_status]}` : `Tạo phiếu (${STATUS_LABEL[r.to_status]})`,
            h("div", { class: "muted" }, formatTime(r.changed_at)))))),
        h("div", { class: "card" }, h("h2", {}, "Lịch sử kỹ thuật viên"),
          t.assignment_history.length === 0 ? h("p", { class: "muted" }, "Chưa gán kỹ thuật viên nào.")
            : h("ul", { class: "history" }, t.assignment_history.map((r) => h("li", {},
              `${r.from_technician ? r.from_technician.full_name : "Chưa gán"} → ${r.to_technician.full_name}`,
              h("div", { class: "muted" }, formatTime(r.changed_at))))))));
  }

  function confirmDelete(t, notify) {
    const close = () => backdrop.remove();
    const confirmBtn = h("button", { class: "btn btn-danger", type: "button", onclick: async () => {
      confirmBtn.disabled = true;
      try { await deleteTicket(id); location.href = "tickets.html"; }
      catch (err) { close(); notify(err.message, false); }
    } }, "Xóa phiếu");
    const backdrop = h("div", { class: "modal-back", role: "dialog", "aria-modal": "true" },
      h("div", { class: "modal" }, h("h2", {}, "Xóa phiếu?"),
        h("p", {}, `Phiếu ${t.ticket_code} sẽ bị ẩn khỏi danh sách. Dữ liệu vẫn được giữ lại trong hệ thống.`),
        h("div", { class: "modal-actions" }, h("button", { class: "btn btn-outline", type: "button", onclick: close }, "Hủy"), confirmBtn)));
    document.body.append(backdrop);
  }
}
