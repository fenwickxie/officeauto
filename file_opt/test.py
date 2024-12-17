import os
import cv2
import numpy as np


def remove_duplicate_images(images_dir, n, beta):
	# Step 1: 获取图片路径列表
	images_path_list = [os.path.join(images_dir, filename) for filename in os.listdir(images_dir)]
	
	# Step 2: 读取并resize图片，并形成二维数组
	images = [(cv2.resize((cv2.imdecode(np.fromfile(image_path, np.uint8), 0)), (n, n))).ravel() for image_path in images_path_list]
	
	# Step 3: 计算相关系数
	corr_matrix = np.corrcoef(images)
	
	# Step 4: 找到相关系数大于beta的相似图片
	similar_images = np.argwhere(corr_matrix > beta)
	
	# Step 5: 构建相似组
	groups = []
	for pair in similar_images:
		added = False
		for group in groups:
			if pair[0] in group or pair[1] in group:
				group.add(pair[0])
				group.add(pair[1])
				added = True
				break
		if not added:
			groups.append(set(pair))
	
	# Step 6: 删除相似组中的重复图片
	for group in groups:
		keep_index = min(group)  # 保留相似组中的第一张图片
		for index in group:
			if index != keep_index:
				os.remove(images_path_list[index])


# 调用示例
images_dir = r'D:\ProgramData\Temp\BP3730-2\L N'
n = 64  # 重设大小后的图片大小（n x n）
beta = 0.8  # 相关系数阈值
remove_duplicate_images(images_dir, n, beta)
