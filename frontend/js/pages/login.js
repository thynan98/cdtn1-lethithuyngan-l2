import { ApiError, getToken, saveSession } from "../api/client.js";
import { login } from "../api/auth.api.js";
import { clearFieldErrors, showFieldErrors } from "../components/form.js";

if (getToken()) location.href = "index.html";

const form = document.getElementById("login-form");
const errorBox = document.getElementById("login-error");
const button = document.getElementById("login-btn");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFieldErrors(form);
  errorBox.classList.add("hidden");
  button.disabled = true;
  button.textContent = "Đang đăng nhập...";
  try {
    const result = await login(form.username.value.trim(), form.password.value);
    saveSession(result.access_token, result.user);
    location.href = "index.html";
  } catch (err) {
    const shown = err instanceof ApiError ? showFieldErrors(form, err.fields) : 0;
    if (!shown) {
      errorBox.textContent = err.message;      // ví dụ "Sai tên đăng nhập hoặc mật khẩu"
      errorBox.classList.remove("hidden");
    }
    button.disabled = false;
    button.textContent = "Đăng nhập";
  }
});
