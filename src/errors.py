class AppError(Exception):
    """Lỗi nghiệp vụ có MÃ, không mang mã HTTP (routes sẽ dịch mã sang HTTP).

    code    : mã theo docs/api-contract.md, ví dụ INVALID_TRANSITION
    message : câu cho người dùng đọc
    fields  : dict {tên trường: lý do} khi lỗi gắn với trường cụ thể
    """

    def __init__(self, code, message, fields=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.fields = fields or {}
