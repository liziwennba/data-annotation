import os
import json
import re

def process_annotation(annotation, segments_data):
    """将旧格式的标注转换为新格式"""
    object_ids = annotation.get("object_ids", [])
    
    # 从segments_anno.json获取对象名称
    object_names = []
    for obj_id in object_ids:
        object_name = "unknown"  # 默认值
        # 在segments_data中查找对应的object_id
        for group in segments_data.get("segGroups", []):
            if group.get("objectId") == obj_id or group.get("id") == obj_id:
                object_name = group.get("label", "unknown")
                break
        object_names.append(object_name)
    
    # 处理description
    original_text = annotation.get("full_text", annotation.get("description", ""))
    
    # 如果存在"#"符号，删除[object_id]部分
    if "#" in original_text:
        description = re.sub(r'\s*\[\d+\]', '', original_text)
    else:
        # 否则，删除[object_id]并添加object_name
        description = re.sub(r'\s*\[\d+\]', '', original_text)
        # 如果没有标点符号结尾，添加一个空格和object_names (用[]括起来)
        if description and not description[-1] in ['.', '?', '!']:
            if not any(obj_name in description for obj_name in object_names):
                object_names_formatted = ", ".join(f"[{name}]" for name in object_names)
                description += " " + object_names_formatted
    
    # 创建新格式的标注
    new_annotation = {
        "object_id": object_ids,
        "object_name": object_names,
        "description": description
    }
    
    return new_annotation

def process_abs_annotation(annotation, segments_data):
    """处理_abs_annotations.json文件中的标注"""
    object_ids = annotation.get("object_ids", [])
    
    # 从segments_anno.json获取对象名称
    object_names = []
    for obj_id in object_ids:
        object_name = "unknown"  # 默认值
        # 在segments_data中查找对应的object_id
        for group in segments_data.get("segGroups", []):
            if group.get("objectId") == obj_id or group.get("id") == obj_id:
                object_name = group.get("label", "unknown")
                break
        object_names.append(object_name)
    
    # 获取距离，保留两位小数
    distance = round(annotation.get("distance_m", 0), 2)
    
    # 构建新的描述: 原始描述 + 第一个object_name + 距离 + 米的 + [第二个object_name]
    original_description = annotation.get("description", "")
    
    # 格式化描述
    if len(object_names) >= 2:
        new_description = f"{original_description} {object_names[0]} {distance}米的[{object_names[1]}]"
    elif len(object_names) == 1:
        new_description = f"{original_description} {object_names[0]} {distance}米"
    else:
        new_description = f"{original_description} {distance}米"
    
    # 创建新格式的标注
    new_annotation = {
        "object_id": object_ids,
        "object_name": object_names,
        "description": new_description
    }
    
    return new_annotation

def main():
    # 指定data目录路径
    data_dir = "data"
    
    # 遍历data目录下的所有文件夹
    for folder_name in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder_name)
        
        # 确保是目录
        if not os.path.isdir(folder_path):
            continue
        
        # 加载segments_anno.json
        segments_file = os.path.join(folder_path, "segments_anno.json")
        if not os.path.exists(segments_file):
            print(f"警告: 在{folder_path}中找不到segments_anno.json文件")
            continue
            
        try:
            # 加载segments文件
            with open(segments_file, 'r', encoding='utf-8') as f:
                segments_data = json.load(f)
                
            # 处理常规annotations文件
            annotations_file = os.path.join(folder_path, f"{folder_name}_annotations.json")
            if os.path.exists(annotations_file):
                # 加载annotation文件
                with open(annotations_file, 'r', encoding='utf-8') as f:
                    annotations = json.load(f)
                    
                # 处理每个标注
                processed_annotations = []
                for annotation in annotations:
                    processed_annotation = process_annotation(annotation, segments_data)
                    processed_annotations.append(processed_annotation)
                    
                # 保存处理后的标注
                processed_file = os.path.join(folder_path, "processed_annotations.json")
                with open(processed_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_annotations, f, ensure_ascii=False, indent=4)
                    
                print(f"成功处理并保存: {processed_file}")
            
            # 处理abs_annotations文件
            abs_annotations_file = os.path.join(folder_path, f"{folder_name}_abs_annotations.json")
            if os.path.exists(abs_annotations_file):
                # 加载abs_annotation文件
                with open(abs_annotations_file, 'r', encoding='utf-8') as f:
                    abs_annotations = json.load(f)
                    
                # 处理每个标注
                processed_abs_annotations = []
                for annotation in abs_annotations:
                    processed_annotation = process_abs_annotation(annotation, segments_data)
                    processed_abs_annotations.append(processed_annotation)
                    
                # 保存处理后的标注
                processed_abs_file = os.path.join(folder_path, "processed_abs_annotations.json")
                with open(processed_abs_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_abs_annotations, f, ensure_ascii=False, indent=4)
                    
                print(f"成功处理并保存: {processed_abs_file}")
                
            # 如果两个文件都不存在，打印警告
            if not os.path.exists(annotations_file) and not os.path.exists(abs_annotations_file):
                print(f"警告: 在{folder_path}中找不到{folder_name}_annotations.json或{folder_name}_abs_annotations.json文件")
                
        except Exception as e:
            print(f"处理{folder_path}时出错: {str(e)}")
            
if __name__ == "__main__":
    main()