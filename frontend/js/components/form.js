// Hiện lỗi theo từng ô nhập: máy chủ trả "fields": {tên_trường: lý do}; mỗi ô có id "f-<tên_trường>".
export function clearFieldErrors(form) {
  form.querySelectorAll(".field").forEach((f) => {
    f.classList.remove("invalid");
    const box = f.querySelector(".field-error");
    if (box) box.textContent = "";
  });
}

export function showFieldErrors(form, fields) {
  let shown = 0;
  for (const [name, reason] of Object.entries(fields || {})) {
    const field = form.querySelector(`#f-${name}`);
    if (!field) continue;
    field.classList.add("invalid");
    const box = field.querySelector(".field-error");
    if (box) box.textContent = reason;
    shown++;
  }
  return shown;
}
