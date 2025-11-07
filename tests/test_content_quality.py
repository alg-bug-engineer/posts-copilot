#!/usr/bin/env python3
"""
test_content_quality.py

测试生成内容的质量：长度、自然度、风格
"""

import os
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def analyze_content_quality(content: str) -> dict:
    """分析内容质量"""
    
    # 移除Front Matter
    content_without_fm = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
    
    # 统计指标
    char_count = len(content_without_fm)
    line_count = len(content_without_fm.split('\n'))
    paragraphs = [p for p in content_without_fm.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # 检测AI痕迹词汇
    ai_phrases = [
        '首先', '其次', '然后', '最后',
        '总之', '综上所述', '总的来说',
        '值得注意的是', '需要指出的是',
        '通过...实现', '基于...技术',
        '为...提供了', '使得...成为可能'
    ]
    
    ai_phrase_count = 0
    found_phrases = []
    for phrase in ai_phrases:
        if phrase in content_without_fm:
            ai_phrase_count += 1
            found_phrases.append(phrase)
    
    # 检测章节标题（##）
    section_titles = re.findall(r'^##\s+(.+)$', content_without_fm, re.MULTILINE)
    section_count = len(section_titles)
    
    # 检测冒号标题
    colon_titles = [t for t in section_titles if '：' in t or ':' in t]
    
    # 检测总结段落
    summary_indicators = ['总结', '综上', '最后说', '写在最后']
    has_summary = any(indicator in content_without_fm for indicator in summary_indicators)
    
    # 段落长度分布
    paragraph_lengths = [len(p) for p in paragraphs]
    avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    
    return {
        'char_count': char_count,
        'line_count': line_count,
        'paragraph_count': paragraph_count,
        'avg_paragraph_length': avg_paragraph_length,
        'ai_phrase_count': ai_phrase_count,
        'found_ai_phrases': found_phrases,
        'section_count': section_count,
        'section_titles': section_titles,
        'colon_titles': colon_titles,
        'has_summary': has_summary
    }


def grade_content(metrics: dict) -> str:
    """给内容打分"""
    score = 100
    issues = []
    
    # 长度检查
    if metrics['char_count'] < 1500:
        score -= 30
        issues.append(f"❌ 内容过短 ({metrics['char_count']}字符，建议≥2000)")
    elif metrics['char_count'] < 2000:
        score -= 10
        issues.append(f"⚠️ 内容偏短 ({metrics['char_count']}字符，建议≥2000)")
    else:
        issues.append(f"✅ 内容长度达标 ({metrics['char_count']}字符)")
    
    # AI痕迹检查
    if metrics['ai_phrase_count'] > 5:
        score -= 20
        issues.append(f"❌ AI痕迹严重 (发现{metrics['ai_phrase_count']}处)")
    elif metrics['ai_phrase_count'] > 2:
        score -= 10
        issues.append(f"⚠️ AI痕迹较多 (发现{metrics['ai_phrase_count']}处: {', '.join(metrics['found_ai_phrases'][:3])})")
    else:
        issues.append(f"✅ 语言自然")
    
    # 章节标题检查
    if metrics['section_count'] > 5:
        score -= 10
        issues.append(f"⚠️ 子标题过多 ({metrics['section_count']}个)")
    elif metrics['section_count'] == 0:
        issues.append(f"✅ 流畅表达，无多余章节")
    else:
        issues.append(f"✓ 章节划分适度 ({metrics['section_count']}个)")
    
    # 冒号标题检查
    if metrics['colon_titles']:
        score -= 15
        issues.append(f"❌ 标题使用冒号 ({len(metrics['colon_titles'])}处)")
    else:
        issues.append(f"✅ 标题表达自然")
    
    # 总结检查
    if metrics['has_summary']:
        score -= 10
        issues.append(f"⚠️ 有总结段落（不够灵活）")
    else:
        issues.append(f"✅ 结尾自然")
    
    # 段落长度检查
    if metrics['avg_paragraph_length'] > 500:
        score -= 10
        issues.append(f"⚠️ 段落偏长 (平均{metrics['avg_paragraph_length']:.0f}字)")
    else:
        issues.append(f"✅ 段落长度适中")
    
    # 评级
    if score >= 90:
        grade = "A (优秀)"
    elif score >= 80:
        grade = "B (良好)"
    elif score >= 70:
        grade = "C (及格)"
    else:
        grade = "D (需改进)"
    
    return grade, score, issues


def test_file(file_path: str):
    """测试单个文件"""
    print(f"\n{'='*80}")
    print(f"📄 测试文件: {Path(file_path).name}")
    print(f"{'='*80}\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metrics = analyze_content_quality(content)
        grade, score, issues = grade_content(metrics)
        
        print(f"📊 内容分析")
        print(f"-" * 80)
        print(f"字符数: {metrics['char_count']}")
        print(f"段落数: {metrics['paragraph_count']}")
        print(f"章节数: {metrics['section_count']}")
        print(f"AI痕迹: {metrics['ai_phrase_count']}处")
        
        if metrics['section_titles']:
            print(f"\n章节标题:")
            for title in metrics['section_titles']:
                print(f"  - {title}")
        
        print(f"\n📈 质量评分")
        print(f"-" * 80)
        print(f"综合得分: {score}/100")
        print(f"质量评级: {grade}")
        
        print(f"\n📝 详细评价")
        print(f"-" * 80)
        for issue in issues:
            print(f"  {issue}")
        
        return score
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 0


def test_directory(directory: str):
    """测试目录中的所有文件"""
    print(f"\n{'='*80}")
    print(f"🧪 批量测试内容质量")
    print(f"{'='*80}")
    
    posts_dir = Path(directory)
    if not posts_dir.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    md_files = list(posts_dir.glob("*.md"))
    if not md_files:
        print(f"❌ 未找到Markdown文件")
        return
    
    print(f"找到 {len(md_files)} 个文件\n")
    
    scores = []
    for file_path in md_files:
        score = test_file(str(file_path))
        scores.append(score)
    
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"\n{'='*80}")
        print(f"📊 总体评价")
        print(f"{'='*80}")
        print(f"平均分数: {avg_score:.1f}/100")
        print(f"最高分: {max(scores)}")
        print(f"最低分: {min(scores)}")
        
        if avg_score >= 85:
            print(f"\n✅ 整体质量优秀！")
        elif avg_score >= 75:
            print(f"\n✓ 整体质量良好")
        else:
            print(f"\n⚠️ 需要改进")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='测试文章内容质量')
    parser.add_argument(
        'path',
        nargs='?',
        help='文件或目录路径'
    )
    
    args = parser.parse_args()
    
    if args.path:
        path = Path(args.path)
        if path.is_file():
            test_file(str(path))
        elif path.is_dir():
            test_directory(str(path))
        else:
            print(f"❌ 路径不存在: {args.path}")
    else:
        # 默认测试demo_posts
        test_directory("data/demo_posts")


if __name__ == "__main__":
    main()
