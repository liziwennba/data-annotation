# 3D场景标注工具使用说明 / 3D Scene Annotation Tool Guide

本工具是一个基于 3D 场景的标注工具，支持通过可视化界面点选物体并添加标注描述。以下是详细的使用流程和注意事项。

---

## 🧰 安装与启动 Installation & Startup

### 1. 安装依赖 Install dependencies
- 推荐使用 Python 3.10.0
- Run the following command:

```bash
pip install open3d==0.18.0 pyqt5 numpy
```

### 2. 启动软件 Launch the tool
```bash
python test_.py
```

启动后界面如下 / Main window on launch:

![软件界面](https://github.com/liziwennba/data-annotation/raw/main/figures/1.png)

---

## 📁 数据准备 Data Preparation

### 1. 数据获取 Download Data

我们将通过 OneDrive 共享数据：
- 每位标注员仅需下载 `data/` 目录下自己负责的场景文件夹
- 文件夹格式为：`data/3db0a1c8f3/scans/`
- 下载后将 `scans` 文件夹 **重命名为对应场景名**，如 `3db0a1c8f3`

📌 结构示例：
```
data/
└── 3db0a1c8f3/
    ├── mesh_aligned_0.05.ply
    └── segments_anno.json
```


### 2. 预处理生成 instance.npy 文件
使用 `data_preprocess.py` 对每个场景文件夹进行预处理，生成每个场景独立的 `instance.npy` 掩码。

请将脚本路径替换为你的实际路径。示例代码如下：

```python
import os
import json
import open3d as o3d
import numpy as np

dataset_path = 'your/path/to/dataset' #CHANGE HERE

for i in os.listdir(dataset_path):
    name = i
    with open(f'{dataset_path}/{name}/segments_anno.json', 'r') as f:
        a = json.load(f)
    pcd = o3d.io.read_point_cloud(f'{dataset_path}/{name}/mesh_aligned_0.05.ply')
    points = np.asarray(pcd.points)
    mask = np.zeros((points.shape[0]))
    for seg in a['segGroups']:
        mask[np.array(seg['segments'])] = seg['objectId']
    np.save(f'{dataset_path}/{name}/instance.npy', mask)
```

运行完成后，每个场景目录下应包含：
```
3db0a1c8f3/
├── mesh_aligned_0.05.ply
├── segments_anno.json
└── instance.npy
```

### 2. 选择场景文件夹 Select scene folder
点击 **选择场景文件夹** 按钮并选择场景目录。系统将自动读取 `.ply` 与 `.npy` 文件。
Click `选择场景文件夹` and select a folder. The tool will automatically load the mesh and mask files.

![加载界面](https://github.com/liziwennba/data-annotation/raw/main/figures/2.png)

---

## 📝 标注流程 Annotation Workflow

### 🔍 步骤一：可视化场景 Visualize Scene
- 点击 **可视化场景** 以查看场景全貌
Click `可视化场景` to open a viewer.

![视图](https://github.com/liziwennba/data-annotation/raw/main/figures/3.png)
![视图2](https://github.com/liziwennba/data-annotation/raw/main/figures/11.png)

---

### 🖊 步骤二：添加标注 Add Annotation

#### 1. 输入描述 Enter a description
在左侧输入框中输入自然语言描述，如：
```text
站在门后，望向正前方，左手边的
```

![输入框](https://github.com/liziwennba/data-annotation/raw/main/figures/5.png)

#### 2. 点选物体 Select objects by clicking
点击 `添加描述并点选物体`，进入点选窗口。
Click `添加描述并点选物体` to open the interactive selection window.

![点选](https://github.com/liziwennba/data-annotation/raw/main/figures/12.png)

在窗口中按住 **Shift + 左键** 点击目标物体上的点。
Hold **Shift** and left-click to pick points.

#### 3. 可视化确认 Visual confirmation
成功点选后将弹出高亮实例视图窗口：

![可视化1](https://github.com/liziwennba/data-annotation/raw/main/figures/7.png)
![可视化2](https://github.com/liziwennba/data-annotation/raw/main/figures/13.png)

如需删除错误标注，请在右侧点击 `删除选中标注`：

![删除按钮](https://github.com/liziwennba/data-annotation/raw/main/figures/9.png)

---

### 💾 步骤三：保存标注 Save Annotations

点击 `保存所有标注` 保存当前所有标注。
Click `保存所有标注` to store annotations as JSON.

![保存界面](https://github.com/liziwennba/data-annotation/raw/main/figures/10.png)

---

### 📂 步骤四：标注下一个场景 Annotate Next Scene

点击 `选择场景文件夹` 重新选择其他场景。
Repeat previous steps for each new scene.

---

# 🧠 提问方式（四类模板）

# 第一视角问题处理指南

## 处理思路
**先定位 → 后寻找目标物体**
1. 通过场景中的显著定位点确定观察视角
2. 基于定位点描述目标物体的空间关系/特征

## 示例场景
![Scene Example](https://github.com/liziwennba/data-annotation/blob/main/figures/annotation_example_1.jpg)<!-- 替换实际图片路径 -->
- 有效定位点示例：
  - 刚进门背对（正对）着门
  - 坐在餐桌旁背对（正对）窗户的椅子上
  - 坐在沙发靠近窗户的一侧

## 定位点使用规范
以 `刚进门背对着门` 为例：
[![Position Example](path/to/position-image.jpg) ](https://github.com/liziwennba/data-annotation/blob/main/figures/annotation_example_2.png)<!-- 替换实际图片路径 -->

### 正确问题示例
1. **完整描述场景**  
   `刚进门背对着门，正对着我可以承载东西的物体是？#`

2. **动态补全描述**  
   `刚进门背对着门，正对我并离我最近的` + 点选【可以承载东西的物体】

3. **组合特征识别**  
   `刚进门背对着门，左手边的物体是？#`  
   `刚进门背对着门，左手边黄色的物体是？#`

### 错误问题示例
❌ `坐在椅子上` （定位模糊）  
❌ `刚进门背对着门，左边的东西` （缺少特征描述）

## 标注规范
| 场景类型 | 结尾符 | 说明 |
|---------|--------|-----|
| 完整问题 | `#` | 无需补充语义信息 |
| 待补全问题 | 无符号 | 需后接【特征描述】|

## 注意事项
- 🔍 定位描述必须满足：
  - 包含明确的场景坐标系（如背对/正对/左手边）
  - 使用可验证的参照物（门/窗/家具）
- ✏️ 物体描述应包含：
  - 功能性特征（可承载/可观赏）
  - 空间关系（正对/最近）
  - 显著物理特征（颜色/形状）

## ✅ 设计原则

| 原则       | 内容说明                                                                 |
|------------|--------------------------------------------------------------------------|
| 与视角无关 | ③/④类问题中不依赖“我站在…”等主观视角                                   |
| 明确无误   | 目标对象在当前上下文中指向唯一实例                                      |
| 简洁明了   | 避免冗余描述，符合 Grice 合理表达准则                                   |
| 实用场景   | 问题应具有生活动机背景，如洗澡、换衣、收纳等                            |

---

## ⚠️ 注意事项 Notes

1. **场景切换时的标注显示 Annotation carry-over**
   - 切换场景后原标注仍显示，这是界面更新的 bug，实际保存不受影响。
   - After selecting the next scene, the old annotation may temporarily display.

2. **点选技巧 Tips for point picking**
   - 必须按住 Shift 才能点选有效区域。
   - Hold Shift when clicking on objects.

3. **保存标注 Saving reminders**
   - 每完成一个场景后必须点击 `保存所有标注`！
   - Always click `保存所有标注` before moving on!

---

通过以上步骤，您即可完成一个完整的 3D 场景标注任务。

---

## 📦 Output Format

Example output JSON:

```json
{
  "description": "我坐在马桶上，面对暖气片...",
  "object_ids": [43, 44, 45],
  "full_text": "我坐在马桶上... [43] [44] [45]"
}
```
---

## 🧠 示例分类与判定标准（自然语言提问样例）

---

### 🧍 第一人称视角类（需判断视角 + 空间方位）

#### ✅ 不需要语义识别（仅凭位置唯一可定位） → 问句末尾加 `#`

| 类型       | 示例句 |
|------------|--------|
| ✅ 正例 | 坐在背靠白板的椅子看向室内，左手边最近的物体# |
| ✅ 正例 | 站在房间的正中央，面向窗户，前方最近的黄色物体# |
| ❌ 反例 | 站在房间的正中央，面向窗户，前方最近的物体（不唯一，缺少限制） |

#### ✅ 需要语义判断（必须结合语义类别才能定位）

| 类型       | 示例句 |
|------------|--------|
| ✅ 正例 | 站在房间的正中央，面向窗户，左边的【computer tower】 |
| ✅ 正例 | 站在房间的正中央，面向窗户，最近的【pen holder】 |

---

### 🧭 物体相对位置关系类（与视角无关，物体-物体间相对位置）

| 示例句 |
|--------|
| 主机上的【耳机】 |
| 在耳机下的【主机】 |
| 桌子上的【耳机】 |
| 最靠近桌边的【水瓶】 |
| 更远离门的【垃圾桶】 |
| 离白板最远的【椅子】 |

📌 特点：
- 关系描述清晰唯一
- 与“我站在…”无关

---

### 📏 绝对距离关系类（带有明确的测距信息）

| 示例句 |
|--------|
| 离靠近背靠白板的【椅子】【1米】【computer tower】 |
| 离靠近背靠白板的【椅子】【2米】【computer tower】 |
| 离【门】【0.5米】【垃圾桶】 |

📌 特点：
- 需要**参照物+目标物+距离**
- 用于多个目标中“精确选一个”

---

✅ 建议在每个标注文件中**混合不同类型的提问方式**，提高多样性与模型泛化能力。


---

## ✅ 标注指南 / Annotation Guidelines

| 项目 / Aspect      | 最佳实践 / Best Practice                                                   |
|--------------------|----------------------------------------------------------------------------|
| 描述 / Description | 使用自然、具备上下文的语言，并包含空间方位信息。<br>Use natural, context-rich language with spatial clues. |
| 点选对象 / Object Picking | 仅选择与意图描述相关的目标物体。<br>Only include objects relevant to the intention.              |
| 完整文本 / Full Text | 在描述末尾添加目标实例的编号，格式为 `[]`。<br>Append instance IDs in `[]` after the description. |

---

## 🔍 常见问题与解决方法 / Troubleshooting

| 问题 / Problem                     | 解决方案 / Solution                                                        |
|-----------------------------------|---------------------------------------------------------------------------|
| 未检测到 mesh 或 instance 文件 <br> No mesh/instance file detected | 确保选中的文件夹中包含 `.ply` 和 `.npy` 文件。<br>Ensure `.ply` and `.npy` exist in the selected folder. |
| 未选中任何点 <br> No points selected          | 点选时请按住 Shift 键并点击目标物体表面。<br>Shift + click only on valid object surfaces. |
| 无法保存标注 <br> Save fails                  | 确保添加了至少一个标注后再保存。<br>Check if annotations exist before saving. |

---

## 📂 Example Scene Folder Structure

```
07f5b601ee/
└── scans/
    ├── mesh_aligned_0.05.ply
    ├── instance_mask.npy
    └── scene0005_00_annotations.json
```

---

## 🧩 Future Improvements

- Multi-language UI support
- Support for segmentation overlay
- Annotation quality checking module

---

## 📜 License

This tool is intended for academic use only. Please cite or acknowledge the authors when used in publications.

---

## 🙌 Acknowledgments

- Developed by [MBZUAI / Ziwen Li, Jiaxin Huang, HanLve Zhang]
- Built using [Open3D](http://www.open3d.org/) and [PyQt5](https://pypi.org/project/PyQt5/)
- Dataset: [ScanNet++](https://kaldir.vc.in.tum.de/scannetpp/)

如有问题，请联系项目管理员。
For support, contact the project maintainer.
