#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test_Mod 販售版初始化腳本
用於首次部署時快速設定系統
"""

import os
import sys
from datetime import datetime, timedelta

# 確保可以匯入專案模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """初始化資料庫"""
    print("\n" + "="*50)
    print("📊 步驟 1: 初始化資料庫")
    print("="*50)
    
    try:
        from app import app, db
        with app.app_context():
            # 檢查資料庫連線
            db.engine.connect()
            print("✅ 資料庫連線成功")
            
            # 建立所有資料表
            db.create_all()
            print("✅ 資料表建立完成")
            
        return True
    except Exception as e:
        print(f"❌ 資料庫初始化失敗: {e}")
        return False


def init_commands():
    """初始化指令配置"""
    print("\n" + "="*50)
    print("🎯 步驟 2: 初始化指令配置")
    print("="*50)
    
    try:
        from app import app
        from utils.feature_control import init_command_config
        
        with app.app_context():
            if init_command_config():
                print("✅ 指令配置初始化完成")
                return True
            else:
                print("⚠️  指令配置可能已存在或初始化失敗")
                return True  # 不視為嚴重錯誤
    except Exception as e:
        print(f"❌ 指令配置初始化失敗: {e}")
        return False


def create_test_groups():
    """建立測試群組設定（可選）"""
    print("\n" + "="*50)
    print("🧪 步驟 3: 建立測試群組設定（可選）")
    print("="*50)
    
    response = input("是否建立測試群組設定？(y/N): ").strip().lower()
    
    if response != 'y':
        print("⏭️  跳過測試群組設定")
        return True
    
    try:
        from app import app
        from utils.feature_control import set_group_plan
        
        test_groups = {
            "TEST_BASIC_GROUP": "basic",
            "TEST_STANDARD_GROUP": "standard",
            "TEST_PROFESSIONAL_GROUP": "professional",
            "TEST_ENTERPRISE_GROUP": "enterprise"
        }
        
        with app.app_context():
            print("\n建立測試群組...")
            for group_id, plan in test_groups.items():
                success, token, message = set_group_plan(group_id, plan)
                if success:
                    print(f"✅ {group_id} ({plan})")
                    print(f"   TOKEN: {token}")
                else:
                    print(f"❌ {group_id}: {message}")
            
        return True
    except Exception as e:
        print(f"❌ 建立測試群組失敗: {e}")
        return False


def check_environment():
    """檢查環境變數"""
    print("\n" + "="*50)
    print("🔍 步驟 0: 檢查環境設定")
    print("="*50)
    
    required_vars = [
        "DATABASE_URL",
        "CHANNEL_ACCESS_TOKEN",
        "CHANNEL_SECRET",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"❌ 缺少環境變數: {var}")
        else:
            # 顯示部分內容確認
            value = os.getenv(var)
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        print(f"\n⚠️  請在 .env 檔案中設定以下環境變數:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    return True


def setup_admin_ids():
    """設定管理員 ID"""
    print("\n" + "="*50)
    print("👤 步驟 4: 設定管理員 ID")
    print("="*50)
    
    try:
        # 檢查 storage.py 是否已設定
        from storage import ADMIN_IDS
        
        if ADMIN_IDS and len(ADMIN_IDS) > 0:
            print(f"✅ 已設定 {len(ADMIN_IDS)} 位管理員")
            for admin_id in ADMIN_IDS:
                masked_id = admin_id[:10] + "..." if len(admin_id) > 10 else admin_id
                print(f"   - {masked_id}")
            return True
        else:
            print("⚠️  storage.py 中的 ADMIN_IDS 為空")
            print("請編輯 storage.py 加入管理員的 LINE User ID")
            return False
            
    except Exception as e:
        print(f"❌ 讀取管理員設定失敗: {e}")
        return False


def show_summary():
    """顯示總結資訊"""
    print("\n" + "="*50)
    print("🎉 初始化完成！")
    print("="*50)
    
    print("\n📋 後續步驟:")
    print("1. 啟動服務:")
    print("   python app.py")
    print("\n2. 設定 LINE Webhook URL:")
    print("   https://your-domain.com/callback")
    print("\n3. 測試 Bot 功能:")
    print("   - 加入 Bot 為好友")
    print("   - 建立測試群組並邀請 Bot")
    print("   - 在群組中執行 /功能設定")
    print("\n4. 參考文件:")
    print("   - QUICK_START.md - 快速開始指南")
    print("   - FEATURE_CONTROL_GUIDE.md - 功能控制指南")
    print("   - DEPLOYMENT_CHECKLIST.md - 部署檢查清單")
    print("\n" + "="*50)


def main():
    """主程式"""
    print("\n" + "="*60)
    print("🚀 Test_Mod 販售版初始化程式 v2.0")
    print("="*60)
    print("\n本程式將協助您完成首次部署的初始化設定")
    print("請確保已完成以下準備工作:")
    print("  1. 已安裝所有依賴套件 (pip install -r requirements.txt)")
    print("  2. 已建立 .env 檔案並設定必要的環境變數")
    print("  3. 資料庫服務正在運行")
    
    response = input("\n是否繼續？(Y/n): ").strip().lower()
    if response == 'n':
        print("初始化已取消")
        return
    
    # 步驟 0: 檢查環境
    if not check_environment():
        print("\n❌ 環境檢查失敗，請先完成環境設定")
        sys.exit(1)
    
    # 步驟 1: 初始化資料庫
    if not init_database():
        print("\n❌ 資料庫初始化失敗")
        sys.exit(1)
    
    # 步驟 2: 初始化指令配置
    if not init_commands():
        print("\n❌ 指令配置初始化失敗")
        sys.exit(1)
    
    # 步驟 3: 建立測試群組（可選）
    create_test_groups()
    
    # 步驟 4: 檢查管理員設定
    if not setup_admin_ids():
        print("\n⚠️  請記得設定管理員 ID")
    
    # 顯示總結
    show_summary()
    
    print("\n✅ 初始化程式執行完成！")
    print("祝您使用愉快！🎉\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  初始化已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
