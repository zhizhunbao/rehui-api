import logging
import os
from datetime import datetime

from utils.path_utils import get_abs_path

def _setup_logger(logger_name: str, log_file: str, level=logging.INFO):
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt='[%(asctime)s] %(levelname)s | %(filename)s | %(funcName)s | %(message)s',
            datefmt='%H:%M:%S'
        )

        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

def setup_daily_logger(logger_name: str = None, date_str: str = None, log_dir: str = 'logs'):
    """
    快速生成按日期命名的 logger，避免重复配置。
    - logger_name 默认为模块名（__name__）
    - date_str 默认为今天日期（YYYYMMDD）
    - log_dir 为 logs 目录（相对项目根）
    """
    logger_name = logger_name or __name__
    date_str = date_str or datetime.now().strftime('%Y%m%d')
    log_file = get_abs_path(log_dir, f"{logger_name}_{date_str}.log")
    return _setup_logger(logger_name=logger_name, log_file=log_file)


if __name__ == "__main__":
    logger = setup_daily_logger("test_logger")

    logger.debug("This is a DEBUG message.")
    logger.info("This is an INFO message.")
    logger.warning("This is a WARNING message.")
    logger.error("This is an ERROR message.")
    logger.critical("This is a CRITICAL message.")
