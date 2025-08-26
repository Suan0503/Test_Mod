"""
models package initializer（安全匯出常用 model 與 db）

- 將 extensions.db 匯出成 models.db，修正舊程式碼使用 `from models import ..., db` 的行為。
- 同時嘗試匯入常用的 model，如果缺檔不會立刻 crash（開發時可考慮改為直接匯入來揭露錯誤）。
"""
from extensions import db  # 將 extensions.db 暴露為 models.db

__all__ = ["db"]

# 嘗試匯入各 model，並將名稱加入 __all__
# 如果有需要你可以移除 try/except 以利開發時暴露問題
try:
    from .whitelist import Whitelist
    __all__.append("Whitelist")
except Exception:
    # 開發時可改為 logging.exception(...) 以觀察錯誤
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
