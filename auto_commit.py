import os
import subprocess
import google.generativeai as genai

# 設定 Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "你的 Gemini 2.0 Flash API Key")
genai.configure(api_key=GEMINI_API_KEY)

def get_git_diff():
    try:
        """取得 Git 暫存區中有變更的檔案內容"""
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, encoding="utf-8"
        )

        diff_content = result.stdout.strip()
        return diff_content if diff_content else None

    except UnicodeDecodeError as e:
        print(f"❌ 文字編碼錯誤: {e}")
        return None

def generate_commit_message(diff_content):
    """使用 Google Gemini 生成 Commit Message"""
    if not diff_content:
        print("暫存取中沒有任何變更的檔案內容。")
        return None

    prompt = (
        f"根據以下 Git 變更內容，幫我產生一段合適的 Git Commit 30個繁體中文字以內的訊息(例如'feat(hotel): 新增 Google Place ID 更新和飯店名稱繁體中文化功能')，一定要有一個訊息內容，不需其它說明或詳細內容等等。:\n\n{diff_content}"
    )

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return (
            response.text.strip() if response.text else None
        )

    except Exception as e:
        print(f"❌ Gemini 生成 Commit 訊息失敗: {str(e)}")
        return None

def auto_commit():
    """執行 Git Commit"""
    diff_content = get_git_diff()

    if not diff_content:
        print("❌ 沒有變更的內容，請先修改檔案後再執行。")
        return

    commit_message = generate_commit_message(diff_content)

    if not commit_message:
        return

    try:
        # subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, encoding="utf-8")
        current_branch = result.stdout.strip()
        if not current_branch:
            print("❌ 無法取得目前分支，請確認本地分支是否存在於遠端 Git 專案內。")
            return

        subprocess.run(["git", "push", "origin", current_branch], check=True)

        print(f"✅ Commit & Push 成功，Commit Message 內容:\n{commit_message}\n")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git Commit 失敗: {e}")

if __name__ == "__main__":
    auto_commit()
