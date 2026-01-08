# -*- coding: utf-8 -*-
"""
管理員指令處理器 - 功能控制相關
"""
from linebot.models import TextSendMessage
from extensions import line_bot_api, db
from storage import ADMIN_IDS
from utils.feature_control import (
    get_group_status, 
    toggle_feature, 
    regenerate_group_token,
    set_group_plan,
    FEATURE_LIST,
    FEATURE_CATEGORIES
)
import json


def handle_admin_commands(event):
    """處理管理員指令"""
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    
    # 只有管理員可以執行
    if user_id not in ADMIN_IDS:
        return False
    
    # 取得群組 ID（若在群組中）
    group_id = None
    if hasattr(event.source, 'group_id'):
        group_id = event.source.group_id
    
    # /功能設定 - 查看當前功能狀態
    if user_text in ["/功能設定", "/features"]:
        if not group_id:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ 此指令僅可在群組中使用")
            )
            return True
        
        status = get_group_status(group_id)
        
        if not status["has_config"]:
            reply = (
                "📊 群組功能狀態\n\n"
                "🎯 當前狀態：未設定（預設全功能）\n"
                "✨ 可用功能：全部功能\n\n"
                "💡 使用「/設定方案 <方案名>」來設定功能方案\n"
                "方案選項：basic, standard, professional, enterprise"
            )
        else:
            features_text = "\n".join([f"  ✅ {FEATURE_LIST.get(f, f)}" for f in status["features"]])
            disabled_features = [f for f in FEATURE_LIST.keys() if f not in status["features"]]
            disabled_text = "\n".join([f"  ❌ {FEATURE_LIST.get(f, f)}" for f in disabled_features]) if disabled_features else "  無"
            
            expires_text = status["expires_at"].strftime("%Y/%m/%d") if status["expires_at"] else "無限期"
            
            reply = (
                f"📊 群組功能狀態\n\n"
                f"🔑 TOKEN: {status['token']}\n"
                f"📅 授權到期: {expires_text}\n"
                f"🔄 更新時間: {status['updated_at'].strftime('%Y/%m/%d %H:%M')}\n\n"
                f"✨ 啟用功能:\n{features_text}\n\n"
                f"🚫 停用功能:\n{disabled_text}\n\n"
                f"💡 使用「/設定功能 <功能代碼>」切換功能開關"
            )
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return True
    
    # /設定功能 <feature_key> - 切換功能開關
    if user_text.startswith("/設定功能 ") or user_text.startswith("/toggle "):
        if not group_id:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ 此指令僅可在群組中使用")
            )
            return True
        
        parts = user_text.split(" ", 1)
        if len(parts) < 2:
            feature_list = "\n".join([f"  • {k}: {v}" for k, v in FEATURE_LIST.items()])
            reply = f"📋 可用功能列表:\n\n{feature_list}\n\n💡 使用方式: /設定功能 <功能代碼>"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            return True
        
        feature_key = parts[1].strip()
        success, new_status, message = toggle_feature(group_id, feature_key)
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        return True
    
    # /生成token - 重新生成 TOKEN
    if user_text in ["/生成token", "/generate_token"]:
        if not group_id:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ 此指令僅可在群組中使用")
            )
            return True
        
        new_token = regenerate_group_token(group_id)
        
        if new_token:
            reply = f"✅ 已生成新的 TOKEN\n\n🔑 {new_token}\n\n⚠️ 請妥善保管此 TOKEN"
        else:
            # 如果群組還沒有設定，先建立
            from utils.feature_control import create_group_features
            new_token = create_group_features(group_id, list(FEATURE_LIST.keys()))
            reply = f"✅ 已建立群組設定並生成 TOKEN\n\n🔑 {new_token}\n\n⚠️ 請妥善保管此 TOKEN"
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return True
    
    # /設定方案 <plan_name> - 設定功能方案
    if user_text.startswith("/設定方案 ") or user_text.startswith("/set_plan "):
        if not group_id:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ 此指令僅可在群組中使用")
            )
            return True
        
        parts = user_text.split(" ", 1)
        if len(parts) < 2:
            plans_text = (
                "📦 可用方案:\n\n"
                "🔹 basic (基礎版)\n"
                f"   {', '.join([FEATURE_LIST[f] for f in FEATURE_CATEGORIES['basic']])}\n\n"
                "🔸 standard (標準版)\n"
                f"   {', '.join([FEATURE_LIST[f] for f in FEATURE_CATEGORIES['standard']])}\n\n"
                "🔶 professional (專業版)\n"
                f"   {', '.join([FEATURE_LIST[f] for f in FEATURE_CATEGORIES['professional']])}\n\n"
                "⭐ enterprise (企業版)\n"
                "   全部功能\n\n"
                "💡 使用方式: /設定方案 <方案名>"
            )
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=plans_text))
            return True
        
        plan_name = parts[1].strip().lower()
        success, token, message = set_group_plan(group_id, plan_name)
        
        if success:
            message += f"\n\n🔑 TOKEN: {token}"
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        return True
    
    # /msg <user_id> <message> - 發送訊息給用戶（原有功能）
    if user_text.startswith("/msg "):
        try:
            parts = user_text.split(" ", 2)
            if len(parts) < 3:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="格式錯誤，請用 /msg <user_id> <內容>")
                )
                return True
            
            target_user_id = parts[1].strip()
            msg = parts[2].strip()
            
            line_bot_api.push_message(
                target_user_id,
                TextSendMessage(text=f"【管理員回覆】\n{msg}")
            )
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="✅ 已發送訊息給用戶")
            )
        except Exception as e:
            print("管理員私訊失敗：", e)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ 發送失敗，請檢查 user_id 是否正確")
            )
        return True
    
    return False
