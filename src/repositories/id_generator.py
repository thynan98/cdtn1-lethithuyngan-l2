from pymongo import ReturnDocument


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
