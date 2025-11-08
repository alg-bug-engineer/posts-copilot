#!/usr/bin/env python3
"""
Cookies 管理工具
用于清理、查看、备份 cookies 文件
"""

import os
import pickle
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class CookiesManager:
    """Cookies 管理器"""
    
    def __init__(self):
        self.cookies_dir = Path(__file__).parent.parent / 'data' / 'cookies'
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
    
    def list_cookies(self) -> Dict[str, dict]:
        """列出所有 cookies 文件"""
        cookies_info = {}
        
        for cookie_file in self.cookies_dir.glob("*_cookies.pkl"):
            platform = cookie_file.stem.replace('_cookies', '')
            
            try:
                # 获取文件信息
                stat = cookie_file.stat()
                
                # 尝试加载 cookies 以获取数量
                with open(cookie_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                cookies_info[platform] = {
                    'file': str(cookie_file),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'count': len(cookies) if isinstance(cookies, list) else 0,
                    'domains': list(set(c.get('domain', '').lstrip('.') for c in cookies if isinstance(cookies, list)))
                }
                
            except Exception as e:
                cookies_info[platform] = {
                    'file': str(cookie_file),
                    'error': str(e)
                }
        
        return cookies_info
    
    def show_cookies_info(self):
        """显示 cookies 信息"""
        cookies_info = self.list_cookies()
        
        if not cookies_info:
            print("📭 没有找到任何 cookies 文件")
            return
        
        print(f"\n{'='*60}")
        print(f"🍪 Cookies 文件信息")
        print(f"{'='*60}")
        
        for platform, info in cookies_info.items():
            print(f"\n📱 平台: {platform}")
            
            if 'error' in info:
                print(f"   ❌ 错误: {info['error']}")
            else:
                print(f"   📁 文件: {info['file']}")
                print(f"   📊 大小: {info['size']} 字节")
                print(f"   🕐 修改时间: {info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   🔢 Cookie 数量: {info['count']}")
                print(f"   🌐 域名: {', '.join(info['domains'])}")
    
    def clean_cookies(self, platform: Optional[str] = None):
        """清理 cookies 文件"""
        if platform:
            # 清理特定平台
            cookie_file = self.cookies_dir / f"{platform}_cookies.pkl"
            if cookie_file.exists():
                cookie_file.unlink()
                print(f"✅ 已删除 {platform} 的 cookies 文件")
            else:
                print(f"⚠️  {platform} 的 cookies 文件不存在")
        else:
            # 清理所有 cookies
            cookie_files = list(self.cookies_dir.glob("*_cookies.pkl"))
            
            if not cookie_files:
                print("📭 没有找到任何 cookies 文件")
                return
            
            for cookie_file in cookie_files:
                platform_name = cookie_file.stem.replace('_cookies', '')
                cookie_file.unlink()
                print(f"✅ 已删除 {platform_name} 的 cookies 文件")
            
            print(f"\n🎉 共清理了 {len(cookie_files)} 个 cookies 文件")
    
    def backup_cookies(self, backup_name: Optional[str] = None):
        """备份 cookies 文件"""
        if backup_name is None:
            backup_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_dir = self.cookies_dir.parent / 'backups' / f'cookies_{backup_name}'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        cookie_files = list(self.cookies_dir.glob("*_cookies.pkl"))
        
        if not cookie_files:
            print("📭 没有找到任何 cookies 文件可备份")
            return
        
        backed_up = 0
        for cookie_file in cookie_files:
            backup_file = backup_dir / cookie_file.name
            
            try:
                import shutil
                shutil.copy2(cookie_file, backup_file)
                backed_up += 1
                print(f"✅ 备份 {cookie_file.name}")
            except Exception as e:
                print(f"❌ 备份 {cookie_file.name} 失败: {e}")
        
        print(f"\n🎉 备份完成！共备份了 {backed_up} 个文件到:")
        print(f"📁 {backup_dir}")
    
    def restore_cookies(self, backup_name: str):
        """恢复 cookies 文件"""
        backup_dir = self.cookies_dir.parent / 'backups' / f'cookies_{backup_name}'
        
        if not backup_dir.exists():
            print(f"❌ 备份目录不存在: {backup_dir}")
            return
        
        backup_files = list(backup_dir.glob("*_cookies.pkl"))
        
        if not backup_files:
            print(f"📭 备份目录中没有找到 cookies 文件: {backup_dir}")
            return
        
        restored = 0
        for backup_file in backup_files:
            target_file = self.cookies_dir / backup_file.name
            
            try:
                import shutil
                shutil.copy2(backup_file, target_file)
                restored += 1
                print(f"✅ 恢复 {backup_file.name}")
            except Exception as e:
                print(f"❌ 恢复 {backup_file.name} 失败: {e}")
        
        print(f"\n🎉 恢复完成！共恢复了 {restored} 个文件")
    
    def export_cookies_json(self, platform: str, output_file: Optional[str] = None):
        """将 cookies 导出为 JSON 格式"""
        cookie_file = self.cookies_dir / f"{platform}_cookies.pkl"
        
        if not cookie_file.exists():
            print(f"❌ {platform} 的 cookies 文件不存在")
            return
        
        try:
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            if output_file is None:
                output_file = self.cookies_dir.parent / f'{platform}_cookies.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ {platform} 的 cookies 已导出到: {output_file}")
            print(f"📊 共导出 {len(cookies)} 个 cookies")
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Cookies 管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看所有 cookies 信息
  python cookies_manager.py --list
  
  # 清理特定平台的 cookies
  python cookies_manager.py --clean --platform csdn
  
  # 清理所有 cookies
  python cookies_manager.py --clean
  
  # 备份 cookies
  python cookies_manager.py --backup
  
  # 恢复 cookies
  python cookies_manager.py --restore backup_name
  
  # 导出 cookies 为 JSON
  python cookies_manager.py --export --platform zhihu
        """
    )
    
    parser.add_argument('--list', action='store_true', help='列出所有 cookies 信息')
    parser.add_argument('--clean', action='store_true', help='清理 cookies 文件')
    parser.add_argument('--backup', action='store_true', help='备份 cookies 文件')
    parser.add_argument('--restore', type=str, help='恢复指定的备份')
    parser.add_argument('--export', action='store_true', help='导出 cookies 为 JSON')
    parser.add_argument('--platform', type=str, help='指定平台名称')
    parser.add_argument('--backup-name', type=str, help='备份名称')
    parser.add_argument('--output', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    if not any([args.list, args.clean, args.backup, args.restore, args.export]):
        parser.print_help()
        return
    
    manager = CookiesManager()
    
    try:
        if args.list:
            manager.show_cookies_info()
        
        elif args.clean:
            if args.platform:
                manager.clean_cookies(args.platform)
            else:
                # 确认删除所有
                confirm = input("\n⚠️  确定要删除所有 cookies 文件吗？(y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    manager.clean_cookies()
                else:
                    print("❌ 操作已取消")
        
        elif args.backup:
            manager.backup_cookies(args.backup_name)
        
        elif args.restore:
            manager.restore_cookies(args.restore)
        
        elif args.export:
            if not args.platform:
                print("❌ 导出功能需要指定平台名称 (--platform)")
                return
            manager.export_cookies_json(args.platform, args.output)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()