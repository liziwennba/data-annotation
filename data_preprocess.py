import json
import open3d as o3d
import numpy as np
for i in os.listdir('your/path/to/dataset'):
    name = i 
    with open(f'D:\\bendi\lidarSLAM\scenes\\{name}\\segments_anno.json','r') as f:
        a = json.load(f)
    pcd = o3d.io.read_point_cloud(f'D:\\bendi\lidarSLAM\scenes\\{name}\\mesh_aligned_0.05.ply')
    points = np.asarray(pcd.points)
    mask = np.zeros((points.shape[0]))
    for i in a['segGroups']:
        mask[np.array(i['segments'])] = i['objectId']
        np.save(f'D:\\bendi\lidarSLAM\scenes\\{name}\\instance.npy',mask)