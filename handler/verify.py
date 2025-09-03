from typing import Optional, Dict, Any


def build_student_card_flex(
	phone: str,
	nickname: str,
	number: str,
	lineid: str,
	join_code: str,
	time_str: str,
	avatar_url: Optional[str] = None,
) -> Dict[str, Any]:
	# 簡化版：提供欄位，維持 API 相容
	avatar = avatar_url or "https://i.imgur.com/8Km9tLL.png"
	return {
		"type": "bubble",
		"hero": {
			"type": "image",
			"url": avatar,
			"size": "full",
			"aspectRatio": "20:9",
			"aspectMode": "cover"
		},
		"body": {
			"type": "box",
			"layout": "vertical",
			"contents": [
				{"type": "text", "text": f"{nickname} 同學", "weight": "bold", "size": "xl"},
				{"type": "text", "text": f"學號: {number}", "size": "sm", "color": "#555555"},
				{"type": "text", "text": f"手機: {phone}", "size": "sm", "color": "#555555"},
				{"type": "text", "text": f"LINE ID: {lineid}", "size": "sm", "color": "#555555"},
				{"type": "text", "text": f"加入碼: {join_code}", "size": "sm", "color": "#555555"},
				{"type": "text", "text": f"時間: {time_str}", "size": "sm", "color": "#888888"},
			]
		}
	}
