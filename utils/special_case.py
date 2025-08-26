"""
特殊驗證案例判斷
"""
def is_special_case(user_id):
    special_ids = {
        "U2bcd63000805da076721eb62872bc39f",
        "U5ce6c382d12eaea28d98f2d48673b4b8",
        "U8f3cc921a9dd18d3e257008a34dd07c1",
    }
    return user_id in special_ids
