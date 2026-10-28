// LỚP CLIENT DUY NHẤT gọi API: mọi file khác đều đi qua đây, không nơi nào khác dùng fetch.
import { API_BASE, TOKEN_KEY, USER_KEY } from "../config.js";

export class ApiError extends Error {
  constructor(status, code, message, fields = {}) {
    super(message);
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}

export function getToken() {
  try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
}

export function getUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
}

export function saveSession(token, user) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch { /* trình duyệt chặn lưu trữ: bỏ qua, người dùng sẽ phải đăng nhập lại */ }
}

export function clearSession() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch { /* bỏ qua */ }
}

export async function request(method, path, { body, query } = {}) {
  let url = API_BASE + path;
  if (query) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== "") params.set(key, value);
    }
    const qs = params.toString();
    if (qs) url += "?" + qs;
  }

  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;

  let response;
  try {
    response = await fetch(url, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined });
  } catch {
    // Không kết nối được máy chủ: báo thân thiện, KHÔNG in địa chỉ hay chi tiết kỹ thuật
    throw new ApiError(0, "NETWORK_ERROR", "Không kết nối được máy chủ. Vui lòng kiểm tra mạng rồi thử lại.");
  }

  let data = null;
  try { data = await response.json(); } catch { /* thân phản hồi không phải JSON */ }

  if (!response.ok) {
    const err = (data && data.error) || {};
    // Hết phiên đăng nhập (không tính lúc đang đăng nhập sai mật khẩu): về trang đăng nhập
    if (response.status === 401 && err.code === "UNAUTHORIZED") {
      clearSession();
      if (!location.pathname.endsWith("login.html")) location.href = "login.html";
    }
    throw new ApiError(response.status, err.code || "UNKNOWN",
      err.message || "Có lỗi xảy ra. Vui lòng thử lại.", err.fields || {});
  }
  return data;
}
