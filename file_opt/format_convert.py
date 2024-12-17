from functools import partial

import cv2
import os
import shutil
from concurrent.futures import ThreadPoolExecutor


class FormatConvert:
	def __init__(self, input_folder, output_folder, backup_folder):
		self.input_folder = input_folder
		self.output_folder = output_folder
		self.backup_folder = backup_folder
	
	def process_image(self, input_file, output_extension):
		# 构建输入和输出文件的完整路径
		input_path = os.path.join(self.input_folder, input_file)
		output_file = os.path.splitext(input_file)[0] + output_extension
		output_path = os.path.join(self.output_folder, output_file)
		
		# 读取图像文件
		img = cv2.imread(input_path, 1)
		
		# 另存为指定格式
		cv2.imwrite(output_path, img)
		
		# 移动源文件到备份目录
		backup_path = os.path.join(self.backup_folder, input_file)
		shutil.move(input_path, backup_path)
	
	def convert_images_parallel(self, input_extensions, output_extension):
		# 确保输出文件夹存在
		if not os.path.exists(self.output_folder):
			os.makedirs(self.output_folder)
		
		# 确保备份文件夹存在
		if not os.path.exists(self.backup_folder):
			os.makedirs(self.backup_folder)
		
		# 获取输入文件夹中所有指定后缀名的文件
		input_files = [f for f in os.listdir(self.input_folder) if any(f.endswith(ext) for ext in input_extensions)]
		
		# 使用 ThreadPoolExecutor 同时处理多个文件
		with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
			futures = []
			
			for input_file in input_files:
				# 使用 functools.partial 包装 process_image 函数
				partial_process_image = partial(self.process_image, input_file, output_extension)
				future = executor.submit(partial_process_image)
				futures.append(future)
			
			# 等待所有任务完成
			for future in futures:
				future.result()


if __name__ == "__main__":
	# 设置输入和输出文件夹以及文件格式
	input_folder = r"D:\Fenwick\Downloads\original_resized_all"
	output_folder = r"D:\Fenwick\Downloads\original_resized_all"
	backup_folder = r"D:\Fenwick\Downloads\original_resized_all\backups"
	input_extensions = [".png", ".tif", ".bmp"]  # 输入文件后缀名列表
	output_extension = ".jpg"  # 输出文件后缀名
	
	# 创建 FormatConvert 对象
	converter = FormatConvert(input_folder, output_folder, backup_folder)
	
	# 调用对象的方法进行转换
	converter.convert_images_parallel(input_extensions, output_extension)
