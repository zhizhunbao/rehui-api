import json
import shutil
import subprocess
import os
import sys
import webbrowser
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 文件

# 读取环境变量
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
REPO_NAME = os.getenv("REPO_NAME", "rehui-api")
token = os.getenv("GITHUB_TOKEN")

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

import os
import shutil
from pathlib import Path
import subprocess

def fix_scripts_dir_only():
    scripts_path = Path("scripts")

    if scripts_path.exists():
        print("🧹 尝试从 Git 中移除 scripts 子模块（如果存在） ...")
        subprocess.run(["git", "submodule", "deinit", "-f", "scripts"], check=False)
        subprocess.run(["git", "rm", "-f", "scripts"], check=False)
        subprocess.run(["rm", "-rf", ".git/modules/scripts"], shell=True)  # 子模块注册目录

        try:
            print("🧹 强制删除 scripts 目录 ...")
            shutil.rmtree(scripts_path, ignore_errors=True)
        except Exception as e:
            print(f"⚠️ 删除失败：{e}")

    # 重建 scripts 空目录
    print("📁 创建新的 scripts 目录 ...")
    scripts_path.mkdir(exist_ok=True)

    print("✅ scripts 目录已完成重建")

# def open_render_deploy_page():
#     print("🌐 打开 Render 部署页面 ...")
#     url = f"https://render.com/deploy?repo=https://github.com/{GITHUB_USERNAME}/{REPO_NAME}"
#     webbrowser.open(url)

if __name__ == "__main__":

    initialize_git()
    # create_repo_if_not_exists(token)
    fix_scripts_dir_only()
    push_to_github()

    # open_render_page()
    # open_render_deploy_page()
