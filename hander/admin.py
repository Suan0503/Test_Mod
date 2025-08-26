"""
管理員私訊處理器 (handle_admin)
- 功能：允許在 LINE 聊天中，管理員使用 /msg <user_id> <內容> 指令對指定用戶發送私訊
- 使用範例：管理員傳送 "/msg U1234567890 你好，這是管理員訊息" -> bot 會 push 訊息給 U1234567890，並回覆管理員「已發送訊息給用戶」
- 注意：
  - 需要在 storage.ADMIN_IDS 中設定管理員 user_id 列表
  - 只在可取得 event.source.user_id 時判定是否為管理員（群組/聊天室訊息可能沒有 user_id）
  - push_message 需要 bot 的 channel 有權限對該 user_id 推播（對方需曾與 bot 一次互動）
"""
from linebot.models import TextSendMessage
from extensions import line_bot_api
from storage import ADMIN_IDS

def handle_admin(event):
    # 取得發送指令的使用者 id（在個人聊天可取得；群組或多方聊天室中可能不存在）
    user_id = getattr(event.source, "user_id", None)
    # 取得使用者輸入的文字並去除前後空白
    user_text = event.message.text.strip()

    # 1) 判斷是否為管理員，且訊息以 /msg 開頭
    #    - user_id 可能為 None（例如群組/聊天室）因此先確保 user_id 存在再做比對
    #    - ADMIN_IDS 應該是一個包含允許管理員 user_id 的可查詢結構 (list 或 set)
    if user_id in ADMIN_IDS and user_text.startswith("/msg "):
        try:
            # 2) 解析指令：以最多三段切割，格式為 "/msg", "<target_user_id>", "<內容...>"
            #    使用 split(" ", 2) 可以保留內容段中的空格
            parts = user_text.split(" ", 2)

            # 若切割後長度不足 3，代表格式錯誤（缺少 target 或內容）
            if len(parts) < 3:
                # 回覆管理員錯誤格式提示（使用 reply_message 回覆原事件）
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="格式錯誤，請用 /msg <user_id> <內容>")
                )
                return

            # 解析出目標 user id 與訊息內容
            target_user_id = parts[1].strip()
            msg = parts[2].strip()

            # 3) 使用 push_message 將訊息直接發送給指定 user（非回覆）
            #    注意：push_message 與 reply_message 的行為不同，push 不需要 reply_token
            #    但要確保 bot 有權限對該 user_id 發訊息（對方需與 bot 有互動紀錄）
            line_bot_api.push_message(
                target_user_id,
                TextSendMessage(text=f"【管理員回覆】\n{msg}")
            )

            # 4) 回覆管理員，告知已發送
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="已發送訊息給用戶")
            )

        except Exception as e:
            # 5) 發送失敗時處理
            #    - 印出錯誤到 stdout（可以改為 logging.exception(...)）
            #    - 回覆管理員發送失敗訊息（不要在回覆中包含敏感錯誤細節）
            print("管理員私訊失敗：", e)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="發送失敗，請檢查 user_id 是否正確")
            )
        # 結束處理（若為管理員 /msg 指令，處理完畢後直接 return）
        return
    # 非管理員或非 /msg 指令時，不在此處處理（呼叫端可繼續後續處理流程）
