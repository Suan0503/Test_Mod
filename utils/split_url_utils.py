import random
from models import UserSplitUrl
from extensions import db

SPLIT_URLS = [
    "https://line.me/ti/p/g7TPO_lhAL",
    "https://line.me/ti/p/Q6-jrvhXbH",
    "https://line.me/ti/p/AKRUvSCLRC"
]

def allocate_new_split_url():
    used_urls = [r.split_url for r in UserSplitUrl.query.all()]
    for url in SPLIT_URLS:
        if url not in used_urls:
            return url
    return random.choice(SPLIT_URLS)  # 若全部都分配過就隨機給一個

def get_or_bind_split_url(user_id):
    record = UserSplitUrl.query.filter_by(user_id=user_id).first()
    if record:
        return record.split_url
    else:
        new_url = allocate_new_split_url()
        new_record = UserSplitUrl(user_id=user_id, split_url=new_url)
        db.session.add(new_record)
        db.session.commit()
        return new_url
