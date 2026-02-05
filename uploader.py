import requests
import time
import json
import os
import subprocess 

# ================= 核心配置 =================
API_LOGIN = "f40890cbc271add9ef00" 
API_KEY = "MZyMX74d4WHeod"
# 请确认这是你的新域名
MY_DOMAIN = "puryvideo-site.pages.dev" 
# ===========================================

def add_remote_upload(video_url):
    base_url = "https://api.streamtape.com/remotedl/add"
    params = {"login": API_LOGIN, "key": API_KEY, "url": video_url}
    try:
        print(f"🚀 Submitting task: {video_url} ...")
        response = requests.get(base_url, params=params)
        data = response.json()
        if data.get("status") == 200:
            return data["result"]["id"]
        else:
            print(f"[ERROR] Streamtape API: {data.get('msg')}")
    except Exception as e:
        print(f"[EXCEPTION] Connection failed: {e}")
    return None

def check_upload_status(upload_id):
    base_url = "https://api.streamtape.com/remotedl/status"
    params = {"login": API_LOGIN, "key": API_KEY, "id": upload_id}

    print("⏳ Waiting for Streamtape download...", end="")
    while True:
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            if data.get("status") != 200: return None

            result = data["result"].get(upload_id)
            if not result: return None

            if result["status"] == 'finished':
                print("\n✅ Download Finished!")
                return {
                    "id": result["linkid"],
                    "embed_url": f"https://streamtape.com/e/{result['linkid']}/"
                }
            else:
                print(".", end="")
                time.sleep(5)
        except Exception as e:
            print(f"\n[EXCEPTION] {e}")
            break
    return None

def generate_static_page(video_data):
    if not os.path.exists("template.html"):
        print("[WARN] template.html not found!")
        return None

    with open("template.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    title = video_data.get('title', f"Video {video_data['id']}")
    seo_desc = f"Watch {title} online for free. {title} 在线观看免费高清. Full HD no ads."
    
    html_content = html_content.replace("{{title}}", title)
    html_content = html_content.replace("{{description}}", seo_desc)
    html_content = html_content.replace("{{embed_url}}", video_data['embed_url'])
    html_content = html_content.replace("{{linkid}}", video_data['id'])
    html_content = html_content.replace("{{date}}", time.strftime("%Y-%m-%d"))

    filename = f"video-{video_data['id']}.html"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[SEO] Page Generated: {filename}")
    return filename

def update_sitemap(new_filename):
    sitemap_file = "sitemap.xml"
    base_url = f"https://{MY_DOMAIN}/"
    header = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    footer = '</urlset>'
    new_entry = f"""  <url>
    <loc>{base_url}{new_filename}</loc>
    <lastmod>{time.strftime("%Y-%m-%d")}</lastmod>
    <changefreq>daily</changefreq>
  </url>\n"""

    content = header
    if os.path.exists(sitemap_file):
        with open(sitemap_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) > 2:
                content = "".join(lines[:-1])

    with open(sitemap_file, "w", encoding="utf-8") as f:
        f.write(content + new_entry + footer)
    print(f"[SEO] Sitemap Updated.")

def save_to_database(video_data, page_filename):
    db_file = "videos.json"
    if not os.path.exists(db_file):
        with open(db_file, "w", encoding="utf-8") as f: json.dump([], f)
    with open(db_file, "r", encoding="utf-8") as f:
        try: data = json.load(f)
        except: data = []
    
    new_entry = {
        "title": video_data.get('title', f"Video-{video_data['id']}"),
        "linkid": video_data['id'],
        "embed_url": video_data['embed_url'],
        "page_url": page_filename,
        "date": time.strftime("%Y-%m-%d")
    }
    data.insert(0, new_entry)
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[DB] Saved to videos.json")

def git_auto_push(commit_msg):
    """【全自动核心】自动打包并上传到 GitHub"""
    print("\n☁️ 正在自动推送更新到 GitHub (Cloudflare 将自动同步)...")
    try:
        # 1. 自动添加所有文件
        subprocess.run(["git", "add", "."], check=True)
        # 2. 自动提交
        subprocess.run(["git", "commit", "-m", f"Auto update: {commit_msg}"], check=True)
        # 3. 自动推送
        subprocess.run(["git", "push"], check=True)
        print("✅ 全自动推送成功！请等待 Cloudflare 更新。")
    except Exception as e:
        print(f"❌ 推送失败: {e}")
        print("💡 提示: 请确保你已经手动运行过一次 'git push -u origin main'")

if __name__ == "__main__":
    print("--- 🌍 Global Video Publisher (Auto-Git Mode) ---")
    
    video_url = input("Video URL (.mp4): ").strip()
    print("💡 Tip: Use English + Chinese for best SEO")
    video_title = input("Video Title: ").strip()
    
    if not video_title: video_title = f"New Leaked Video {int(time.time())}"

    if video_url:
        task_id = add_remote_upload(video_url)
        if task_id:
            video_info = check_upload_status(task_id)
            if video_info:
                video_info['title'] = video_title
                page_filename = generate_static_page(video_info)
                update_sitemap(page_filename)
                save_to_database(video_info, page_filename)
                
                # 🔥 触发自动推送
                git_auto_push(video_title)