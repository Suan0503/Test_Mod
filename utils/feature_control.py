# -*- coding: utf-8 -*-
"""
功能控制系統 - 販售版本功能管理
參考 FanFan 專案的 feature_switches 架構
"""
import json
import secrets
from datetime import datetime
from typing import List, Optional, Dict
from extensions import db
from models import GroupFeatureSetting, CommandConfig, FeatureUsageLog

# 定義所有可用功能
FEATURE_LIST = {
    "verify": "驗證功能",
    "report": "回報文功能",
    "coupon": "抽獎券功能",
    "draw": "每日抽獎",
    "wallet": "儲值錢包",
    "admin_panel": "管理面板",
    "schedule": "預約系統",
    "wage": "薪資管理",
    "manual_verify": "手動驗證",
    "statistics": "統計功能",
    "ad_menu": "廣告專區"
}

# 預設管理員功能（可根據需求調整）
DEFAULT_ADMIN_FEATURES = list(FEATURE_LIST.keys())

# 功能分類
FEATURE_CATEGORIES = {
    "basic": ["verify", "report", "coupon"],  # 基礎版
    "standard": ["verify", "report", "coupon", "draw", "wallet"],  # 標準版
    "professional": ["verify", "report", "coupon", "draw", "wallet", "admin_panel", "schedule"],  # 專業版
    "enterprise": list(FEATURE_LIST.keys())  # 企業版（全功能）
}


def generate_group_token() -> str:
    """生成唯一的群組 TOKEN"""
    return secrets.token_urlsafe(16)


def create_group_features(group_id: str, features: List[str], token: str = None, expires_at: datetime = None) -> str:
    """
    為群組建立功能設定
    
    Args:
        group_id: LINE 群組 ID
        features: 功能列表
        token: 自訂 TOKEN（若無則自動生成）
        expires_at: 授權到期日（可選）
    
    Returns:
        群組 TOKEN
    """
    if not token:
        token = generate_group_token()
    
    # 檢查是否已存在
    existing = GroupFeatureSetting.query.filter_by(group_id=group_id).first()
    
    if existing:
        # 更新現有設定
        existing.features = json.dumps(features, ensure_ascii=False)
        existing.token = token
        existing.updated_at = datetime.utcnow()
        if expires_at:
            existing.expires_at = expires_at
    else:
        # 建立新設定
        setting = GroupFeatureSetting(
            group_id=group_id,
            token=token,
            features=json.dumps(features, ensure_ascii=False),
            expires_at=expires_at
        )
        db.session.add(setting)
    
    try:
        db.session.commit()
        return token
    except Exception as e:
        db.session.rollback()
        raise e


def get_group_features(group_id: str) -> List[str]:
    """
    取得群組可用的功能列表
    
    Args:
        group_id: LINE 群組 ID
    
    Returns:
        功能列表，若未設定則返回所有功能（預設行為）
    """
    setting = GroupFeatureSetting.query.filter_by(group_id=group_id, is_active=True).first()
    
    if not setting:
        # 預設給予所有功能
        return list(FEATURE_LIST.keys())
    
    # 檢查是否過期
    if setting.expires_at and setting.expires_at < datetime.utcnow():
        return []  # 過期則不提供任何功能
    
    try:
        features = json.loads(setting.features)
        return features if isinstance(features, list) else []
    except:
        return []


def check_feature_enabled(group_id: str, feature_key: str) -> bool:
    """
    檢查群組是否啟用某項功能
    
    Args:
        group_id: LINE 群組 ID
        feature_key: 功能鍵值
    
    Returns:
        是否啟用
    """
    enabled_features = get_group_features(group_id)
    return feature_key in enabled_features


def toggle_feature(group_id: str, feature_key: str) -> tuple:
    """
    切換群組功能開關
    
    Args:
        group_id: LINE 群組 ID
        feature_key: 功能鍵值
    
    Returns:
        (是否成功, 當前狀態, 訊息)
    """
    if feature_key not in FEATURE_LIST:
        return False, False, f"❌ 未知功能: {feature_key}"
    
    setting = GroupFeatureSetting.query.filter_by(group_id=group_id).first()
    
    if not setting:
        # 首次設定，預設開啟所有功能，然後關閉指定功能
        features = list(FEATURE_LIST.keys())
        features.remove(feature_key)
        token = create_group_features(group_id, features)
        return True, False, f"✅ 已關閉「{FEATURE_LIST[feature_key]}」\n🔑 TOKEN: {token}"
    
    try:
        features = json.loads(setting.features)
    except:
        features = []
    
    if feature_key in features:
        # 關閉功能
        features.remove(feature_key)
        new_status = False
        status_text = "關閉"
    else:
        # 開啟功能
        features.append(feature_key)
        new_status = True
        status_text = "開啟"
    
    setting.features = json.dumps(features, ensure_ascii=False)
    setting.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return True, new_status, f"✅ 已{status_text}「{FEATURE_LIST[feature_key]}」"
    except Exception as e:
        db.session.rollback()
        return False, new_status, f"❌ 操作失敗: {str(e)}"


def get_group_token(group_id: str) -> Optional[str]:
    """取得群組的 TOKEN"""
    setting = GroupFeatureSetting.query.filter_by(group_id=group_id).first()
    return setting.token if setting else None


