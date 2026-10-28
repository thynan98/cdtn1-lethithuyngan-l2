// Khung chung: thanh trên (logo, người dùng, Đăng xuất) và menu bên. Chưa đăng nhập thì về trang đăng nhập.
import { clearSession, getToken, getUser } from "../api/client.js";
import { h } from "./dom.js";

const MENU = [
  { key: "overview", href: "index.html", label: "Tổng quan" },
  { key: "tickets", href: "tickets.html", label: "Danh sách phiếu" },
];

export function requireLogin() {
  const user = getUser();
  if (!getToken() || !user) {
    location.href = "login.html";
    return null;
  }
  return user;
}

export const canWrite = (user) => user.role === "NHAN_VIEN";   // tạo, phân loại, gán, đổi trạng thái
export const canDelete = (user) => user.role === "QUAN_LY";    // xóa (ẩn) phiếu
export const ROLE_LABEL = { NHAN_VIEN: "Nhân viên tiếp nhận", QUAN_LY: "Quản lý trung tâm" };

export function mountLayout(active, user) {
  const logout = () => { clearSession(); location.href = "login.html"; };
  const menuBox = h("div", { class: "user-menu hidden", id: "user-menu" },
    h("button", { class: "user-menu-item", type: "button", onclick: logout }, "Đăng xuất"));
  const userBtn = h("button", { class: "user-btn", type: "button", "aria-haspopup": "true",
    onclick: () => menuBox.classList.toggle("hidden") },
    h("span", { class: "avatar", "aria-hidden": "true" }, user.full_name.trim().charAt(0).toUpperCase()),
    h("span", { class: "user-name" }, user.full_name));
  document.addEventListener("click", (e) => {
    if (!menuBox.contains(e.target) && !userBtn.contains(e.target)) menuBox.classList.add("hidden");
  });

  const header = h("header", { class: "topbar" },
    h("div", { class: "brand" },
      h("img", { class: "brand-logo", src: "img/logo.svg", alt: "Logo Mekong Mobile" }),
      h("div", {}, h("div", { class: "brand-name" }, "Mekong Mobile"),
        h("div", { class: "brand-sub" }, "QUẢN LÝ PHIẾU BẢO HÀNH"))),
    h("div", { class: "user-box" }, userBtn, menuBox));
  const nav = h("nav", { class: "sidebar", "aria-label": "Menu chính" },
    MENU.map((m) => h("a", { href: m.href, class: "nav-item" + (m.key === active ? " active" : "") }, m.label)));

  const main = document.getElementById("main");
  document.body.prepend(header, nav);
  return main;
}
