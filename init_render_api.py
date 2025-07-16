import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

import requests
from dotenv import load_dotenv

GITHUB_USERNAME = "zhizhunbao"
REPO_NAME = "rehui-api"

def install_dependencies():
    print("📦 安装依赖 fastapi + uvicorn + python-dotenv ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "python-dotenv", "git-filter-repo"])

def get_github_token():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ 环境变量 GITHUB_TOKEN 未找到，请先设置 .env 文件")
        sys.exit(1)
    return token

def create_project_structure(project_dir: Path):
    api_dir = project_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)

    (api_dir / "main_weapp_api.py").write_text('''\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"msg": "pong"}

@app.get("/api/rank/top")
def get_top_rank():
    return {"top": ["Car A", "Car B", "Car C"]}
''')

    (project_dir / "start_render.py").write_text('''\
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main_weapp_api:app", host="0.0.0.0", port=8000)
''')

    (project_dir / "start.sh").write_text('''\
#!/usr/bin/env bash
uvicorn api.main_weapp_api:app --host 0.0.0.0 --port 8000
''')

    (project_dir / "requirements.txt").write_text('''\
fastapi
uvicorn
python-dotenv
''')

    (project_dir / "render.yaml").write_text('''\
services:
  - type: web
    name: rehui-api
    env: python
    buildCommand: ""
    startCommand: bash scripts/start.sh
    plan: free
    branch: main
    autoDeploy: true
''')

    (project_dir / ".gitignore").write_text('''\
__pycache__/
*.pyc
config/.env
.venv/
.idea/
scripts/setup_env_and_deps.py
db/postgres_tools
''')

    print("✅ 项目结构已创建。")

def initialize_git():
    print("🔧 初始化 Git 仓库 ...")
    subprocess.run(["git", "init"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "🎉 init rehui-api project"])

def create_repo_if_not_exists(token):
    print(f"🔍 检查 GitHub 是否已存在仓库 {REPO_NAME} ...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    check_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}"
    res = requests.get(check_url, headers=headers)

    if res.status_code == 200:
        print("✅ 仓库已存在，跳过创建步骤。")
    else:
        print("📁 仓库不存在，准备自动创建...")
        data = {"name": REPO_NAME, "private": False, "auto_init": False}
        create_res = requests.post("https://api.github.com/user/repos", headers=headers, data=json.dumps(data))

        if create_res.status_code == 201:
            print("✅ 仓库创建成功！")
        else:
            print("❌ 仓库创建失败：", create_res.text)
            sys.exit(1)

def push_to_github():
    print("🚀 推送代码到 GitHub ...")
    remote_url = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    remote_result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    if "origin" not in remote_result.stdout:
        subprocess.run(["git", "remote", "add", "origin", remote_url])

    subprocess.run(["git", "branch", "-M", "main"])
    result = subprocess.run(["git", "push", "-u", "origin", "main", "--force"])
    if result.returncode == 0:
        print("✅ 推送成功！")
    else:
        print("❌ 推送失败，请检查 GitHub 返回的错误")

def open_render_page():
    print("🌍 打开 Render 部署页面 ...")
    webbrowser.open("https://dashboard.render.com/new/web")
    print("✅ 完成！点击仓库一键部署 rehui-api 即可 🎉")

def main():
    project_dir = Path(".")
    install_dependencies()
    token = get_github_token()
    create_project_structure(project_dir)
    initialize_git()
    create_repo_if_not_exists(token)
    push_to_github()
    open_render_page()

if __name__ == "__main__":
    main()
