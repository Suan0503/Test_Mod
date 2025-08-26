"""
models package initializer（安全匯出常用 model）

- 使用延遲/受控匯入（try/except）可避免單一缺失造成整個 app 無法啟動。
- 若你偏好更嚴格的行為（缺檔就崩潰），可以改為直接 from .whitelist import Whitelist 等。
"""
__all__ = []

try:
    from .whitelist import Whitelist
    __all__.append("Whitelist")
except Exception:
    # 開發時建議把錯誤印出或 logging.warning，這裡暫時 silence
    pass

try:
    from .blacklist import Blacklist
    __all__.append("Blacklist")
except Exception:
    pass

try:
    from .coupon import Coupon
    __all__.append("Coupon")
except Exception:
    pass
