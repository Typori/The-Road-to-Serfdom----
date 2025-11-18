#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原文章节拆分工具
功能：根据原文中的目录结构，自动将原文拆分为多个章节文件
作者：翻译工程工具集
版本：v1.0
日期：2025-11-18
"""

import os
import re
from pathlib import Path


class ChapterSplitter:
    """章节拆分器"""
    
    def __init__(self, source_file, output_dir):
        """
        初始化拆分器
        
        Args:
            source_file: 原文文件路径
            output_dir: 输出目录路径
        """
        self.source_file = Path(source_file)
        self.output_dir = Path(output_dir)
        self.content = ""
        self.chapters = []
        
    def load_content(self):
        """加载原文内容"""
        print(f"正在加载原文: {self.source_file}")
        with open(self.source_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"✓ 已加载 {len(self.content)} 个字符")
    
    def identify_chapters(self):
        """识别所有章节的位置"""
        print("\
正在识别章节结构...")
        
        # 定义章节模式
        # 格式: CHAPTER_NUMBER \n\n CHAPTER_TITLE
        # 注意：使用单词边界确保精确匹配（避免FOUR被FOURTEEN匹配）
        chapter_patterns = [
            # (章节编号名, 章节标题, 正则表达式模式)
            ('One', 'The Abandoned Road', r'\bONE\b\s*\r?\n+\s*THE ABANDONED ROAD'),
            ('Two', 'The Great Utopia', r'\bTWO\b\s*\r?\n+\s*THE GREAT UTOPIA'),
            ('Three', 'Individualism and Collectivism', r'\bTHREE\b\s*\r?\n+\s*INDIVIDUALISM AND COLLECTIVISM'),
            ('Four', 'The "Inevitability" of Planning', r'\bFOUR\b\s*\r?\n+\s*THE\s+["\u201c]INEVITABILITY["\u201d]\s+OF\s+PLANNING'),
            ('Five', 'Planning and Democracy', r'\bFIVE\b\s*\r?\n+\s*PLANNING AND DEMOCRACY'),
            ('Six', 'Planning and the Rule of Law', r'\bSIX\b\s*\r?\n+\s*PLANNING AND THE RULE OF LAW'),
            ('Seven', 'Economic Control and Totalitarianism', r'\bSEVEN\b\s*\r?\n+\s*ECONOMIC CONTROL AND\s*\r?\n+\s*TOTALITARIANISM'),
            ('Eight', 'Who, Whom?', r'\bEIGHT\b\s*\r?\n+\s*WHO,\s+WHOM\?'),
            ('Nine', 'Security and Freedom', r'\bNINE\b\s*\r?\n+\s*SECURITY AND FREEDOM'),
            ('Ten', 'Why the Worst Get on Top', r'\bTEN\b\s*\r?\n+\s*WHY THE WORST GET ON TOP'),
            ('Eleven', 'The End of Truth', r'\bELEVEN\b\s*\r?\n+\s*THE END OF TRUTH'),
            ('Twelve', 'The Socialist Roots of Naziism', r'\bTWELVE\b\s*\r?\n+\s*THE SOCIALIST ROOTS OF NAZIISM'),
            ('Thirteen', 'The Totalitarians in Our Midst', r'\bTHIRTEEN\b\s*\r?\n+\s*THE TOTALITARIANS IN OUR MIDST'),
            ('Fourteen', 'Material Conditions and Ideal Ends', r'\bFOURTEEN\b\s*\r?\n+\s*MATERIAL CONDITIONS AND IDEAL ENDS'),
            ('Fifteen', 'The Prospects of International Order', r'\bFIFTEEN\b\s*\r?\n+\s*THE PROSPECTS OF\s*\r?\n+\s*INTERNATIONAL ORDER'),
            ('Sixteen', 'Conclusion', r'\bSIXTEEN\b\s*\r?\n+\s*CONCLUSION'),
        ]
        
        # 查找所有章节
        for number_name, title, pattern in chapter_patterns:
            matches = list(re.finditer(pattern, self.content, re.MULTILINE))
            # 只取最后一个匹配（实际章节内容，而非目录）
            if matches:
                match = matches[-1]
                self.chapters.append({
                    'number': number_name,
                    'title': title,
                    'start': match.start(),
                    'pattern': pattern
                })
            else:
                print(f"  ⚠ 警告: 未找到章节 {number_name}: {title}")
        
        # 按位置排序
        self.chapters.sort(key=lambda x: x['start'])
        
        print(f"✓ 找到 {len(self.chapters)} 个章节：")
        for i, ch in enumerate(self.chapters):
            print(f"  {i+1:2d}. {ch['number']:10s} - {ch['title']}")
    
    def extract_chapters(self):
        """提取并保存每个章节"""
        print("\
开始提取章节...")
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 提取每个章节
        for i, chapter in enumerate(self.chapters):
            # 确定章节结束位置
            if i < len(self.chapters) - 1:
                end = self.chapters[i + 1]['start']
            else:
                # 最后一章到文件末尾
                end = len(self.content)
            
            # 提取章节内容
            chapter_content = self.content[chapter['start']:end].strip()
            
            # 生成文件名
            # 格式: Chapter01_The_Abandoned_Road.txt
            chapter_num = f"{i+1:02d}"
            # 移除标题中的特殊字符（引号、问号等），保留字母数字和空格
            safe_title = re.sub(r'[^\w\s-]', '', chapter['title']).strip()
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"Chapter{chapter_num}_{safe_title}.txt"
            filepath = self.output_dir / filename
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(chapter_content)
            
            print(f"  ✓ {chapter_num}. {chapter['number']:10s} → {filename} ({len(chapter_content):,} 字符)")
            
            # 更新章节信息
            chapter['filename'] = filename
            chapter['size'] = len(chapter_content)
    
    def generate_index(self):
        """生成索引文件"""
        print("\
生成章节索引...")
        
        index_file = self.output_dir / "00_章节索引.md"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# The Road to Serfdom - 原文章节索引\
\
")
            f.write(f"**来源文件**: {self.source_file.name}\
")
            f.write(f"**拆分日期**: 2025-11-18\
")
            f.write(f"**章节总数**: {len(self.chapters)}\
\
")
            f.write("---\
\
")
            f.write("## 章节列表\
\
")
            
            for i, ch in enumerate(self.chapters):
                f.write(f"{i+1:2d}. **{ch['number']}**: {ch['title']}\
")
                f.write(f"    - 文件: `{ch['filename']}`\
")
                f.write(f"    - 大小: {ch['size']:,} 字符\
\
")
            
            f.write("\
---\
\
")
            f.write("## 使用说明\
\
")
            f.write("1. 每个章节独立保存为 `.txt` 文件\
")
            f.write("2. 文件命名格式: `Chapter序号_章节标题.txt`\
")
            f.write("3. 章节内容包含从该章开头到下一章开头之前的全部文本\
")
            f.write("4. 可使用这些文件进行翻译工作\
")
            f.write("5. 注意：文件名中的特殊字符（引号、问号等）已被移除\
")
        
        print(f"  ✓ 索引文件: {index_file.name}")
    
    def run(self):
        """执行完整的拆分流程"""
        print("=" * 60)
        print("原文章节拆分工具 v1.0")
        print("=" * 60)
        
        try:
            # 1. 加载内容
            self.load_content()
            
            # 2. 识别章节
            self.identify_chapters()
            
            if not self.chapters:
                print("\
❌ 错误: 未找到任何章节!")
                return False
            
            # 3. 提取章节
            self.extract_chapters()
            
            # 4. 生成索引
            self.generate_index()
            
            print("\
" + "=" * 60)
            print(f"✓ 拆分完成！共处理 {len(self.chapters)} 个章节")
            print(f"✓ 输出目录: {self.output_dir}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\
❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    # 默认路径配置
    PROJECT_ROOT = Path(__file__).parent.parent
    SOURCE_FILE = PROJECT_ROOT / "2.原文资料" / "The-Road-to-Serfdom.txt"
    OUTPUT_DIR = PROJECT_ROOT / "2.原文资料" / "chapters"
    
    # 创建拆分器并运行
    splitter = ChapterSplitter(SOURCE_FILE, OUTPUT_DIR)
    success = splitter.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
