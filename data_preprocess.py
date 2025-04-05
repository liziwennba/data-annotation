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
