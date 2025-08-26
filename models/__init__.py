"""
models package initializer (安全匯出)

- 這個檔案會盡量以延遲匯入（try/except）方式匯出常用 model，
  避免在某些情況下造成整個應用因某個 model 缺失而啟動失敗。
- 若你偏好主動且明確的匯入，之後可以把 try/except 改為直接 from .whitelist import Whitelist 等。
"""
__all__ = []

# 這邊採用 try/except，不會在無對應檔案時直接崩潰
try:
    from .whitelist import Whitelist
    __all__.append("Whitelist")
except Exception:
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
