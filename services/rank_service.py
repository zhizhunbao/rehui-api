from services.base_service import BaseService
from utils.db_utils import run_query_df


class RankService(BaseService):
    """
    榜单服务：从 dws_rehui_rank_cargurus 表中获取 rehui_score 排名前 N 的车辆
    """

    def get_top_rank(self, limit: int = 5, city: str = None, make: str = None) -> dict:
        trace_id = self.get_trace_id()
        limit = self.validate_limit(limit)

        sql = """
              SELECT listing_id, title, make, model, trim, year, city, rehui_score
              FROM dws_rehui_rank_cargurus
              WHERE 1=1 \
              """
        params = {}

        if city:
            sql += " AND city = :city"
            params["city"] = city
        if make:
            sql += " AND make = :make"
            params["make"] = make

        sql += " ORDER BY rehui_score DESC LIMIT :limit"
        params["limit"] = limit

        try:
            self.logger.info(f"[{trace_id}] 📊 查询榜单 city={city}, make={make}, limit={limit}")
            df = run_query_df(self.engine, sql, params, logger=self.logger)
            self.logger.info(f"[{trace_id}] ✅ 查询成功，返回 {len(df)} 条")
            return self.success(df.to_dict(orient="records"))

        except Exception as e:
            self.logger.error(f"[{trace_id}] ❌ 查询失败: {e}", exc_info=True)
            return self.error("查询失败，请稍后再试", code=500)
