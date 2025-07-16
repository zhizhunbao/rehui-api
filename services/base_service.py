import os
import uuid
from dotenv import load_dotenv
from sqlalchemy.engine import Engine

from utils.db_utils import get_sqlalchemy_engine
from utils.logger import setup_daily_logger

class BaseService:
    """
    通用 Service 基类：
    - 自动注入 engine / logger
    - 提供分页、limit 校验、异常封装、统一返回结构
    """

    def __init__(self):
        self.logger = self._init_logger()
        self.engine = self._init_engine()

    def _init_logger(self):
        return setup_daily_logger(self.__class__.__name__)

    def _init_engine(self) -> Engine:
        load_dotenv()
        self.logger.info("🔌 初始化数据库连接 ...")
        return get_sqlalchemy_engine(
            host=os.getenv("RENDER_DB_HOST"),
            port=int(os.getenv("RENDER_DB_PORT", 5432)),
            db=os.getenv("RENDER_DB_NAME"),
            user=os.getenv("RENDER_DB_USER"),
            password=os.getenv("RENDER_DB_PASSWORD"),
        )

    # ✅ 通用工具方法
    def paginate(self, rows: list, page: int, size: int) -> list:
        return rows[(page - 1) * size : page * size]

    def validate_limit(self, limit: int, max_limit: int = 50) -> int:
        return min(max(1, limit), max_limit)

    def get_trace_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def require(self, field: str, value, message: str = None):
        if value is None:
            raise ValueError(message or f"Missing required: {field}")

    # ✅ 安全执行包装
    def safe_execute(self, func, *args, **kwargs):
        trace_id = self.get_trace_id()
        try:
            self.logger.info(f"[{trace_id}] ✅ 执行函数: {func.__name__}")
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"[{trace_id}] ❌ 异常: {e}", exc_info=True)
            return self.error(f"服务内部异常：{str(e)}", code=500)

    # ✅ 标准响应结构
    def success(self, data=None, message="success"):
        return {"code": 0, "message": message, "data": data}

    def error(self, message="error", code=1):
        return {"code": code, "message": message, "data": None}
