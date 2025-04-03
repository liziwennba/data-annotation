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
