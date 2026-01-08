# 📚 Test_Mod 配置範例

## 🎯 功能方案配置範例

### 範例 1：基礎版配置
適合小型店家或試用客戶

```python
# 使用指令
/設定方案 basic

# 或手動設定
from utils.feature_control import create_group_features

group_id = "C1234567890abcdef..."
features = ["verify", "report", "coupon"]
token = create_group_features(group_id, features)
print(f"TOKEN: {token}")
```

**資料庫資料**：
```json
{
  "group_id": "C1234567890abcdef...",
  "token": "xK2m9Pq4rS8tU6vW0yZ3aB5cD7eF1gH4",
  "features": ["verify", "report", "coupon"],
  "is_active": true,
  "expires_at": null
}
```

### 範例 2：標準版配置（含到期日）
適合一般商家，設定 1 年授權期

```python
from datetime import datetime, timedelta
from utils.feature_control import create_group_features

group_id = "C2345678901bcdefg..."
features = ["verify", "report", "coupon", "draw", "wallet"]
expires_at = datetime.utcnow() + timedelta(days=365)  # 1 年後到期

token = create_group_features(group_id, features, expires_at=expires_at)
```

**資料庫資料**：
```json
{
  "group_id": "C2345678901bcdefg...",
  "token": "yL3n0Qr5sT9uV7wX1zA4bC6dE8fG2hI5",
  "features": ["verify", "report", "coupon", "draw", "wallet"],
  "is_active": true,
  "expires_at": "2027-01-08T00:00:00"
}
```

### 範例 3：專業版客製化配置
基於專業版，額外加入統計功能

```python
# 方式 1：先套用方案再調整
/設定方案 professional
/設定功能 statistics

# 方式 2：直接指定功能列表
from utils.feature_control import create_group_features

group_id = "C3456789012cdefgh..."
features = [
    "verify", "report", "coupon", "draw", 
    "wallet", "admin_panel", "schedule",
    "statistics"  # 額外新增
]
token = create_group_features(group_id, features)
```

### 範例 4：企業版完整配置
所有功能全開

```python
/設定方案 enterprise

# 或
from utils.feature_control import FEATURE_LIST, create_group_features

group_id = "C4567890123defghi..."
features = list(FEATURE_LIST.keys())  # 所有功能
token = create_group_features(group_id, features)
```

## 🔧 特殊場景配置

### 場景 1：試用期限制
提供 30 天試用，僅開放基礎功能

```python
from datetime import datetime, timedelta
from utils.feature_control import create_group_features

group_id = "C5678901234efghij..."
features = ["verify", "report"]  # 最基本功能
expires_at = datetime.utcnow() + timedelta(days=30)  # 30 天試用

token = create_group_features(
    group_id=group_id,
    features=features,
    expires_at=expires_at
)

# 通知客戶
message = f"""
✨ 試用版已啟動

🎯 可用功能：
  • 驗證功能
  • 回報文功能

📅 試用期限：30 天
🔑 TOKEN: {token}

試用期滿請聯繫升級正式版 🎁
"""
```

### 場景 2：季節性功能開放
特定節日開放抽獎功能

```python
from utils.feature_control import get_group_features, toggle_feature

group_id = "C6789012345fghijk..."

# 活動前開啟抽獎
toggle_feature(group_id, "draw")

# 活動結束後關閉
toggle_feature(group_id, "draw")
```

### 場景 3：階段性功能釋放
新客戶先給基礎版，滿意後升級

```python
# 第一階段：基礎版 (第 1 個月)
/設定方案 basic

# 第二階段：標準版 (第 2-6 個月)
/設定方案 standard

# 第三階段：專業版 (第 7 個月起)
/設定方案 professional
```

### 場景 4：功能組合套餐
為不同產業設計專屬套餐

```python
from utils.feature_control import create_group_features

# 美容產業套餐
beauty_features = [
    "verify",      # 會員驗證
    "schedule",    # 預約系統
    "wallet",      # 儲值錢包
    "coupon"       # 優惠券
]

# 餐飲產業套餐
restaurant_features = [
    "verify",      # 會員驗證
    "draw",        # 抽獎活動
    "wallet",      # 儲值錢包
    "ad_menu"      # 廣告專區
]

# 零售產業套餐
retail_features = [
    "verify",      # 會員驗證
    "report",      # 回報文
    "coupon",      # 優惠券
    "statistics"   # 銷售統計
]
```

