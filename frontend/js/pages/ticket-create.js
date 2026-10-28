import { ApiError } from "../api/client.js";
import { createTicket, findCustomer } from "../api/tickets.api.js";
import { h } from "../components/dom.js";
import { clearFieldErrors, showFieldErrors } from "../components/form.js";
import { canWrite, mountLayout, requireLogin } from "../components/layout.js";

const user = requireLogin();
if (user) {
  const main = mountLayout("tickets", user);
  if (!canWrite(user)) {
    main.append(h("div", { class: "card" }, h("p", { class: "state-title" }, "Bạn không có quyền tạo phiếu"),
      h("a", { class: "btn btn-outline", href: "tickets.html" }, "Về danh sách phiếu")));
  } else {
    const field = (name, label, control) => h("div", { class: "field", id: `f-${name}` },
      h("label", { for: name }, label), control, h("div", { class: "field-error" }));
    const errorBox = h("div", { class: "alert alert-error hidden", role: "alert" });
    const hint = h("div", { class: "muted", style: "font-size:13px;margin-top:4px" });
    const phone = h("input", { id: "customer_phone", inputmode: "tel", placeholder: "Ví dụ 0912 345 678" });
    const name = h("input", { id: "customer_name", placeholder: "Họ và tên khách hàng" });
    const desc = h("textarea", { id: "issue_desc", rows: "4", placeholder: "Mô tả lỗi (10 đến 2000 ký tự)" });
    const priority = h("select", { id: "priority" },
      h("option", { value: "TRUNG_BINH" }, "Trung bình"), h("option", { value: "CAO" }, "Cao"), h("option", { value: "THAP" }, "Thấp"));
    const submit = h("button", { class: "btn", type: "submit" }, "Tạo phiếu");
    const form = h("form", { novalidate: true, id: "ticket-form" },
      field("customer_phone", "Số điện thoại", phone), hint,
      field("customer_name", "Tên khách hàng", name),
      field("issue_desc", "Mô tả lỗi", desc),
      field("priority", "Mức ưu tiên", priority),
      h("div", {}, submit, " ", h("a", { class: "btn btn-outline", href: "tickets.html" }, "Hủy")));

    // Khách đã có số điện thoại này thì điền sẵn tên (một số điện thoại = một hồ sơ khách)
    phone.addEventListener("blur", async () => {
      hint.textContent = "";
      if (!phone.value.trim()) return;
      try {
        const customer = await findCustomer(phone.value.trim());
        name.value = customer.full_name;
        hint.textContent = `Khách quen: ${customer.full_name} (${customer.tickets.length} phiếu gần đây)`;
      } catch { /* chưa có khách này hoặc số chưa hợp lệ: để nhập tay, máy chủ sẽ báo lỗi khi gửi */ }
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearFieldErrors(form);
      errorBox.classList.add("hidden");
      submit.disabled = true;
      submit.textContent = "Đang tạo...";
      try {
        const created = await createTicket({
          customer_name: name.value.trim(), customer_phone: phone.value.trim(),
          issue_desc: desc.value.trim(), priority: priority.value,
        });
        location.href = `ticket-detail.html?id=${created.ticket_id}`;
      } catch (err) {
        const shown = err instanceof ApiError ? showFieldErrors(form, err.fields) : 0;
        if (!shown) { errorBox.textContent = err.message; errorBox.classList.remove("hidden"); }
        submit.disabled = false;
        submit.textContent = "Tạo phiếu";
      }
    });

    main.append(h("div", { class: "page-head" }, h("div", {}, h("h1", {}, "Tạo phiếu mới"),
      h("div", { class: "muted" }, "Hạn cam kết được tính tự động theo mức ưu tiên"))),
      h("div", { class: "card", style: "max-width:640px" }, errorBox, form));
  }
}
