#!/usr/bin/env python3
"""
aibase_crawler.py

从 AIBase (aibase.com) 抓取最新 AI 新闻
提取标题、链接、摘要、时间等信息
"""

import re
import time
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class AIBaseCrawler:
    """AIBase 新闻爬虫"""
    
    BASE_URL = "https://www.aibase.com/zh/news"
    
    # 请求头，模拟浏览器访问
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.aibase.com/'
    }
    
    def __init__(self, timeout: int = 10):
        """
        初始化爬虫
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def fetch_top_news(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        抓取 AIBase 最新新闻
        
        Args:
            limit: 抓取的新闻数量，默认10条
            
        Returns:
            新闻列表，每条新闻包含：
            {
                'title': 标题,
                'url': 链接,
                'summary': 摘要,
                'time': 发布时间,
                'source': 来源,
                'image_url': 封面图片
            }
        """
        print(f"\n{'='*70}")
        print(f"🚀 开始抓取 AIBase 最新 AI 新闻 TOP{limit}")
        print(f"{'='*70}\n")
        
        try:
            # 发起请求
            print(f"📡 正在请求: {self.BASE_URL}")
            response = self.session.get(self.BASE_URL, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有新闻链接 <a> 标签
            # 根据提供的HTML结构，新闻项是 <a> 标签，class包含 "flex group justify-between"
            articles = soup.find_all(
                'a',
                class_=lambda x: x and 'flex' in x and 'group' in x and 'justify-between' in x,
                limit=limit
            )
            
            if not articles:
                print("❌ 未找到新闻列表")
                return []
            
            print(f"✓ 找到 {len(articles)} 篇新闻\n")
            
            news_list = []
            for idx, article in enumerate(articles, 1):
                try:
                    news_item = self._parse_article(article, idx)
                    if news_item:
                        news_list.append(news_item)
                        print(f"  [{idx}] ✓ {news_item['title'][:50]}...")
                except Exception as e:
                    print(f"  [{idx}] ✗ 解析失败: {e}")
                    continue
            
            print(f"\n{'='*70}")
            print(f"✅ 成功抓取 {len(news_list)} 条新闻")
            print(f"{'='*70}\n")
            
            return news_list
            
        except requests.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            return []
        except Exception as e:
            print(f"❌ 抓取出错: {e}")
            return []
    
    def _parse_article(self, article_element, index: int) -> Optional[Dict[str, str]]:
        """
        解析单个新闻条目
        
        Args:
            article_element: BeautifulSoup元素对象
            index: 新闻序号
            
        Returns:
            解析后的新闻信息字典，失败返回None
        """
        try:
            # 提取链接
            url = article_element.get('href', '')
            if url and not url.startswith('http'):
                url = f"https://www.aibase.com{url}"
            
            # 提取标题 <h3> 标签
            title_elem = article_element.find('h3', class_=lambda x: x and 'line-clamp-2' in x)
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # 提取摘要 <div> 标签，class 包含 "line-clamp-2 text-surface-500"
            summary_elem = article_element.find(
                'div',
                class_=lambda x: x and 'line-clamp-2' in x and 'text-surface-500' in x
            )
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # 提取时间和来源
            # <div class="text-sm text-gray-400 flex items-center space-x-1">
            #   <span>11  分钟前</span><span>.</span><span class="font-light">AIbase</span>
            # </div>
            time_info_div = article_element.find('div', class_=lambda x: x and 'text-gray-400' in x)
            time_str = ""
            source = "AIbase"
            
            if time_info_div:
                spans = time_info_div.find_all('span')
                if len(spans) >= 1:
                    time_str = spans[0].get_text(strip=True)
                if len(spans) >= 3:
                    source = spans[2].get_text(strip=True)
            
            # 提取图片
            img_elem = article_element.find('img')
            image_url = img_elem.get('src', '') if img_elem else ""
            
            # 验证必要字段
            if not title or not url:
                return None
            
            return {
                'title': title,
                'url': url,
                'summary': summary,
                'time': time_str,
                'source': source,
                'image_url': image_url,
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  解析文章 #{index} 失败: {e}")
            return None
    
    def get_news_detail(self, url: str) -> Optional[Dict[str, str]]:
        """
        获取新闻详情页内容
        
        Args:
            url: 新闻详情页链接
            
        Returns:
            包含详细内容的字典，失败返回None
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 这里可以根据实际的详情页结构提取更多信息
            # 目前返回基本信息
            return {
                'full_content': soup.get_text(strip=True),
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"获取详情页失败 {url}: {e}")
            return None


def main():
    """测试爬虫功能"""
    crawler = AIBaseCrawler()
    
    # 抓取前10条新闻
    news_list = crawler.fetch_top_news(limit=10)
    
    # 打印结果
    print("\n" + "="*80)
    print("📰 抓取结果:")
    print("="*80 + "\n")
    
    for idx, news in enumerate(news_list, 1):
        print(f"{idx}. {news['title']}")
        print(f"   时间: {news['time']}")
        print(f"   来源: {news['source']}")
        print(f"   链接: {news['url']}")
        if news.get('summary'):
            print(f"   摘要: {news['summary'][:100]}...")
        print()


if __name__ == "__main__":
    main()
