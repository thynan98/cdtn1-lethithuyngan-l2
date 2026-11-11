from pymongo import ReturnDocument
MAX_ID = 2**63 - 1      # MongoDB chỉ lưu số nguyên tối đa 8 byte


def is_storable_id(value):
    """id hợp lệ để tra cứu: số nguyên từ 1 đến 8 byte. id vô lý thì chắc chắn không có bản ghi."""
    return isinstance(value, int) and 0 < value <= MAX_ID

def next_id(db, name):
    """Cấp số nguyên tiếp theo cho một thực thể (ticket, customer, ...).

    Dùng collection `counters`; $inc là thao tác nguyên tử nên hai yêu cầu
    cùng lúc không bao giờ nhận trùng số.
    """
    doc = db.counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["seq"]
