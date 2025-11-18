#!/usr/bin/env python3
"""
publish_csdn_headless_fix.py

修复 headless 模式下发布失败的问题。

主要改进：
1. 增加 headless 模式下的等待时间
2. 添加网络请求监听
3. 添加随机延迟模拟人类行为
4. 增强浏览器伪装
5. 添加发布验证机制
"""

import random
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def random_delay(min_ms=100, max_ms=500):
    """添加随机延迟，模拟人类操作"""
    time.sleep(random.uniform(min_ms/1000, max_ms/1000))


def click_publish_buttons_enhanced(page, tags=None, headless=False) -> bool:
    """
    增强版发布按钮点击，专门优化 headless 模式。
    
    主要改进：
    1. headless 模式下增加等待时间
    2. 监听网络请求确保发布完成
    3. 添加发布成功验证
    """
    
    def robust_click(selector, desc, timeout=10000, retries=2):
        """保持原有的点击逻辑"""
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=timeout)
        except PlaywrightTimeoutError:
            print(f"等待元素可见超时: {selector} ({desc})")
            return False

        for attempt in range(1, retries + 1):
            try:
                locator.scroll_into_view_if_needed()
                locator.click(timeout=5000)
                print(f"已点击 {desc} (selector={selector}, attempt={attempt})")
                random_delay(200, 800)  # 添加随机延迟
                return True
            except Exception as e:
                print(f"尝试点击 {desc} 失败 (attempt={attempt}): {e}")
                time.sleep(0.5)

        return False

    # 点击主发布按钮
    publish_selectors = [
        'button.btn.btn-publish',
        'button.btn-publish',
    ]
    
    clicked = False
    for sel in publish_selectors:
        if robust_click(sel, '主发布按钮', timeout=20000, retries=3):
            clicked = True
            break

    if not clicked:
        print("未能找到或点击主发布按钮")
        return False

    # 🔧 修复点1：增加等待时间（headless 模式需要更长）
    wait_time = 3 if headless else 1
    print(f"等待弹窗加载 ({wait_time}秒)...")
    time.sleep(wait_time)
    
    # 🔧 修复点2：添加操作间的随机延迟
    random_delay(300, 1000)

    # 在弹窗中添加标签
    modal_containers = ['.modal__inner-2', '.modal__content']
    
    for container in modal_containers:
        try:
            # 检查容器是否存在
            if page.locator(container).count() == 0:
                continue
                
            print(f"在容器 {container} 中操作...")
            
            # 添加标签
            if tags and isinstance(tags, (list, tuple)) and len(tags) > 0:
                print(f"尝试添加标签: {tags}")
                for tag in tags:
                    try:
                        # 简化标签添加逻辑
                        input_selector = f'{container} input.el-input__inner'
                        input_locator = page.locator(input_selector).first
                        
                        if input_locator.count() > 0:
                            input_locator.click()
                            random_delay(200, 500)
                            
                            page.keyboard.type(tag, delay=50)  # 模拟打字延迟
                            random_delay(300, 600)
                            
                            page.keyboard.press('Enter')
                            random_delay(500, 1000)
                            
                            print(f"已添加标签: {tag}")
                    except Exception as e:
                        print(f"添加标签 {tag} 失败: {e}")

            # 设置粉丝可见
            try:
                fans_visible_selector = f'{container} label[for="needfans"]'
                fans_locator = page.locator(fans_visible_selector).first
                
                if fans_locator.count() > 0:
                    fans_locator.click()
                    random_delay(300, 600)
                    print("已设置为粉丝可见")
            except Exception as e:
                print(f"设置粉丝可见失败: {e}")

            # 🔧 修复点3：监听网络请求，确保发布完成
            try:
                print("准备点击最终发布按钮并监听网络请求...")
                
                # 查找发布按钮
                publish_btn_selector = f'{container} >> button.btn-b-red:visible'
                btn_locator = page.locator(publish_btn_selector).first
                
                if btn_locator.count() == 0:
                    print("未找到最终发布按钮")
                    continue
                
                # 🔧 关键改进：使用 expect_response 监听发布请求
                try:
                    with page.expect_response(
                        lambda response: (
                            'blog-console-api.csdn.net' in response.url or
                            'biz-source.csdn.net' in response.url or
                            '/article' in response.url
                        ) and response.status == 200,
                        timeout=20000
                    ) as response_info:
                        btn_locator.click(timeout=5000)
                        print("已点击最终发布按钮，等待请求完成...")
                    
                    response = response_info.value
                    print(f"✅ 发布请求已完成: {response.status} {response.url}")
                    
                    # 🔧 修复点4：等待额外时间确保服务器处理完成
                    extra_wait = 3 if headless else 1
                    print(f"等待服务器处理 ({extra_wait}秒)...")
                    time.sleep(extra_wait)
                    
                    return True
                    
                except PlaywrightTimeoutError:
                    # 如果没有捕获到预期的网络请求，尝试传统方式
                    print("⚠️  未捕获到预期的网络请求，使用传统方式...")
                    btn_locator.click(timeout=5000)
                    
                    # 等待 modal 关闭
                    try:
                        page.wait_for_selector(container, state='detached', timeout=10000)
                        print(f"弹窗已关闭")
                        
                        # 额外等待以确保请求完成
                        wait_after_modal = 5 if headless else 2
                        time.sleep(wait_after_modal)
                        
                        return True
                    except Exception as e:
                        print(f"等待弹窗关闭失败: {e}")
                        # 即使失败也等待一段时间
                        time.sleep(5)
                        return False
                        
            except Exception as e:
                print(f"点击发布按钮或监听请求时出错: {e}")
                continue
                
        except Exception as e:
            print(f"在容器 {container} 中操作失败: {e}")
            continue

    print("❌ 未能完成发布流程")
    return False


