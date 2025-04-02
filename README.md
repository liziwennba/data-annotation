# 3D场景标注工具使用说明

本工具是一个基于 3D 场景的标注工具，支持通过可视化界面点选物体并添加标注描述。以下是详细的使用流程和注意事项。

---

## **安装与启动**

1. **安装依赖**：
   - 确保您已经安装了 Python 环境（建议 Python 3.8 及以上）。
   - 使用以下命令安装所需依赖：
     ```bash
     pip install open3d pyqt5 numpy
     ```

2. **启动软件**：
   - 运行以下命令启动标注工具：
     ```bash
     python test_.py
     ```
   - 启动后，您将看到主界面，如下图所示：  
     ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/1.png)

---

## **数据准备**

1. **解压数据集**：
   - 将下载好的数据压缩包解压，目录结构应类似如下：
     ```
     path/to/dataset/XXX
     ```
     其中 `XXX` 是各个场景的名称。

2. **选择场景文件夹**：
   - 在软件中点击 **选择场景文件夹** 按钮，选择某个场景文件夹（例如 `XXX`）。
   - 选择后，软件会加载该场景的 `.ply` 文件（3D 模型）和 `.npy` 文件（实例掩码）。
   - ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/2.png)

---

## **标注流程**

### **1. 可视化场景**
- 点击 **可视化场景** 按钮，加载并观察整个场景模型。  
- ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/3.png)
- 可视化场景
- ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/11.png)
---

### **2. 添加标注**
1. **输入描述**：
   - 在左侧 **物体描述** 输入框中，输入需要标注的问题描述。例如：
     ```
     我刚洗完澡，背对淋浴器和花洒，请帮我分割出挂在暖气片上离我最近的可以用来擦干身体的物体。
     ```
   - ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/5.png)

2. **点选物体**：
   - 点击 **添加描述并点选物体** 按钮，进入点选模式。
   - 软件会弹出可视化窗口，如下图所示：  
     ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/12.png)
   - 在界面中，将鼠标移动到目标物体上的一个点，**按住 Shift 并左键点击**，完成点选。
   - 添加完所有物体后，关闭点选窗口。

3. **确认可视化**：
   - 点选完成后关闭窗口并选择yes，软件会弹出一个窗口，显示您选择的物体高亮可视化效果：  
     ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/7.png)
     ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/13.png)
   - 如果可视化正确，关闭窗口并进行下一个问题的描述和点选。
   - 如果可视化不正确，可在右侧**已保存的标注**列表中选择错误的描述，点击 **删除选中标注** 按钮进行删除。  
     ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/9.png)

---

### **3. 保存标注**
- 完成所有问题的标注后，点击 **保存所有标注** 按钮，将标注结果保存为 JSON 文件。
- ![软件界面](https://github.com/liziwennba/data-annotation/raw/main/10.png)

---

### **4. 标注下一个场景**
- 点击 **选择场景文件夹**，选择新的场景目录，重复上述步骤。

---

## **注意事项**
1. **场景切换时的标注显示**：
   - 选择新场景后，之前场景的标注会继续显示在列表中（这是一个bug）。
   - 但输入第一个描述并点选保存后，旧的标注会消失，不影响操作。

2. **点选技巧**：
   - 点选时需确保按住 **Shift** 键，并点击目标物体的合适位置。

3. **标注保存**：
   - 每完成一个场景的标注，务必点击 **保存所有标注**，避免数据丢失。

---

通过上述流程，您可以高效完成 3D 场景的标注任务。如有问题，请联系技术支持团队。
