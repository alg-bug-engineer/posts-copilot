#!/usr/bin/env python3
"""
qbitai_crawler.py

从量子位(qbitai.com)抓取热门科技新闻
提取标题、链接、简介、标签、作者、时间等信息
"""

import re
import time
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class QbitAICrawler:
    """量子位新闻爬虫"""
    
    BASE_URL = "https://www.qbitai.com"
    
    # 请求头，模拟浏览器访问
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
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
        抓取量子位首页TOP热点新闻
        
        Args:
            limit: 抓取的新闻数量，默认10条
            
        Returns:
            新闻列表，每条新闻包含：
            {
                'title': 标题,
                'url': 链接,
                'summary': 摘要,
                'author': 作者,
                'time': 发布时间,
                'tags': 标签列表,
                'image_url': 封面图片
            }
        """
        print(f"\n{'='*70}")
        print(f"🚀 开始抓取量子位首页 TOP{limit} 热点新闻")
        print(f"{'='*70}\n")
        
        try:
            # 发起请求
            print(f"📡 正在请求: {self.BASE_URL}")
            response = self.session.get(self.BASE_URL, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章列表容器
            article_list = soup.find('div', class_='article_list')
            if not article_list:
                print("❌ 未找到文章列表容器")
                return []
            
            # 查找所有文章项
            articles = article_list.find_all('div', class_='picture_text', limit=limit)
            print(f"✓ 找到 {len(articles)} 篇文章\n")
            
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
            print(f"❌ 抓取过程出错: {e}")
            return []
    
    def _parse_article(self, article_element, index: int) -> Optional[Dict[str, str]]:
        """
        解析单篇文章元素
        
        Args:
            article_element: BeautifulSoup文章元素
            index: 文章序号
            
        Returns:
            文章信息字典，解析失败返回None
        """
        # 提取图片
        image_url = ""
        picture_div = article_element.find('div', class_='picture')
        if picture_div:
            img_tag = picture_div.find('img')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']
        
        # 提取文本区域
        text_box = article_element.find('div', class_='text_box')
        if not text_box:
            return None
        
        # 提取标题和链接
        h4_tag = text_box.find('h4')
        if not h4_tag:
            return None
        
        a_tag = h4_tag.find('a')
        if not a_tag:
            return None
        
        title = a_tag.get_text(strip=True)
        url = a_tag.get('href', '')
        if not url.startswith('http'):
            url = self.BASE_URL + url
        
        # 提取摘要
        summary = ""
        summary_p = text_box.find('p')
        if summary_p:
            summary_text = summary_p.get_text(strip=True)
            # 过滤掉空内容
            if summary_text and summary_text not in ['""', '']:
                summary = summary_text
        
        # 提取信息区域（作者、时间、标签）
        info_div = text_box.find('div', class_='info')
        author = ""
        publish_time = ""
        tags = []
        
        if info_div:
            # 提取作者
            author_span = info_div.find('span', class_='author')
            if author_span:
                author_a = author_span.find('a')
                if author_a:
                    author = author_a.get_text(strip=True)
            
            # 提取时间
            time_span = info_div.find('span', class_='time')
            if time_span:
                publish_time = time_span.get_text(strip=True)
            
            # 提取标签
            tags_div = info_div.find('div', class_='tags_s')
            if tags_div:
                tag_links = tags_div.find_all('a', rel='tag')
                tags = [tag.get_text(strip=True) for tag in tag_links if tag.get_text(strip=True)]
        
        return {
            'title': title,
            'url': url,
            'summary': summary if summary else title,  # 如果没有摘要，使用标题
            'author': author,
            'time': publish_time,
            'tags': tags,
            'image_url': image_url,
            'source': '量子位',
            'crawled_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def fetch_article_detail(self, url: str) -> Optional[Dict[str, str]]:
        """
        抓取文章详情页内容（可选功能）
        
        Args:
            url: 文章URL
            
        Returns:
            包含完整内容的字典
        """
        try:
            print(f"📄 正在抓取文章详情: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试提取文章正文（这部分需要根据实际页面结构调整）
            article_content = soup.find('div', class_='article-content')
            if not article_content:
                article_content = soup.find('article')
            
            if article_content:
                # 提取所有段落
                paragraphs = article_content.find_all(['p', 'h2', 'h3'])
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                return {
                    'url': url,
                    'content': content,
                    'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                print(f"  ⚠️ 未找到文章正文区域")
                return None
                
        except Exception as e:
            print(f"  ❌ 抓取详情失败: {e}")
            return None
    
    def save_to_json(self, news_list: List[Dict], output_file: str = "qbitai_news.json"):
        """
        保存新闻列表为JSON文件
        
        Args:
            news_list: 新闻列表
            output_file: 输出文件路径
        """
        import json
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(news_list, f, ensure_ascii=False, indent=2)
            print(f"✅ 新闻已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")


def main():
    """测试爬虫功能"""
    crawler = QbitAICrawler()
    
    # 抓取TOP10新闻
    news_list = crawler.fetch_top_news(limit=10)
    
    # 打印结果
    if news_list:
        print("\n" + "="*70)
        print("📋 抓取结果汇总")
        print("="*70 + "\n")
        
        for idx, news in enumerate(news_list, 1):
            print(f"\n【{idx}】{news['title']}")
            print(f"   作者: {news['author']} | 时间: {news['time']}")
            print(f"   标签: {', '.join(news['tags']) if news['tags'] else '无'}")
            print(f"   摘要: {news['summary'][:100]}...")
            print(f"   链接: {news['url']}")
        
        # 保存为JSON
        crawler.save_to_json(news_list, "data/qbitai_top10.json")
    else:
        print("\n❌ 未抓取到任何新闻")


if __name__ == "__main__":
    main()
