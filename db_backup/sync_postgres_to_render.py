import os
import sys
import subprocess
import platform
import zipfile
import requests
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# === 基本配置 ===
TOOLS_DIR = Path("db_backup/postgres_tools")
ZIP_PATH = TOOLS_DIR / "pg_tools.zip"
PG_URL = "https://get.enterprisedb.com/postgresql/postgresql-16.3-1-windows-x64-binaries.zip"
TABLE_NAME = "dws_rehui_rank_cargurus"
DUMP_FILE = f"{TABLE_NAME}.sql"
ENV_PATH = Path("config/.env")  # ✅ 环境变量文件

# === 工具函数 ===

def run_cmd(command):
    print(f"🚀 执行命令:\n{command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("❌ 命令执行失败")
        sys.exit(1)

def get_env_var(key: str) -> str:
    value = os.getenv(key)
    if not value:
        print(f"❌ 缺失环境变量：{key}")
        sys.exit(1)
    return value

def download_pg_tools():
    print("⬇️ 下载 PostgreSQL CLI 工具 ...")
    TOOLS_DIR.mkdir(exist_ok=True)
    with requests.get(PG_URL, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(ZIP_PATH, 'wb') as f, tqdm(desc="下载中", total=total, unit='B', unit_scale=True) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

    print("📦 解压工具中 ...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(TOOLS_DIR)
    print("✅ 解压完成")

def get_pg_tool_path(tool: str) -> str:
    if platform.system() != "Windows":
        return tool  # mac / linux 默认使用系统命令

    tool_path = TOOLS_DIR / "pgsql" / "bin" / f"{tool}.exe"
    if not tool_path.exists():
        print(f"⚠️ 未找到 {tool}.exe，准备下载 ...")
        download_pg_tools()

    if not tool_path.exists():
        print(f"❌ 仍未找到 {tool}.exe，终止")
        sys.exit(1)
    return str(tool_path)

# === 导出导入 ===

def export_table():
    print(f"📤 导出本地表: {TABLE_NAME}")
    os.environ["PGPASSWORD"] = get_env_var("LOCAL_DB_PASSWORD")
    pg_dump = get_pg_tool_path("pg_dump")

    cmd = (
        f'"{pg_dump}" -w '
        f'-h {get_env_var("LOCAL_DB_HOST")} '
        f'-p {get_env_var("LOCAL_DB_PORT")} '
        f'-U {get_env_var("LOCAL_DB_USER")} '
        f'-d {get_env_var("LOCAL_DB_NAME")} '
        f'-t {TABLE_NAME} > {DUMP_FILE}'
    )
    run_cmd(cmd)
    print(f"✅ 表导出成功 → {DUMP_FILE}")

def import_table():
    print(f"📥 导入 Render 表: {TABLE_NAME}")
    os.environ["PGPASSWORD"] = get_env_var("RENDER_DB_PASSWORD")
    psql = get_pg_tool_path("psql")

    cmd = (
        f'"{psql}" -w '
        f'-h {get_env_var("RENDER_DB_HOST")} '
        f'-p {get_env_var("RENDER_DB_PORT")} '
        f'-U {get_env_var("RENDER_DB_USER")} '
        f'-d {get_env_var("RENDER_DB_NAME")} '
        f'-f {DUMP_FILE}'
    )
    run_cmd(cmd)
    print("✅ 导入成功")

# === 主入口 ===

def main():
    if not ENV_PATH.exists():
        print("❌ config/.env 文件不存在")
        sys.exit(1)

    load_dotenv(dotenv_path=ENV_PATH)
    export_table()
    import_table()

if __name__ == "__main__":
    main()
