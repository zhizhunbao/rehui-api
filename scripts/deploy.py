import subprocess
import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 文件

# 读取环境变量
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
REPO_NAME = os.getenv("REPO_NAME", "rehui-api")

def push_to_github():
    print("🚀 推送代码到 GitHub ...")
    remote_url = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    print(f"📦 构造远程地址: {remote_url}")

    # 确保 remote 存在
    remote_result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    if "origin" not in remote_result.stdout:
        print("🔧 设置 origin remote ...")
        subprocess.run(["git", "remote", "add", "origin", remote_url])

    subprocess.run(["git", "branch", "-M", "main"])

    print("📤 正在强制推送 main 分支 ...")
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main", "--force"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ 推送成功！")
    else:
        print("❌ 推送失败！")
        print("🔎 stdout:", result.stdout)
        print("🔎 stderr:", result.stderr)

def open_render_page():
    print("🌍 打开 Render 部署页面 ...")
    webbrowser.open("https://dashboard.render.com/new/web")
    print("✅ 完成！点击仓库一键部署 rehui-api 即可 🎉")

# def open_render_deploy_page():
#     print("🌐 打开 Render 部署页面 ...")
#     url = f"https://render.com/deploy?repo=https://github.com/{GITHUB_USERNAME}/{REPO_NAME}"
#     webbrowser.open(url)

if __name__ == "__main__":
    push_to_github()
    # open_render_page()
    # open_render_deploy_page()
