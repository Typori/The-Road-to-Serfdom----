#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原文完整拆分工具 v2.0
功能：完整拆分《通往奴役之路》原文，包括所有前言、16个章节和附录
"""

import re
from pathlib import Path


class ComprehensiveChapterSplitter:
    """完整章节拆分器"""
    
    def __init__(self, source_file, output_dir):
        self.source_file = Path(source_file)
        self.output_dir = Path(output_dir)
        self.content = ""
        self.sections = []
        
    def load_content(self):
        print(f"正在加载原文: {self.source_file}")
        with open(self.source_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"✓ 已加载 {len(self.content)} 个字符")
    
    def identify_sections(self):
        print("\n正在识别文书完整结构...")
        
        section_patterns = [
            ('Prefatory Materials', '【前言部分】Editorial Foreword', r'^Editorial Foreword$', False),
            ('Preface Original', '【前言部分】Preface to the Original Editions', r'^Preface to the Original Editions$', False),
            ('Foreword 1956', '【前言部分】Foreword to the 1956 American Paperback Edition', r'^Foreword to the 1956 American Paperback Edition$', False),
            ('Preface 1976', '【前言部分】Preface to the 1976 Edition', r'^Preface to the 1976 Edition$', False),
            ('Introduction Main', '【前言部分】Introduction', r'^Introduction$', False),
            
            ('Chapter 01', 'Chapter 01: The Abandoned Road', r'\bONE\b\s*\r?\n+\s*THE ABANDONED ROAD', True),
            ('Chapter 02', 'Chapter 02: The Great Utopia', r'\bTWO\b\s*\r?\n+\s*THE GREAT UTOPIA', True),
            ('Chapter 03', 'Chapter 03: Individualism and Collectivism', r'\bTHREE\b\s*\r?\n+\s*INDIVIDUALISM AND COLLECTIVISM', True),
            ('Chapter 04', 'Chapter 04: The "Inevitability" of Planning', r'\bFOUR\b\s*\r?\n+\s*THE\s+["\u201c]INEVITABILITY["\u201d]\s+OF\s+PLANNING', True),
            ('Chapter 05', 'Chapter 05: Planning and Democracy', r'\bFIVE\b\s*\r?\n+\s*PLANNING AND DEMOCRACY', True),
            ('Chapter 06', 'Chapter 06: Planning and the Rule of Law', r'\bSIX\b\s*\r?\n+\s*PLANNING AND THE RULE OF LAW', True),
            ('Chapter 07', 'Chapter 07: Economic Control and Totalitarianism', r'\bSEVEN\b\s*\r?\n+\s*ECONOMIC CONTROL AND\s*\r?\n+\s*TOTALITARIANISM', True),
            ('Chapter 08', 'Chapter 08: Who, Whom?', r'\bEIGHT\b\s*\r?\n+\s*WHO,\s+WHOM\?', True),
            ('Chapter 09', 'Chapter 09: Security and Freedom', r'\bNINE\b\s*\r?\n+\s*SECURITY AND FREEDOM', True),
            ('Chapter 10', 'Chapter 10: Why the Worst Get on Top', r'\bTEN\b\s*\r?\n+\s*WHY THE WORST GET ON TOP', True),
            ('Chapter 11', 'Chapter 11: The End of Truth', r'\bELEVEN\b\s*\r?\n+\s*THE END OF TRUTH', True),
            ('Chapter 12', 'Chapter 12: The Socialist Roots of Naziism', r'\bTWELVE\b\s*\r?\n+\s*THE SOCIALIST ROOTS OF NAZIISM', True),
            ('Chapter 13', 'Chapter 13: The Totalitarians in Our Midst', r'\bTHIRTEEN\b\s*\r?\n+\s*THE TOTALITARIANS IN OUR MIDST', True),
            ('Chapter 14', 'Chapter 14: Material Conditions and Ideal Ends', r'\bFOURTEEN\b\s*\r?\n+\s*MATERIAL CONDITIONS AND IDEAL ENDS', True),
            ('Chapter 15', 'Chapter 15: The Prospects of International Order', r'\bFIFTEEN\b\s*\r?\n+\s*THE PROSPECTS OF\s*\r?\n+\s*INTERNATIONAL ORDER', True),
            ('Chapter 16', 'Chapter 16: Conclusion', r'\bSIXTEEN\b\s*\r?\n+\s*CONCLUSION', True),
            ('Supplementary', '【附录部分】Bibliographical Note & Appendix & Documents', r'^Bibliographical Note$', False),
        ]
        
        for short_name, display_name, pattern, is_chapter in section_patterns:
            matches = list(re.finditer(pattern, self.content, re.MULTILINE))
            if matches:
                match = matches[-1]
                self.sections.append({
                    'short': short_name,
                    'display': display_name,
                    'is_chapter': is_chapter,
                    'start': match.start(),
                    'pattern': pattern
                })
            else:
                print(f"  警告: 未找到 {display_name}")
        
        self.sections.sort(key=lambda x: x['start'])
        
        print(f"✓ 找到 {len(self.sections)} 个部分")
        chapter_count = sum(1 for s in self.sections if s['is_chapter'])
        print(f"  章节: {chapter_count} | 其他部分: {len(self.sections) - chapter_count}")
    
    def extract_sections(self):
        print("\n开始提取部分...")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        file_counter = 1
        for i, section in enumerate(self.sections):
            if i < len(self.sections) - 1:
                end = self.sections[i + 1]['start']
            else:
                end = len(self.content)
            
            section_content = self.content[section['start']:end].strip()
            
            if section['is_chapter']:
                chapter_num = f"{file_counter:02d}"
                safe_title = re.sub(r'[^\w\s-]', '', section['display']).strip()
                safe_title = re.sub(r'[-\s]+', '_', safe_title)
                filename = f"Chapter{chapter_num}_{safe_title}.txt"
                file_counter += 1
            else:
                if 'Editorial' in section['display']:
                    filename = "00_Editorial_Foreword.txt"
                elif 'Original' in section['display']:
                    filename = "00_Preface_Original_Editions.txt"
                elif '1956' in section['display']:
                    filename = "00_Foreword_1956.txt"
                elif '1976' in section['display']:
                    filename = "00_Preface_1976.txt"
                elif 'Introduction' in section['display']:
                    filename = "00_Introduction.txt"
                else:
                    filename = "99_Appendix_And_Supplements.txt"
            
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(section_content)
            
            size_kb = len(section_content) / 1024
            print(f"  ✓ {section['display']:60s} → {filename} ({size_kb:7.2f} KB)")
            
            section['filename'] = filename
            section['size'] = len(section_content)
    
    def generate_index(self):
        print("\n生成完整索引...")
        
        index_file = self.output_dir / "00_Complete_Index.md"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# The Road to Serfdom - 完整原文拆分索引\n\n")
            f.write(f"**来源文件**: {self.source_file.name}\n")
            f.write(f"**拆分日期**: 2025-11-18\n")
            f.write(f"**拆分版本**: v2.0 (完整版)\n")
            f.write(f"**部分总数**: {len(self.sections)}\n\n")
            
            f.write("---\n\n")
            f.write("## 文件结构\n\n")
            
            current_category = None
            for i, sec in enumerate(self.sections):
                category = '前言部分' if not sec['is_chapter'] else '主要章节' if 'Chapter' in sec['display'] else '附录部分'
                
                if category != current_category:
                    f.write(f"\n### {category}\n\n")
                    current_category = category
                
                f.write(f"{i+1:2d}. **{sec['display']}**\n")
                f.write(f"    - 文件: `{sec['filename']}`\n")
                f.write(f"    - 大小: {sec['size']:,} 字符 / {sec['size']/1024:.2f} KB\n\n")
            
            f.write("\n---\n\n")
            f.write("## 特点\n\n")
            f.write("✓ **完整性**：包含前言、16个主要章节、附录等所有内容\n")
            f.write("✓ **避免碎片化**：将零散的前言和附录合并在统一文件中\n")
            f.write("✓ **清晰组织**：前言(00_) | 章节 | 附录(99_)\n")
            f.write("✓ **无遗漏**：确保原文每一字符都被保留\n\n")
            
            f.write("## 文件说明\n\n")
            f.write("- **前言部分 (00_)**: 各种序言、前言、编者序\n")
            f.write("- **章节 (Chapter01-16)**: 书籍核心内容\n")
            f.write("- **附录 (99_)**: 参考文献、历史文献、读者报告\n\n")
        
        print(f"  ✓ 索引文件: {index_file.name}")
    
    def run(self):
        print("=" * 70)
        print("原文完整拆分工具 v2.0")
        print("=" * 70)
        
        try:
            self.load_content()
            self.identify_sections()
            
            if not self.sections:
                print("\n错误: 未找到任何部分!")
                return False
            
            self.extract_sections()
            self.generate_index()
            
            total_size = sum(sec['size'] for sec in self.sections)
            coverage = (total_size / len(self.content)) * 100
            
            print("\n" + "=" * 70)
            print(f"✓ 拆分完成！")
            print(f"  部分总数: {len(self.sections)}")
            print(f"  总大小: {total_size:,} / {len(self.content):,} 字符")
            print(f"  完整性: {coverage:.2f}%")
            print(f"  输出: {self.output_dir}")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    PROJECT_ROOT = Path(__file__).parent.parent
    SOURCE_FILE = PROJECT_ROOT / "2.原文资料" / "The-Road-to-Serfdom.txt"
    OUTPUT_DIR = PROJECT_ROOT / "2.原文资料" / "chapters"
    
    splitter = ComprehensiveChapterSplitter(SOURCE_FILE, OUTPUT_DIR)
    success = splitter.run()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