def regenerate_group_token(group_id: str) -> Optional[str]:
    """重新生成群組 TOKEN"""
    setting = GroupFeatureSetting.query.filter_by(group_id=group_id).first()
    
    if not setting:
        return None
    
    new_token = generate_group_token()
    setting.token = new_token
    setting.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return new_token
    except:
        db.session.rollback()
        return None


def get_group_status(group_id: str) -> Dict:
    """
    取得群組功能狀態摘要
    
    Returns:
        包含功能列表、TOKEN、到期日等資訊的字典
    """
    setting = GroupFeatureSetting.query.filter_by(group_id=group_id).first()
    
    if not setting:
        return {
            "has_config": False,
            "features": list(FEATURE_LIST.keys()),
            "token": None,
            "expires_at": None,
            "is_active": True
        }
    
    try:
        features = json.loads(setting.features)
    except:
        features = []
    
    return {
        "has_config": True,
        "features": features,
        "token": setting.token,
        "expires_at": setting.expires_at,
        "is_active": setting.is_active,
        "created_at": setting.created_at,
        "updated_at": setting.updated_at
    }


def log_feature_usage(group_id: str, user_id: str, feature_key: str, command_used: str = None):
    """記錄功能使用日誌"""
    try:
        log = FeatureUsageLog(
            group_id=group_id,
            user_id=user_id,
            feature_key=feature_key,
            command_used=command_used
        )
        db.session.add(log)
        db.session.commit()
    except:
        db.session.rollback()


def set_group_plan(group_id: str, plan_name: str) -> tuple:
    """
    為群組設定方案
    
    Args:
        group_id: 群組 ID
        plan_name: 方案名稱 (basic/standard/professional/enterprise)
    
    Returns:
        (是否成功, TOKEN, 訊息)
    """
    if plan_name not in FEATURE_CATEGORIES:
        return False, None, f"❌ 未知方案: {plan_name}"
    
    features = FEATURE_CATEGORIES[plan_name]
    
    try:
        token = create_group_features(group_id, features)
        plan_names = {
            "basic": "基礎版",
            "standard": "標準版",
            "professional": "專業版",
            "enterprise": "企業版"
        }
        return True, token, f"✅ 已設定為「{plan_names[plan_name]}」方案"
    except Exception as e:
        return False, None, f"❌ 設定失敗: {str(e)}"


# ===== 指令配置管理 =====

def init_command_config():
    """初始化指令配置（首次部署時執行）"""
    default_commands = [
        # 驗證功能
        {"command_key": "verify_info", "command_zh": "驗證資訊", "command_en": "verify", "feature_category": "verify", "description": "查詢驗證資訊", "is_admin_only": False},
        
        # 回報文功能
        {"command_key": "report", "command_zh": "回報文", "command_en": "report", "feature_category": "report", "description": "提交回報文", "is_admin_only": False},
        
        # 抽獎功能
        {"command_key": "draw", "command_zh": "每日抽獎", "command_en": "draw", "feature_category": "draw", "description": "每日抽獎功能", "is_admin_only": False},
        {"command_key": "my_coupons", "command_zh": "我的抽獎券", "command_en": "my_coupons", "feature_category": "coupon", "description": "查詢抽獎券", "is_admin_only": False},
        
        # 錢包功能
        {"command_key": "wallet", "command_zh": "我的錢包", "command_en": "wallet", "feature_category": "wallet", "description": "查詢儲值錢包", "is_admin_only": False},
        
        # 管理功能
        {"command_key": "admin_panel", "command_zh": "管理面板", "command_en": "admin", "feature_category": "admin_panel", "description": "開啟管理面板", "is_admin_only": True},
        {"command_key": "send_message", "command_zh": "/msg", "command_en": "/msg", "feature_category": "admin_panel", "description": "管理員發送訊息", "is_admin_only": True},
        
        # 功能控制（主人專用）
        {"command_key": "feature_status", "command_zh": "/功能設定", "command_en": "/features", "feature_category": "admin_panel", "description": "查看功能設定", "is_admin_only": True},
        {"command_key": "toggle_feature", "command_zh": "/設定功能", "command_en": "/toggle", "feature_category": "admin_panel", "description": "切換功能開關", "is_admin_only": True},
        {"command_key": "generate_token", "command_zh": "/生成token", "command_en": "/generate_token", "feature_category": "admin_panel", "description": "生成群組TOKEN", "is_admin_only": True},
        {"command_key": "set_plan", "command_zh": "/設定方案", "command_en": "/set_plan", "feature_category": "admin_panel", "description": "設定群組方案", "is_admin_only": True},
        
        # 廣告專區
        {"command_key": "ad_menu", "command_zh": "廣告專區", "command_en": "ad", "feature_category": "ad_menu", "description": "廣告專區入口", "is_admin_only": False},
    ]
    
    try:
        for cmd in default_commands:
            existing = CommandConfig.query.filter_by(command_key=cmd["command_key"]).first()
            if not existing:
                config = CommandConfig(**cmd)
                db.session.add(config)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"初始化指令配置失敗: {e}")
        return False


def get_command_by_text(text: str) -> Optional[CommandConfig]:
    """根據文字內容查詢指令配置"""
    return CommandConfig.query.filter(
        (CommandConfig.command_zh == text) | (CommandConfig.command_en == text)
    ).first()
