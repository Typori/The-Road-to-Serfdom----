#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
译文提取工具
功能：从翻译工作区的Markdown文件中提取纯译文
规则：
1. 只保留 [译文] 后的内容
2. 移除段落标识符 <!-- pX.sY -->
3. 保留章节划分
4. s切换时一个换行，p切换时两个换行
"""

import os
import re
import sys
from pathlib import Path


def extract_yaml_metadata(lines):
    """提取YAML头部的元数据"""
    metadata = {}
    in_yaml = False
    
    for line in lines:
        if line.strip() == '---':
            if in_yaml:
                break
            in_yaml = True
            continue
        
        if in_yaml:
            match = re.match(r'^(\w+):\s*"?([^"]+)"?$', line)
            if match:
                key, value = match.groups()
                metadata[key.strip()] = value.strip().strip('"')
    
    return metadata


def extract_translation(lines):
    """提取译文内容"""
    result = []
    in_translation = False
    prev_p = ""
    prev_s = ""
    pending_nbsp = False  # 标记是否需要在下一个内容前添加&nbsp;
    last_section_has_content = False  # 标记当前章节是否有内容
    
    for line in lines:
        # 检查章节标题
        section_match = re.match(r'^##\s+(.+)$', line)
        if section_match:
            section_title = section_match.group(1)
            # 跳过注释和修订记录部分
            if not re.search(r'^(注释|本章修订记录)', section_title):
                # 如果前一个章节有内容，在新章节前添加&nbsp;分隔
                if last_section_has_content:
                    result.append("")
                    result.append("&nbsp;")
                    result.append("")
                
                # 如果有待处理的&nbsp;，在标题前添加
                if pending_nbsp:
                    result.append("")
                    result.append("&nbsp;")
                    result.append("")
                    pending_nbsp = False
                
                result.append("")
                result.append(f"## {section_title}")
                result.append("")
                last_section_has_content = False
            in_translation = False
            prev_p = ""
            prev_s = ""
            pending_nbsp = False
            continue
        
        # 检查译文标记
        if line.strip() == '[译文]':
            in_translation = True
            continue
        
        if line.strip() == '[原文]':
            in_translation = False
            continue
        
        # 提取译文内容
        if in_translation and line.strip():
            # 跳过分隔符---
            if line.strip() == '---':
                continue
                
            # 移除段落标识符
            clean_line = re.sub(r'<!--\s*p\d+\.s\d+\s*-->', '', line)
            clean_line = clean_line.strip()
            
            if clean_line:
                # 提取段落和句子编号
                marker_match = re.search(r'<!--\s*p(\d+)\.s(\d+)\s*-->', line)
                if marker_match:
                    cur_p = marker_match.group(1)
                    cur_s = marker_match.group(2)
                    
                    # 根据p/s变化添加换行
                    if prev_p and prev_p != cur_p:
                        # p切换：标记需要在下一个内容前添加&nbsp;
                        pending_nbsp = True
                    elif prev_s and prev_s != cur_s:
                        # s切换：一个换行
                        result.append("")
                    
                    # 如果有待处理的&nbsp;，在添加内容前先添加
                    if pending_nbsp:
                        result.append("")
                        result.append("&nbsp;")
                        result.append("")
                        pending_nbsp = False
                    
                    prev_p = cur_p
                    prev_s = cur_s
                
                result.append(clean_line)
                last_section_has_content = True
    
    return result


def build_output(metadata, translation):
    """构建最终输出"""
    output = []
    
    # 添加标题
    if 'title' in metadata:
        output.append(f"# {metadata['title']}")
        output.append("")
    
    # 添加元数据信息
    if 'chapter' in metadata or 'revision' in metadata:
        meta_parts = []
        if 'chapter' in metadata:
            meta_parts.append(f"第 {metadata['chapter']} 章")
        if 'revision' in metadata:
            meta_parts.append(f"版本: {metadata['revision']}")
        if 'date' in metadata:
            meta_parts.append(f"日期: {metadata['date']}")
        
        if meta_parts:
            output.append(f"> {' | '.join(meta_parts)}")
            output.append("")
            output.append("---")
            output.append("")
    
    # 添加译文内容
    output.extend(translation)
    
    return output


def process_file(input_file, output_dir):
    """处理单个文件"""
    print(f"\n处理文件: {input_file.name}")
    
    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 去除行尾换行符
    lines = [line.rstrip('\r\n') for line in lines]
    
    # 提取元数据
    metadata = extract_yaml_metadata(lines)
    
    # 提取译文
    translation = extract_translation(lines)
    
    # 构建输出
    output = build_output(metadata, translation)
    
    # 生成输出文件名
    output_filename = f"{input_file.stem}_译文.md"
    output_file = output_dir / output_filename
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(output))
    
    print(f"  ✓ 已保存: {output_filename}")
    return output_file


def main():
    """主函数"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    # 设置工作目录和输出目录
    work_dir = root_dir / "3.翻译工作区"
    output_dir = root_dir / "4.译文"
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # 查找所有Markdown文件
    md_files = sorted(work_dir.glob("*.md"))
    
    if not md_files:
        print("错误：未找到Markdown文件")
        return 1
    
    print("=" * 60)
    print(" " * 20 + "译文提取工具")
    print("=" * 60)
    
    # 如果有多个文件，显示菜单
    if len(md_files) > 1:
        print("\n请选择要处理的文件：")
        for i, file in enumerate(md_files, 1):
            print(f"  [{i}] {file.name}")
        print("  [A] 全部文件")
        
        choice = input("\n请输入选择: ").strip().upper()
        
        if choice == 'A':
            # 处理所有文件
            print(f"\n正在处理 {len(md_files)} 个文件...\n")
            for file in md_files:
                try:
                    process_file(file, output_dir)
                except Exception as e:
                    print(f"  ✗ 错误: {e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(md_files):
            # 处理选中的文件
            try:
                output_file = process_file(md_files[int(choice) - 1], output_dir)
                print(f"\n完整路径: {output_file}")
            except Exception as e:
                print(f"  ✗ 错误: {e}")
                return 1
        else:
            print("无效的选择")
            return 1
    else:
        # 只有一个文件，直接处理
        try:
            output_file = process_file(md_files[0], output_dir)
            print(f"\n完整路径: {output_file}")
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            return 1
    
    print("\n" + "=" * 60)
    print(" " * 22 + "处理完成！")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