def verify_publish_success(page, timeout=10000) -> bool:
    """
    🔧 修复点5：验证文章是否真的发布成功
    
    检查方法：
    1. 页面是否跳转到文章管理页面
    2. 是否出现成功提示
    """
    try:
        # 方法1：检查 URL 是否跳转
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            current_url = page.url
            if 'article/manage' in current_url or 'article/list' in current_url:
                print("✅ 发布成功：页面已跳转到文章管理")
                return True
            
            # 方法2：查找成功提示
            success_patterns = [
                'text=发布成功',
                'text=发表成功',
                '[class*="success"]',
                '.success-message'
            ]
            
            for pattern in success_patterns:
                if page.locator(pattern).count() > 0:
                    print(f"✅ 发布成功：发现成功提示 ({pattern})")
                    return True
            
            time.sleep(0.5)
        
        print("⚠️  未检测到明确的成功标志")
        return False
        
    except Exception as e:
        print(f"验证发布状态时出错: {e}")
        return False


def launch_browser_with_stealth(p, headless=False):
    """
    🔧 修复点6：启动伪装过的浏览器
    
    隐藏自动化特征，避免被检测
    """
    browser = p.chromium.launch(
        headless=headless,
        args=[
            '--disable-blink-features=AutomationControlled',  # 隐藏自动化控制特征
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',  # 如果遇到 CORS 问题
            '--disable-features=IsolateOrigins,site-per-process',
        ]
    )
    return browser


def create_context_with_stealth(browser, storage_file=None):
    """
    🔧 修复点7：创建伪装过的浏览器上下文
    """
    context = browser.new_context(
        storage_state=str(storage_file) if storage_file and storage_file.exists() else None,
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='zh-CN',
        timezone_id='Asia/Shanghai',
        extra_http_headers={
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    )
    
    # 注入脚本隐藏 webdriver 特征
    context.add_init_script("""
        // 隐藏 webdriver 属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // 添加 chrome 对象
        window.chrome = {
            runtime: {}
        };
        
        // 修改 plugins 长度
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // 修改 languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
    """)
    
    return context


# 使用示例
def example_usage():
    """
    演示如何使用增强版的发布函数
    """
    storage_file = Path('storage.json')
    
    with sync_playwright() as p:
        # 使用伪装浏览器
        browser = launch_browser_with_stealth(p, headless=True)
        
        # 创建伪装上下文
        context = create_context_with_stealth(browser, storage_file)
        page = context.new_page()
        
        # 打开编辑器
        page.goto("https://editor.csdn.net/md/?not_checkout=1&spm=1000.2115.3001.5352")
        
        # ... 填充标题和内容 ...
        
        # 使用增强版发布函数
        success = click_publish_buttons_enhanced(
            page, 
            tags=['人工智能', 'Python'], 
            headless=True  # 传入 headless 参数
        )
        
        if success:
            # 验证发布是否真的成功
            verified = verify_publish_success(page, timeout=15000)
            if verified:
                print("✅ 文章发布并验证成功！")
            else:
                print("⚠️  发布可能成功但未能验证")
        else:
            print("❌ 发布失败")
        
        # 清理
        context.close()
        browser.close()


if __name__ == '__main__':
    print("这是一个示例文件，展示了如何修复 headless 模式下的发布问题")
    print("主要改进点：")
    print("1. ⏱️  增加 headless 模式下的等待时间")
    print("2. 🎲 添加随机延迟模拟人类行为")
    print("3. 🌐 监听网络请求确保发布完成")
    print("4. 🥸 增强浏览器伪装避免检测")
    print("5. ✅ 添加发布成功验证")
    print("\n请将这些改进应用到您的 publish_csdn.py 中")
