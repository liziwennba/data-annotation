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

![软件界面](https://github.com/liziwennba/data-annotation/raw/main/1.png)

---

## 📁 数据准备 Data Preparation

### 1. 解压并查看场景目录 Unpack and inspect scene folder
```bash
path/to/dataset/XXX
```
其中 `XXX` 为场景编号 / `XXX` is the scene folder name.

### 2. 选择场景文件夹 Select scene folder
点击 **选择场景文件夹** 按钮并选择场景目录。系统将自动读取 `.ply` 与 `.npy` 文件。
Click `选择场景文件夹` and select a folder. The tool will automatically load the mesh and mask files.

![加载界面](https://github.com/liziwennba/data-annotation/raw/main/2.png)

---

## 📝 标注流程 Annotation Workflow

### 🔍 步骤一：可视化场景 Visualize Scene
- 点击 **可视化场景** 以查看场景全貌
Click `可视化场景` to open a viewer.

![视图](https://github.com/liziwennba/data-annotation/raw/main/3.png)
![视图2](https://github.com/liziwennba/data-annotation/raw/main/11.png)

---

### 🖊 步骤二：添加标注 Add Annotation

#### 1. 输入描述 Enter a description
在左侧输入框中输入自然语言描述，如：
```text
我刚洗完澡，背对淋浴器和花洒，请帮我分割出挂在暖气片上离我最近的可以用来擦干身体的物体。
```

![输入框](https://github.com/liziwennba/data-annotation/raw/main/5.png)

#### 2. 点选物体 Select objects by clicking
点击 `添加描述并点选物体`，进入点选窗口。
Click `添加描述并点选物体` to open the interactive selection window.

![点选](https://github.com/liziwennba/data-annotation/raw/main/12.png)

在窗口中按住 **Shift + 左键** 点击目标物体上的点。
Hold **Shift** and left-click to pick points.

#### 3. 可视化确认 Visual confirmation
成功点选后将弹出高亮实例视图窗口：

![可视化1](https://github.com/liziwennba/data-annotation/raw/main/7.png)
![可视化2](https://github.com/liziwennba/data-annotation/raw/main/13.png)

如需删除错误标注，请在右侧点击 `删除选中标注`：

![删除按钮](https://github.com/liziwennba/data-annotation/raw/main/9.png)

---

### 💾 步骤三：保存标注 Save Annotations

点击 `保存所有标注` 保存当前所有标注。
Click `保存所有标注` to store annotations as JSON.

![保存界面](https://github.com/liziwennba/data-annotation/raw/main/10.png)

---

### 📂 步骤四：标注下一个场景 Annotate Next Scene

点击 `选择场景文件夹` 重新选择其他场景。
Repeat previous steps for each new scene.

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
scene0005_00/
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
