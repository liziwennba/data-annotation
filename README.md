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

for i in os.listdir('your/path/to/dataset'):
    name = i
    with open(f'your/path/to/dataset/{name}/segments_anno.json', 'r') as f:
        a = json.load(f)
    pcd = o3d.io.read_point_cloud(f'your/path/to/dataset/{name}/mesh_aligned_0.05.ply')
    points = np.asarray(pcd.points)
    mask = np.zeros((points.shape[0]))
    for seg in a['segGroups']:
        mask[np.array(seg['segments'])] = seg['objectId']
    np.save(f'your/path/to/dataset/{name}/instance.npy', mask)
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
我刚洗完澡，背对淋浴器和花洒，请帮我分割出挂在暖气片上离我最近的可以用来擦干身体的物体。
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

## 🧠 提问方式（四类模板）

本项目支持以下四类结构化自然语言提问方式，用于生成高质量意图标注：

### ① 第一人称视角描述（主观 + 属性）

强调 **当前位置** + **观察方向** + **目标物体物理属性**

📌 结构：
> [当前位置参照物] + [朝向] + [目标物体属性（大小 / 颜色 / 形状）]

📎 示例：
> 我站在马桶旁，面对镜子和洗手台，请问地上那块**小的深灰色方形垫子**是哪一个？


### ② 空间位置唯一指代（结尾打上 #）

仅通过空间位置即可精准定位目标，无需提到物体属性或类别  
**要求目标位置在当前场景中具有唯一性**

📌 特点：
- 无需形容词修饰
- 与语义类别无关
- 句尾加 `#` 标记

📎 示例：
> 我面对卫生间门，门上**最靠近门把手的物体是？** #


### ③ 物体之间的相对空间关系（视角无关）

目标通过其与另一个物体的相对位置进行定位  
**与观察者视角无关，仅描述物体之间的空间关系**

📌 特点：
- “在…上方 / 左边 / 旁边”的结构
- 不依赖“我站在…”等主观视角描述

📎 示例：
> 挂在暖气片上，**在粉白色毛巾正上方的物体是？**


### ④ 多物体之间的绝对距离比较

通过“最近”、“最远”、“之间”等词，结合参照物明确目标  
**适用于多个同类物体中选取一个的情形**

📌 特点：
- 描述基于 **相对距离**
- 参照物需明确、唯一

📎 示例：
> 正对暖气片时，**距离粉白格子毛巾最近的可以穿的衣物是哪一件？**

---

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
