"""Tiện ích thời gian. Mọi thời điểm nghiệp vụ tính theo giờ Việt Nam (UTC+7)."""
from datetime import datetime, timedelta, timezone

VN = timezone(timedelta(hours=7))


def now_vn():
    """Thời điểm hiện tại theo giờ Việt Nam (có múi giờ)."""
    return datetime.now(VN)


def as_vn(dt):
    """Đổi một datetime về giờ Việt Nam. Datetime không có múi giờ được coi là UTC
    (đó là cách MongoDB trả về khi không bật tz_aware)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(VN)


def iso_vn(dt):
    """Chuỗi ISO 8601 kèm múi giờ, ví dụ 2026-10-05T14:30:00+07:00 (theo api-contract)."""
    dt = as_vn(dt)
    return dt.isoformat(timespec="seconds") if dt else None
