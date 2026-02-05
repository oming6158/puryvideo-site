import uploader  # 直接调用你原来的脚本功能
import time

# 读取 links.txt
def run_batch():
    print("--- 🚀 启动批量上传模式 ---")
    
    try:
        with open("links.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ 找不到 links.txt！请先创建文件并放入链接。")
        return

    success_count = 0
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue
        
        # 解析 "链接|标题" 格式
        if "|" in line:
            url, title = line.split("|", 1)
        else:
            url = line
            title = f"Auto Video {int(time.time())}"
            
        print(f"\n🎬 正在处理: {title}")
        print(f"🔗 链接: {url}")
        
        # === 调用 uploader 的核心功能 ===
        # 1. 提交任务
        task_id = uploader.add_remote_upload(url)
        
        if task_id:
            # 2. 等待下载
            video_info = uploader.check_upload_status(task_id)
            if video_info:
                video_info['title'] = title
                
                # 3. 生成网页 & 4. 更新 Sitemap & 5. 存数据库
                page_filename = uploader.generate_static_page(video_info)
                uploader.update_sitemap(page_filename)
                uploader.save_to_database(video_info, page_filename)
                
                success_count += 1
                print(f"✅ 第 {success_count} 个视频处理完毕！")
        
        # 休息一下防止被封 IP
        print("💤 休息 3 秒...")
        time.sleep(3)

    print(f"\n🎉 批量任务结束！共成功上传 {success_count} 个视频。")
    
    # 最后统一推送一次到 GitHub
    uploader.git_auto_push(f"Batch upload {success_count} videos")

if __name__ == "__main__":
    run_batch()