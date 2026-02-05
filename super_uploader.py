import os
import time
import json
import subprocess
import requests

# ================= 核心配置 (请确认路径正确) =================
API_LOGIN = "f40890cbc271add9ef00" 
API_KEY = "MZyMX74d4WHeod"
# 路径使用了你在 image_147f1a.png 中展示的绝对路径
FFMPEG_DIR = r"C:\ffmpeg-2026-02-04-git-627da1111c-full_build\bin"
# ===========================================================

def download_video(url):
    """【全能版】自动识别 YT/FB 并调用不同策略下载"""
    print(f"\n📥 正在处理源链接: {url}")
    filename = "temp_video.mp4"
    if os.path.exists(filename): 
        os.remove(filename)

    # 判断是 FB 还是 YT
    is_fb = "facebook.com" in url or "fb.watch" in url
    cookie_file = "facebook_cookies.txt" if is_fb else "youtube_cookies.txt"
    
    # 基础命令参数
    cmd = [
        "yt-dlp",
        "--ffmpeg-location", FFMPEG_DIR,
        "--cookies", cookie_file,
        "--no-check-certificate",
        "--no-cache-dir",
        "--rm-cache-dir",
        "--no-playlist",
        "-f", "best[height<=720][ext=mp4]/best",
        "-o", filename,
        url
    ]

    # 如果是 YouTube，额外尝试 TV 协议绕过解密挑战
    if not is_fb:
        cmd.extend(["--extractor-args", "youtube:player_client=tv"])

    try:
        print(f"🚀 正在启动下载引擎 (使用 {cookie_file})...")
        subprocess.run(cmd, check=True)
        if os.path.exists(filename):
            print(f"✅ 下载并合成成功！")
            return filename
    except Exception as e:
        print(f"❌ 下载失败，请检查 Cookie 是否过期。错误: {e}")
        return None

def upload_to_streamtape(file_path):
    """【上传器】本地文件直推模式"""
    print(f"☁️ 正在将视频推送到 Streamtape...")
    try:
        get_url = f"https://api.streamtape.com/file/ul?login={API_LOGIN}&key={API_KEY}"
        res = requests.get(get_url).json()
        upload_url = res['result']['url']
        
        with open(file_path, 'rb') as f:
            response = requests.post(upload_url, files={'file1': f})
            data = response.json()
            
        if data.get("status") == 200:
            linkid = data['result']['id']
            print(f"✅ 上传成功！ID: {linkid}")
            return {"id": linkid, "embed_url": f"https://streamtape.com/e/{linkid}/"}
    except Exception as e:
        print(f"❌ 上传出错: {e}")
    return None

def generate_static_page(video_data):
    """【生成器】生成 HTML 静态页"""
    try:
        with open("template.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        for key in ['title', 'embed_url', 'id']:
            html = html.replace(f"{{{{{key}}}}}", str(video_data.get(key, '')))
        html = html.replace("{{date}}", time.strftime("%Y-%m-%d"))

        page_name = f"video-{video_data['id']}.html"
        with open(page_name, "w", encoding="utf-8") as f:
            f.write(html)
        return page_name
    except Exception as e:
        print(f"❌ 网页生成失败: {e}")
        return None

if __name__ == "__main__":
    print("--- 📺 视频全自动搬运系统 (2026 稳定版) ---")
    
    if not os.path.exists("links.txt"):
        print("❌ 错误：找不到 links.txt")
        exit()

    with open("links.txt", "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if "|" in l]

    for line in lines:
        yt_url, title = line.split("|", 1)
        video_file = download_video(yt_url)
        
        if video_file:
            info = upload_to_streamtape(video_file)
            if info:
                info['title'] = title
                generate_static_page(info)
                print(f"✨ 搬运完成：{title}")
            
            # 传完一个删一个，节省空间
            if os.path.exists(video_file): 
                os.remove(video_file)

    print("\n🏁 所有任务执行完毕！")