## 💾 資料庫直接操作

### 查詢群組設定
```sql
-- 查看所有群組設定
SELECT 
    group_id, 
    token, 
    features, 
    is_active,
    expires_at,
    created_at 
FROM group_feature_setting 
WHERE is_active = true;

-- 查看即將到期的授權 (30 天內)
SELECT 
    group_id, 
    expires_at,
    DATEDIFF(expires_at, NOW()) as days_left
FROM group_feature_setting 
WHERE expires_at IS NOT NULL 
  AND expires_at < DATE_ADD(NOW(), INTERVAL 30 DAY)
ORDER BY expires_at;
```

### 批次更新功能
```sql
-- 為所有群組新增廣告專區功能
UPDATE group_feature_setting 
SET features = JSON_ARRAY_APPEND(features, '$', 'ad_menu'),
    updated_at = NOW()
WHERE NOT JSON_CONTAINS(features, '"ad_menu"');

-- 延長所有授權 3 個月
UPDATE group_feature_setting 
SET expires_at = DATE_ADD(expires_at, INTERVAL 3 MONTH),
    updated_at = NOW()
WHERE expires_at IS NOT NULL;
```

### 統計查詢
```sql
-- 功能使用統計 (本月)
SELECT 
    feature_key,
    COUNT(*) as usage_count,
    COUNT(DISTINCT user_id) as unique_users
FROM feature_usage_log
WHERE created_at >= DATE_FORMAT(NOW(), '%Y-%m-01')
GROUP BY feature_key
ORDER BY usage_count DESC;

-- 最活躍的群組 (本週)
SELECT 
    group_id,
    COUNT(*) as total_actions,
    COUNT(DISTINCT feature_key) as features_used
FROM feature_usage_log
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY group_id
ORDER BY total_actions DESC
LIMIT 10;
```

## 🔄 遷移與備份

### 匯出群組設定
```python
from models import GroupFeatureSetting
import json

def export_group_settings(output_file="group_settings_backup.json"):
    """匯出所有群組設定"""
    settings = GroupFeatureSetting.query.all()
    
    data = []
    for s in settings:
        data.append({
            "group_id": s.group_id,
            "token": s.token,
            "features": json.loads(s.features),
            "expires_at": s.expires_at.isoformat() if s.expires_at else None,
            "is_active": s.is_active
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已匯出 {len(data)} 筆設定到 {output_file}")
```

### 匯入群組設定
```python
from models import GroupFeatureSetting
from extensions import db
import json

def import_group_settings(input_file="group_settings_backup.json"):
    """匯入群組設定"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for item in data:
        existing = GroupFeatureSetting.query.filter_by(
            group_id=item['group_id']
        ).first()
        
        if existing:
            # 更新現有設定
            existing.token = item['token']
            existing.features = json.dumps(item['features'])
            existing.is_active = item['is_active']
            if item['expires_at']:
                existing.expires_at = datetime.fromisoformat(item['expires_at'])
        else:
            # 建立新設定
            setting = GroupFeatureSetting(
                group_id=item['group_id'],
                token=item['token'],
                features=json.dumps(item['features']),
                is_active=item['is_active'],
                expires_at=datetime.fromisoformat(item['expires_at']) if item['expires_at'] else None
            )
            db.session.add(setting)
    
    db.session.commit()
    print(f"✅ 已匯入 {len(data)} 筆設定")
```

## 📊 初始化腳本

### 一鍵設定多個測試群組
```python
from utils.feature_control import set_group_plan

# 測試群組列表
test_groups = {
    "C1111111111111111": "basic",
    "C2222222222222222": "standard",
    "C3333333333333333": "professional",
    "C4444444444444444": "enterprise"
}

for group_id, plan in test_groups.items():
    success, token, message = set_group_plan(group_id, plan)
    if success:
        print(f"✅ {group_id}: {plan} - TOKEN: {token}")
    else:
        print(f"❌ {group_id}: {message}")
```

---

**提示**：以上配置範例可根據實際需求調整，建議在測試環境先行驗證後再套用到正式環境。
