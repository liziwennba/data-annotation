import sys
import os
import json
import open3d as o3d
import numpy as np
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QFileDialog, QLabel, QTextEdit, 
                            QListWidget, QMessageBox, QListWidgetItem, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def dict_to_camera_params(param_dict):
    """Convert a dictionary to Open3D PinholeCameraParameters"""
    if not param_dict:
        return None
        
    params = o3d.camera.PinholeCameraParameters()
    
    # Set intrinsic parameters
    intrinsic = o3d.camera.PinholeCameraIntrinsic()
    intrinsic.width = param_dict["intrinsic"]["width"]
    intrinsic.height = param_dict["intrinsic"]["height"]
    intrinsic.set_intrinsics(
        intrinsic.width, 
        intrinsic.height,
        param_dict["intrinsic"]["fx"],
        param_dict["intrinsic"]["fy"],
        param_dict["intrinsic"]["cx"],
        param_dict["intrinsic"]["cy"]
    )
    params.intrinsic = intrinsic
    
    # Set extrinsic parameters
    params.extrinsic = np.array(param_dict["extrinsic"])
    
    return params

class MeshAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("3D场景标注工具")
        self.setGeometry(100, 100, 1000, 800)
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 顶部控制区域
        top_layout = QHBoxLayout()
        
        self.scene_path_label = QLabel("当前场景: 未选择")
        self.browse_button = QPushButton("选择场景文件夹")
        self.browse_button.clicked.connect(self.browse_scene_directory)
        
        self.visualize_button = QPushButton("可视化场景")
        self.visualize_button.clicked.connect(self.visualize_scene)
        self.visualize_button.setEnabled(False)
        
        top_layout.addWidget(self.scene_path_label)
        top_layout.addWidget(self.browse_button)
        top_layout.addWidget(self.visualize_button)
        
        main_layout.addLayout(top_layout)
        
        # 中部布局 - 分为左侧描述区和右侧标注列表
        mid_layout = QHBoxLayout()
        
        # 左侧 - 描述输入区
        left_layout = QVBoxLayout()
        self.description_label = QLabel("物体描述:")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("请输入物体描述...")
        
        self.add_description_button = QPushButton("添加描述并点选物体")
        self.add_description_button.clicked.connect(self.add_description)
        self.add_description_button.setEnabled(False)
        
        left_layout.addWidget(self.description_label)
        left_layout.addWidget(self.description_input)
        left_layout.addWidget(self.add_description_button)
        
        # 相机保存模式按钮 - 添加到左侧布局
        self.camera_mode_button = QPushButton("启用相机保存模式")
        self.camera_mode_button.setCheckable(True)  # 使按钮可切换
        self.camera_mode_button.clicked.connect(self.toggle_camera_mode)
        self.camera_mode_button.setEnabled(False)
        
        self.save_camera_button = QPushButton("设置/查看标注相机视角")
        self.save_camera_button.clicked.connect(self.save_camera_view)
        self.save_camera_button.setEnabled(False)
        
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(self.camera_mode_button)
        camera_layout.addWidget(self.save_camera_button)
        
        left_layout.addLayout(camera_layout)
        
        # 右侧 - 标注列表
        right_layout = QVBoxLayout()
        self.annotations_label = QLabel("已保存的标注:")
        self.annotations_list = QListWidget()
        self.annotations_list.itemClicked.connect(self.annotation_selected)
        
        self.view_annotation_button = QPushButton("查看选中标注")
        self.view_annotation_button.clicked.connect(self.view_annotation)
        self.view_annotation_button.setEnabled(False)
        
        self.edit_annotation_button = QPushButton("编辑选中标注")  # 新增编辑按钮
        self.edit_annotation_button.clicked.connect(self.edit_annotation)
        self.edit_annotation_button.setEnabled(False)
        
        self.delete_annotation_button = QPushButton("删除选中标注")
        self.delete_annotation_button.clicked.connect(self.delete_annotation)
        self.delete_annotation_button.setEnabled(False)
        
        self.save_annotations_button = QPushButton("保存所有标注")
        self.save_annotations_button.clicked.connect(self.save_annotations)
        self.save_annotations_button.setEnabled(False)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.view_annotation_button)
        buttons_layout.addWidget(self.edit_annotation_button)  # 将编辑按钮添加到布局
        buttons_layout.addWidget(self.delete_annotation_button)
        
        right_layout.addWidget(self.annotations_label)
        right_layout.addWidget(self.annotations_list)
        right_layout.addLayout(buttons_layout)
        right_layout.addWidget(self.save_annotations_button)
        
        # 将左右区域添加到中部布局
        mid_layout.addLayout(left_layout, 3)  # 左侧占3份
        mid_layout.addLayout(right_layout, 2)  # 右侧占2份
        
        main_layout.addLayout(mid_layout)
        
        # 底部状态栏
        self.status_label = QLabel("状态: 准备就绪")
        main_layout.addWidget(self.status_label)
        
        # 存储场景相关信息
        self.scene_dir = ""
        self.scene_name = ""
        self.mesh_path = ""
        self.instance_mask_path = ""
        self.mesh = None
        self.instance_mask = None
        self.camera_pose = None
        self.present_params = None
        
        # 存储标注数据
        self.annotations = []
        self.current_annotation_index = -1
        
        # 标注文件路径
        self.annotations_file_path = ""
        
        # 点选的物体ID
        self.selected_object_ids = []
        
        # 相机模式设置
        self.camera_mode_enabled = False
        
        # 默认相机参数 - 初始化为空字典
        self.default_camera_params = {}
        
        # 跟踪标注是否已修改但尚未保存
        self.annotations_modified = False
        
    def toggle_camera_mode(self):
        """切换相机保存模式"""
        self.camera_mode_enabled = self.camera_mode_button.isChecked()
        
        if self.camera_mode_enabled:
            self.camera_mode_button.setText("关闭相机保存模式")
            self.save_camera_button.setEnabled(True)
            self.status_label.setText("状态: 相机保存模式已启用")
        else:
            self.camera_mode_button.setText("启用相机保存模式")
            self.save_camera_button.setEnabled(False)
            self.status_label.setText("状态: 相机保存模式已关闭")
            
    def save_camera_view(self):
        """设置或查看相机视角"""
        if not self.camera_mode_enabled:
            QMessageBox.warning(self, "模式错误", "请先启用相机保存模式")
            return
            
        #if self.current_annotation_index < 0 or self.current_annotation_index >= len(self.annotations):
        #    QMessageBox.warning(self, "选择错误", "请先选择一个标注")
        #    return
            
        if not self.mesh_path:
            QMessageBox.warning(self, "文件错误", "未找到mesh文件")
            return
            
        try:
            # 加载mesh，如果尚未加载
            if not self.mesh:
                self.mesh = o3d.io.read_triangle_mesh(self.mesh_path)
                
                # 如果mesh没有顶点颜色，添加默认颜色
                if not self.mesh.has_vertex_colors():
                    vertices = np.asarray(self.mesh.vertices)
                    colors = np.ones((len(vertices), 3)) * 0.7  # 灰色
                    self.mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
            
            # 创建mesh的副本，用于可视化
            vis_mesh = o3d.geometry.TriangleMesh(self.mesh)
            
            ## 获取当前标注
            has_camera_params = False
            if self.current_annotation_index > 0 and self.current_annotation_index < len(self.annotations):
                annotation = self.annotations[self.current_annotation_index]
                object_ids = annotation["object_ids"]
                # 检查标注中是否已有相机参数
                has_camera_params = "camera_params" in annotation and annotation["camera_params"]
                #print(annotation["camera_params"])
                #print(has_camera_params)
                # 高亮显示标注的物体
                if self.instance_mask is not None and len(object_ids) > 0:
                    # 获取顶点和颜色
                    vertices = np.asarray(vis_mesh.vertices)
                    colors = np.asarray(vis_mesh.vertex_colors).copy()
                    
                    # 计算高亮点
                    highlight_mask = np.zeros(len(self.instance_mask), dtype=bool)
                    for obj_id in object_ids:
                        highlight_mask |= (self.instance_mask == obj_id)
                    
                    # 将高亮点设置为绿色
                    colors[highlight_mask] = [0, 1, 0]  # 绿色
                    
                    # 更新mesh颜色
                    vis_mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
            
            # 设置窗口标题
            window_title = f"设置相机视角 - 标注 #{self.current_annotation_index + 1}"
            
            
            
            # 创建可视化窗口
            window_width = 1024
            window_height = 768
            vis = o3d.visualization.Visualizer()
            vis.create_window(window_name=window_title, width=window_width, height=window_height)
            vis.add_geometry(vis_mesh)
            
            # 添加坐标系
            coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
            vis.add_geometry(coordinate_frame)
            
            # 设置渲染选项
            opt = vis.get_render_option()
            opt.background_color = np.array([1.0, 1.0, 1.0])  # 白色背景
            
            # 如果标注中已有相机参数，则恢复视角
            view_control = vis.get_view_control()
            #print(has_camera_params)
            if has_camera_params:
                try:
                    # 恢复保存的相机参数
                    params_dict = annotation["camera_params"]
                    #vis_params = annotation["vis_params"]
                    vis_params = dict_to_camera_params(params_dict)
                    # 设置外参矩阵 - 使用view_control的底层方法
                    extrinsic = np.array(params_dict["extrinsic"])
                    view_control.convert_from_pinhole_camera_parameters(vis_params,True)
                    
                    self.status_label.setText("状态: 已恢复保存的相机视角")
                except Exception as e:
                    self.status_label.setText(f"状态: 恢复相机视角出错: {str(e)}")
            elif self.present_params:
                try:
                    # 恢复保存的相机参数
                    #params_dict = annotation["camera_params"]
                    #vis_params = annotation["vis_params"]
                    vis_params = self.present_params
                    # 设置外参矩阵 - 使用view_control的底层方法
                    #extrinsic = np.array(params_dict["extrinsic"])
                    view_control.convert_from_pinhole_camera_parameters(vis_params,True)
                    
                    self.status_label.setText("状态: 已恢复保存的相机视角")
                except Exception as e:
                    self.status_label.setText(f"状态: 恢复相机视角出错: {str(e)}")
            #print(has_camera_params)
            # 运行可视化器
            vis.run()
            
            # 获取最终的相机参数
            final_params = view_control.convert_to_pinhole_camera_parameters()
            
            # 提取相机外参和内参
            extrinsic = final_params.extrinsic
            intrinsic = {
                "width": final_params.intrinsic.width,
                "height": final_params.intrinsic.height,
                "fx": final_params.intrinsic.get_focal_length()[0],
                "fy": final_params.intrinsic.get_focal_length()[1],
                "cx": final_params.intrinsic.get_principal_point()[0],
                "cy": final_params.intrinsic.get_principal_point()[1]
            }
            
            # 关闭可视化窗口
            vis.destroy_window()
            
            # 从外参矩阵中提取相机位置和朝向
            camera_position = -np.array([extrinsic[0, 3], extrinsic[1, 3], extrinsic[2, 3]])
            camera_direction = -np.array([extrinsic[2, 0], extrinsic[2, 1], extrinsic[2, 2]])
            up_vector = np.array([extrinsic[1, 0], extrinsic[1, 1], extrinsic[1, 2]])
            self.camera_pose = {
                "extrinsic": extrinsic.tolist(),
                "intrinsic": intrinsic,
                "position": camera_position.tolist(),
                "direction": camera_direction.tolist(),
                "up": up_vector.tolist()
            }
            self.present_params = final_params
            # 保存相机参数到标注中
            if self.current_annotation_index > 0 and self.current_annotation_index < len(self.annotations):
                annotation["camera_params"] = self.camera_pose
                self.annotations_modified = True  # 标记标注已修改
            #    annotation["vis_params"] = self.present_params
            # 更新界面
            self.status_label.setText("状态: 已保存相机视角到当前标注")
            QMessageBox.information(self, "保存成功", "已保存相机视角到当前标注")
            
        except Exception as e:
            self.status_label.setText(f"状态: 设置相机视角时出错: {str(e)}")
            QMessageBox.warning(self, "错误", f"设置相机视角时出错: {str(e)}")
            
    def browse_scene_directory(self):
        """浏览并选择场景目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择场景目录", "")
        
        if not dir_path:
            return
        
        # 如果已有修改的标注且未保存，先询问是否保存
        if self.annotations and self.annotations_modified:
            reply = QMessageBox.question(self, '保存标注', 
                                        '当前场景的标注已修改但尚未保存。\n是否在加载新场景前保存标注？',
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                                        QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.save_annotations()
            elif reply == QMessageBox.Cancel:
                return  # 取消加载新场景
        
        self.scene_dir = dir_path
        self.scene_name = os.path.basename(dir_path)
        self.scene_path_label.setText(f"当前场景: {self.scene_name}")
        
        # 查找场景中的文件
        self.find_scene_files()
        
    def find_scene_files(self):
        """查找场景目录中的相关文件"""
        if not self.scene_dir or not self.scene_name:
            return
        
        self.status_label.setText(f"状态: 正在查找场景 {self.scene_name} 的文件...")
        
        # 查找ply文件
        ply_files = [f for f in os.listdir(self.scene_dir) if f.endswith('.ply')]
        
        # 修改优先级：首先查找"mesh_aligned_0.05.ply"文件
        mesh_file = None
        
        # 第一优先级：mesh_aligned_0.05.ply
        if "mesh_aligned_0.05.ply" in ply_files:
            mesh_file = "mesh_aligned_0.05.ply"
        # 第二优先级：与场景同名的ply文件
        elif f"{self.scene_name}.ply" in ply_files:
            mesh_file = f"{self.scene_name}.ply"
        # 第三优先级：mesh.ply
        elif "mesh.ply" in ply_files:
            mesh_file = "mesh.ply"
        # 如果都没找到，使用第一个ply文件
        elif ply_files:
            mesh_file = ply_files[0]
        
        if mesh_file:
            self.mesh_path = os.path.join(self.scene_dir, mesh_file)
            self.status_label.setText(f"状态: 找到mesh文件 {mesh_file}")
        else:
            self.status_label.setText("状态: 未找到mesh文件")
            QMessageBox.warning(self, "文件错误", "在选中的目录中没有找到ply文件")
            return
        
        # 查找npy文件
        npy_files = [f for f in os.listdir(self.scene_dir) if f.endswith('.npy')]
        
        # 优先查找带有instance或instances的npy文件
        instance_file = None
        for npy_file in npy_files:
            if "instance" in npy_file.lower():
                instance_file = npy_file
                break
        
        # 如果没找到，使用第一个npy文件
        if not instance_file and npy_files:
            instance_file = npy_files[0]
        
        if instance_file:
            self.instance_mask_path = os.path.join(self.scene_dir, instance_file)
            self.status_label.setText(f"状态: 找到实例掩码文件 {instance_file}")
        else:
            self.status_label.setText("状态: 未找到实例掩码文件")
            QMessageBox.warning(self, "文件错误", "在选中的目录中没有找到npy文件")
            return
        
        # 尝试加载实例掩码
        try:
            self.instance_mask = np.load(self.instance_mask_path)
            self.status_label.setText(f"状态: 已加载实例掩码，包含 {len(np.unique(self.instance_mask))} 个实例")
        except Exception as e:
            self.status_label.setText(f"状态: 无法加载实例掩码: {str(e)}")
            QMessageBox.warning(self, "加载错误", f"无法加载实例掩码文件: {str(e)}")
            return
        
        # 尝试加载annotations文件
        self.annotations_file_path = os.path.join(self.scene_dir, f"{self.scene_name}_annotations.json")
        if os.path.exists(self.annotations_file_path):
            try:
                with open(self.annotations_file_path, 'r', encoding='utf-8') as f:
                    self.annotations = json.load(f)
                    
                # 检查所有标注是否都有相机参数字段
                for annotation in self.annotations:
                    if "camera_params" not in annotation:
                        annotation["camera_params"] = {}
                        #annotation["vis_params"] = {}
                self.update_annotations_list()
                self.status_label.setText(f"状态: 已加载 {len(self.annotations)} 条标注")
            except Exception as e:
                self.status_label.setText(f"状态: 无法加载标注文件: {str(e)}")
                QMessageBox.warning(self, "加载错误", f"无法加载标注文件: {str(e)}")
                self.annotations = []
        else:
            self.annotations = []
            self.status_label.setText("状态: 未找到现有标注文件，将创建新文件")
        
        # 重置修改标志
        self.annotations_modified = False
        
        # 启用可视化和标注按钮
        self.visualize_button.setEnabled(True)
        self.add_description_button.setEnabled(True)
        self.save_annotations_button.setEnabled(True)
        self.camera_mode_button.setEnabled(True)  # 启用相机模式按钮
        
    def update_annotations_list(self):
        """更新标注列表显示"""
        self.annotations_list.clear()
        for i, annotation in enumerate(self.annotations):
            description = annotation["description"]
            num_objects = len(annotation["object_ids"])
            has_camera = "camera_params" in annotation and annotation["camera_params"]
            
            item_text = f"{i+1}. {description[:30]}... [{num_objects}个实例]"
            if len(description) <= 30:
                item_text = f"{i+1}. {description} [{num_objects}个实例]"
                
            # 添加相机图标表示有相机参数
            if has_camera:
                item_text += " 📷"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)  # 存储索引便于后续访问
            self.annotations_list.addItem(item)
            
    def annotation_selected(self, item):
        """处理标注列表选择事件"""
        self.current_annotation_index = item.data(Qt.UserRole)
        self.view_annotation_button.setEnabled(True)
        self.edit_annotation_button.setEnabled(True)  # 启用编辑按钮
        self.delete_annotation_button.setEnabled(True)
        
        # 如果相机保存模式启用，则启用保存相机按钮
        if self.camera_mode_enabled:
            self.save_camera_button.setEnabled(True)
            
    def visualize_scene(self):
        """可视化场景模型"""
        if not self.mesh_path:
            QMessageBox.warning(self, "可视化错误", "未找到mesh文件")
            return
        
        try:
            self.status_label.setText("状态: 正在加载mesh...")
            
            # 加载mesh
            self.mesh = o3d.io.read_triangle_mesh(self.mesh_path)
            
            # 如果mesh没有顶点颜色，添加默认颜色
            if not self.mesh.has_vertex_colors():
                vertices = np.asarray(self.mesh.vertices)
                colors = np.ones((len(vertices), 3)) * 0.7  # 灰色
                self.mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
            
            # 可视化mesh
            coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
            vis = o3d.visualization.Visualizer()
            window_width = 1024
            window_height = 768
            vis.create_window(window_name=f"场景: {self.scene_name}", width=window_width, height=window_height)
            vis.add_geometry(self.mesh)
            vis.add_geometry(coordinate_frame)
            
            # 设置为白色背景
            opt = vis.get_render_option()
            opt.background_color = np.array([1.0, 1.0, 1.0])  # 白色背景
            
            # 运行可视化器
            vis.run()
            
            # 保存默认视角参数，以备后用
            view_control = vis.get_view_control()
            self.default_camera_params = view_control.convert_to_pinhole_camera_parameters()
            
            vis.destroy_window()
            
            self.status_label.setText(f"状态: 已可视化场景 {self.scene_name}")
            
        except Exception as e:
            self.status_label.setText(f"状态: 可视化失败: {str(e)}")
            QMessageBox.warning(self, "可视化错误", f"无法可视化场景: {str(e)}")
            
    def add_description(self):
        """添加描述并启动点选模式"""
        description = self.description_input.toPlainText().strip()
        
        if not description:
            QMessageBox.warning(self, "描述错误", "请先输入描述")
            return
        
        # 检查mesh和实例掩码是否加载
        if not self.mesh_path or not self.instance_mask_path:
            QMessageBox.warning(self, "文件错误", "请先选择包含mesh和实例掩码的场景目录")
            return
        
        # 点选逻辑
        if not self.mesh:
            try:
                self.mesh = o3d.io.read_triangle_mesh(self.mesh_path)
                
                # 如果mesh没有顶点颜色，添加默认颜色
                if not self.mesh.has_vertex_colors():
                    vertices = np.asarray(self.mesh.vertices)
                    colors = np.ones((len(vertices), 3)) * 0.7  # 灰色
                    self.mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
            except Exception as e:
                self.status_label.setText(f"状态: 加载mesh失败: {str(e)}")
                QMessageBox.warning(self, "加载错误", f"无法加载mesh: {str(e)}")
                return
        
        try:
            self.status_label.setText("状态: 进入点选模式，按住Shift并点击物体以选择实例...")
            
            # 创建点云以进行点选
            # 我们从mesh获取点并使用顶点颜色
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(np.asarray(self.mesh.vertices))
            pcd.colors = o3d.utility.Vector3dVector(np.asarray(self.mesh.vertex_colors))
            
            # 创建坐标系
            coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
            
            # 创建点选可视化器
            vis = o3d.visualization.VisualizerWithEditing()
            vis.create_window(window_name=f"点选模式 - {description}", width=1024, height=768)
            vis.add_geometry(pcd)
            vis.add_geometry(coordinate_frame)
            
            # 设置为白色背景
            opt = vis.get_render_option()
            opt.background_color = np.array([1.0, 1.0, 1.0])  # 白色背景
            opt.point_size = 3.0  # 增大点大小便于选择
            
            # 运行可视化器
            vis.run()
            vis.destroy_window()
            
            # 获取选中的点索引
            picked_indices = vis.get_picked_points()
            
            if not picked_indices:
                self.status_label.setText("状态: 未选择任何点，请重试")
                return
            
            # 获取选中点对应的实例ID
            self.selected_object_ids = []
            unique_instance_ids = set()
            
            # 提取所有被点选的点对应的实例ID
            vertices = np.asarray(self.mesh.vertices)
            if len(self.instance_mask) != len(vertices):
                self.status_label.setText(f"状态: 实例掩码大小 ({len(self.instance_mask)}) 与mesh顶点数 ({len(vertices)}) 不匹配")
                QMessageBox.warning(self, "数据错误", "实例掩码与mesh顶点数量不匹配")
                return
            
            for idx in picked_indices:
                if 0 <= idx < len(self.instance_mask):
                    instance_id = int(self.instance_mask[idx])
                    if instance_id > 0:  # 忽略ID为0的背景
                        unique_instance_ids.add(instance_id)
            
            if not unique_instance_ids:
                self.status_label.setText("状态: 未选择任何有效实例，请重试")
                QMessageBox.warning(self, "选择错误", "未选择任何有效实例，请确保点选的是有实例ID的区域")
                return
            
            # 将唯一实例ID添加到描述中
            self.selected_object_ids = list(unique_instance_ids)
            annotated_description = description
            for obj_id in self.selected_object_ids:
                annotated_description += f" [{obj_id}]"
            
            # 创建新的标注项
            if not self.camera_mode_enabled:
                new_annotation = {
                    "description": description,
                    "object_ids": self.selected_object_ids,
                    "full_text": annotated_description,
                    "camera_params": {},  # 初始化空的相机参数字段
                    #"vis_params":{}
                }
            else:
                new_annotation = {
                    "description": description,
                    "object_ids": self.selected_object_ids,
                    "full_text": annotated_description,
                    "camera_params": self.camera_pose,  # 初始化空的相机参数字段
                    #"vis_params":self.present_params
                }
            
            # 确认添加
            reply = QMessageBox.question(self, '确认添加标注', 
                                         f'确认添加以下标注？\n\n{annotated_description}\n\n选中了 {len(self.selected_object_ids)} 个实例',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.annotations.append(new_annotation)
                self.update_annotations_list()
                self.description_input.clear()
                self.status_label.setText(f"状态: 已添加标注，选中了 {len(self.selected_object_ids)} 个实例")
                self.annotations_modified = True  # 标记标注已修改
                
                # 可视化标注的实例
                self.visualize_selected_instances(self.selected_object_ids)
            else:
                self.status_label.setText("状态: 已取消添加标注")
            
        except Exception as e:
            self.status_label.setText(f"状态: 点选过程中出错: {str(e)}")
            QMessageBox.warning(self, "点选错误", f"点选过程出错: {str(e)}")
    
    def visualize_selected_instances(self, object_ids):
        """可视化选中的实例"""
        if not self.mesh or not self.instance_mask.any():
            return
        
        try:
            # 创建mesh的副本，以防修改原始mesh
            highlighted_mesh = o3d.geometry.TriangleMesh(self.mesh)
            
            # 获取顶点和颜色
            vertices = np.asarray(highlighted_mesh.vertices)
            colors = np.asarray(highlighted_mesh.vertex_colors).copy()
            
            # 计算高亮点
            highlight_mask = np.zeros(len(self.instance_mask), dtype=bool)
            for obj_id in object_ids:
                highlight_mask |= (self.instance_mask == obj_id)
            
            # 将高亮点设置为绿色
            colors[highlight_mask] = [0, 1, 0]  # 绿色
            
            # 更新mesh颜色
            highlighted_mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
            
            # 可视化
            coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
            vis = o3d.visualization.Visualizer()
            vis.create_window(window_name=f"选中的实例 - {len(object_ids)}个", width=1024, height=768)
            vis.add_geometry(highlighted_mesh)
            vis.add_geometry(coordinate_frame)
            
            # 设置为白色背景
            opt = vis.get_render_option()
            opt.background_color = np.array([1.0, 1.0, 1.0])  # 白色背景
            
            # 如果当前处于相机保存模式，且当前选择的标注有相机参数，则恢复相机视角
            if self.camera_mode_enabled and self.current_annotation_index >= 0 and self.current_annotation_index < len(self.annotations):
                annotation = self.annotations[self.current_annotation_index]
                if "camera_params" in annotation and annotation["camera_params"]:
                    try:
                        view_control = vis.get_view_control()
                        params_dict = annotation["camera_params"]
                        #vis_params = annotation["vis_params"]
                        vis_params = dict_to_camera_params(params_dict)
                        # 设置外参矩阵 - 使用view_control的底层方法
                        #extrinsic = np.array(params_dict["extrinsic"])
                        view_control.convert_from_pinhole_camera_parameters(vis_params,True)
                    except Exception as e:
                        print(f"恢复相机视角失败: {str(e)}")
            
            vis.run()
            vis.destroy_window()
            
            self.status_label.setText(f"状态: 已可视化 {len(object_ids)} 个选中实例")
            
        except Exception as e:
            self.status_label.setText(f"状态: 可视化选中实例时出错: {str(e)}")
            
    def view_annotation(self):
        """查看选中的标注"""
        if self.current_annotation_index < 0 or self.current_annotation_index >= len(self.annotations):
            return
        
        annotation = self.annotations[self.current_annotation_index]
        object_ids = annotation["object_ids"]
        
        # 查看是否有相机参数
        has_camera = "camera_params" in annotation and annotation["camera_params"]
        camera_info = "包含相机视角参数" if has_camera else "无相机视角参数"
        
        # 显示标注详情
        QMessageBox.information(self, "标注详情", 
                              f"描述: {annotation['description']}\n\n"
                              f"实例ID: {object_ids}\n\n"
                              f"完整文本: {annotation['full_text']}\n\n"
                              f"相机参数: {camera_info}")
        
        # 可视化标注的实例
        self.visualize_selected_instances(object_ids)
    
    def edit_annotation(self):
        """编辑选中的标注"""
        if self.current_annotation_index < 0 or self.current_annotation_index >= len(self.annotations):
            return
        
        annotation = self.annotations[self.current_annotation_index]
        current_description = annotation["description"]
        object_ids = annotation["object_ids"]
        
        # 创建编辑对话框
        dialog = QInputDialog(self)
        dialog.setWindowTitle("编辑标注")
        dialog.setLabelText("编辑描述:")
        dialog.setTextValue(current_description)
        dialog.resize(400, 200)  # 设置对话框大小
        
        if dialog.exec_():
            new_description = dialog.textValue().strip()
            
            if new_description and new_description != current_description:
                # 更新标注信息
                annotation["description"] = new_description
                
                # 更新完整文本
                new_full_text = new_description
                for obj_id in object_ids:
                    new_full_text += f" [{obj_id}]"
                annotation["full_text"] = new_full_text
                
                # 更新标注列表
                self.update_annotations_list()
                self.status_label.setText(f"状态: 已更新标注 #{self.current_annotation_index + 1}")
                self.annotations_modified = True  # 标记标注已修改
                
                # 显示编辑后的标注
                QMessageBox.information(self, "编辑成功", 
                                      f"已更新标注:\n\n"
                                      f"新描述: {new_description}\n\n"
                                      f"实例ID: {object_ids}\n\n"
                                      f"新完整文本: {new_full_text}")
            elif not new_description:
                QMessageBox.warning(self, "编辑错误", "描述不能为空")
            else:
                self.status_label.setText("状态: 描述未变更，标注保持不变")
        else:
            self.status_label.setText("状态: 已取消编辑标注")
            
    def delete_annotation(self):
        """删除选中的标注"""
        if self.current_annotation_index < 0 or self.current_annotation_index >= len(self.annotations):
            return
        
        reply = QMessageBox.question(self, '确认删除', 
                                    '确认要删除选中的标注吗？',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            del self.annotations[self.current_annotation_index]
            self.update_annotations_list()
            self.current_annotation_index = -1
            self.view_annotation_button.setEnabled(False)
            self.edit_annotation_button.setEnabled(False)  # 禁用编辑按钮
            self.delete_annotation_button.setEnabled(False)
            self.save_camera_button.setEnabled(False)  # 禁用相机按钮
            self.status_label.setText("状态: 已删除标注")
            self.annotations_modified = True  # 标记标注已修改
            
    def save_annotations(self):
        """保存所有标注"""
        if not self.annotations:
            QMessageBox.warning(self, "保存错误", "没有标注可保存")
            return
        
        if not self.annotations_file_path:
            self.annotations_file_path = os.path.join(self.scene_dir, f"{self.scene_name}_annotations.json")
        
        try:
            with open(self.annotations_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.annotations, f, indent=4, ensure_ascii=False)
            
            self.status_label.setText(f"状态: 已保存 {len(self.annotations)} 条标注到 {os.path.basename(self.annotations_file_path)}")
            QMessageBox.information(self, "保存成功", f"已保存 {len(self.annotations)} 条标注到\n{self.annotations_file_path}")
            self.annotations_modified = False  # 重置修改标志
            
        except Exception as e:
            self.status_label.setText(f"状态: 保存标注失败: {str(e)}")
            QMessageBox.warning(self, "保存错误", f"无法保存标注: {str(e)}")
    
    def closeEvent(self, event):
        """重写关闭事件处理函数，在关闭前询问是否保存标注"""
        if self.annotations and self.annotations_modified:
            reply = QMessageBox.question(self, '保存标注', 
                                        '标注已修改但尚未保存。\n是否在退出前保存标注？',
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                                        QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.save_annotations()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()  # 取消关闭
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建并显示主窗口
    annotator = MeshAnnotator()
    annotator.show()
    
    sys.exit(app.exec_())