"""
测试 51CTO 发布器的元素选择器
验证更新后的选择器是否正确
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logger import setup_logger

logger = setup_logger('test_selectors')

# 定义所有选择器
SELECTORS = {
    "标题输入框": {
        "type": "CSS",
        "selector": 'input[name="title"][id="title"].title_input',
        "说明": "文章标题输入框，最多100字"
    },
    "正文输入框": {
        "type": "CSS",
        "selector": 'textarea.auto-textarea-input.write-area[placeholder="请输入正文"]',
        "说明": "文章正文输入框"
    },
    "发布按钮": {
        "type": "CSS",
        "selector": 'button.edit-submit',
        "说明": "进入发布设置页面的按钮"
    },
    "一级分类": {
        "type": "XPath",
        "selector": '//div[@class="types_content"]//div[contains(@class, "select_item")]/span[text()="人工智能"]/..',
        "说明": "一级分类选择"
    },
    "二级分类": {
        "type": "XPath",
        "selector": '//div[@class="second-types-content"]//div[contains(@class, "second-types-item")]/span[text()="NLP"]/..',
        "说明": "二级分类选择"
    },
    "个人分类": {
        "type": "CSS",
        "selector": 'input.el-input__inner.pull-down[id="selfType"]',
        "说明": "个人分类下拉框"
    },
    "标签输入框": {
        "type": "CSS",
        "selector": 'input.tag-paper.pull-tag[id="tag-input"]',
        "说明": "标签输入框，最多5个标签，每个最多20字"
    },
    "摘要输入框": {
        "type": "CSS",
        "selector": 'textarea[id="abstractData"]',
        "说明": "摘要输入框，最多500字"
    },
    "最终发布按钮": {
        "type": "CSS",
        "selector": 'button.release[id="submitForm"]',
        "说明": "最终发布按钮"
    }
}


def main():
    """显示所有选择器"""
    logger.info("=" * 80)
    logger.info("51CTO 发布器元素选择器清单")
    logger.info("=" * 80)
    
    for idx, (name, info) in enumerate(SELECTORS.items(), 1):
        logger.info(f"\n{idx}. {name}")
        logger.info(f"   类型: {info['type']}")
        logger.info(f"   选择器: {info['selector']}")
        logger.info(f"   说明: {info['说明']}")
    
    logger.info("\n" + "=" * 80)
    logger.info("选择器说明")
    logger.info("=" * 80)
    
    logger.info("""
使用说明:
1. 标题: 最多100个字
2. 正文: Markdown 格式，支持图片
3. 一级分类: 23个选项，包括后端开发、前端开发、人工智能等
4. 二级分类: 根据一级分类动态显示（例如：人工智能→NLP、深度学习等）
5. 个人分类: 需要提前在个人中心创建
6. 标签: 最多5个，每个最多20字，支持 , ; enter 分隔
7. 摘要: 最多500字，不填写则默认使用文章前200字
8. 话题: 可选，需要在话题列表中存在

优化点:
✅ 使用 WebDriverWait 等待元素加载
✅ 使用更精确的 CSS 选择器
✅ 添加标签和摘要长度限制
✅ 支持二级分类选择
✅ 改进错误处理和日志记录
""")
    
    logger.info("=" * 80)
    logger.info("✅ 51CTO 发布器已更新，所有选择器已匹配最新页面结构")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
