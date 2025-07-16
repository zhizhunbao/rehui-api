import os
import sys
import platform
import subprocess
import zipfile
import requests
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# === 配置 ===
TABLE_NAME = "dws_rehui_rank_cargurus"
DUMP_FILE = f"{TABLE_NAME}.sql"
TOOLS_DIR = Path("postgres_tools")
PG_DUMP_PATH = TOOLS_DIR / "pgsql" / "bin" / "pg_dump.exe"
PG_TOOLS_ZIP = TOOLS_DIR / "pg_tools.zip"
PG_TOOLS_URL = "https://get.enterprisedb.com/postgresql/postgresql-16.3-1-windows-x64-binaries.zip"

# === 工具函数 ===

def download_pg_tools():
    print("📦 准备下载 PostgreSQL CLI 工具（仅 Windows）")
    TOOLS_DIR.mkdir(exist_ok=True)
    if not PG_TOOLS_ZIP.exists():
        with requests.get(PG_TOOLS_URL, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with open(PG_TOOLS_ZIP, 'wb') as f, tqdm(
                    desc="⬇️ 下载中", total=total, unit='B', unit_scale=True
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
        print("✅ 下载完成")
    else:
        print("✅ 已存在下载文件，跳过下载")

    print("📂 解压中...")
    with zipfile.ZipFile(PG_TOOLS_ZIP, 'r') as zip_ref:
        zip_ref.extractall(TOOLS_DIR)
    print("✅ 解压完成")

def ensure_pg_dump():
    if platform.system() != "Windows":
        return "pg_dump"  # macOS/Linux 可用系统 pg_dump
    if PG_DUMP_PATH.exists():
        return str(PG_DUMP_PATH)
    else:
        download_pg_tools()
        if not PG_DUMP_PATH.exists():
            print("❌ pg_dump 仍未找到，退出")
            sys.exit(1)
        return str(PG_DUMP_PATH)

def run_cmd(command):
    print(f"🚀 执行命令:\n{command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("❌ 命令执行失败")
        sys.exit(1)

def export_single_table(pg_dump):
    print(f"📦 导出本地表: {TABLE_NAME}")
    os.environ["PGPASSWORD"] = os.getenv("LOCAL_DB_PASSWORD")
    cmd = (
        f'"{pg_dump}" -w '
        f'-h {os.getenv("LOCAL_DB_HOST")} '
        f'-p {os.getenv("LOCAL_DB_PORT")} '
        f'-U {os.getenv("LOCAL_DB_USER")} '
        f'-d {os.getenv("LOCAL_DB_NAME")} '
        f'-t {TABLE_NAME} > {DUMP_FILE}'
    )
    run_cmd(cmd)
    print(f"✅ 表导出成功 → {DUMP_FILE}")

def import_to_render():
    print("☁️ 开始导入到 Render PostgreSQL")
    os.environ["PGPASSWORD"] = os.getenv("RENDER_DB_PASSWORD")
    cmd = (
        f'psql -w '
        f'-h {os.getenv("RENDER_DB_HOST")} '
        f'-p {os.getenv("RENDER_DB_PORT")} '
        f'-U {os.getenv("RENDER_DB_USER")} '
        f'-d {os.getenv("RENDER_DB_NAME")} '
        f'-f {DUMP_FILE}'
    )
    run_cmd(cmd)
    print("✅ Render 导入成功")

# === 主流程 ===

def main():
    load_dotenv()
    pg_dump = ensure_pg_dump()
    export_single_table(pg_dump)
    import_to_render()

if __name__ == "__main__":
    main()
