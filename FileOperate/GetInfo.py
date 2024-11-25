import os
import platform
from datetime import datetime


class GetInfo:
	def __init__(self, file_path):
		self.file_path = file_path
	
	def get_file_date(self):
		if platform.system() == 'Windows':
			create_time = os.path.getctime(self.file_path)
			modify_time = os.path.getmtime(self.file_path)
			infor = os.path.getatime(self.file_path)
		elif platform.system() == 'Linux' or platform.system() == 'Darwin':
			create_time = os.path.getctime(self.file_path)
			modify_time = os.path.getmtime(self.file_path)
		else:
			create_time = modify_time = None
		
		# if create_time is not None:
		# 	create_time_formatted = datetime.utcfromtimestamp(create_time).strftime('%Y%m%d')
		# 	print(f'创建日期(YYMMDD): {create_time_formatted}')
		# else:
		# 	print('无法获取创建日期')
		#
		# if modify_time is not None:
		# 	modify_time_formatted = datetime.utcfromtimestamp(modify_time).strftime('%Y%m%d')
		# 	print(f'修改日期(YYMMDD): {modify_time_formatted}')
		# 	return modify_time_formatted
		# else:
		# 	print('无法获取修改日期')
		
		if modify_time is not None and create_time is not None:
			return datetime.utcfromtimestamp(min(modify_time, create_time)).strftime('%Y%m%d')
		elif modify_time is not None:
			return datetime.utcfromtimestamp(modify_time).strftime('%Y%m%d')
		elif create_time is not None:
			return datetime.utcfromtimestamp(create_time).strftime('%Y%m%d')
		else:
			raise ValueError(self.file_path + '：无法获取日期')
	
	def get_movie_date(self):
		import subprocess
		import json
		
		if os.path.exists(self.file_path):
			# 使用ffprobe获取视频文件信息，包括创建媒体日期
			command = ['ffprobe', '-v', 'error', '-show_entries', 'format_tags=creation_time', '-of', 'default=nw=1:nk=1', self.file_path]
			result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
			
			if result.returncode == 0:
				# 解析ffprobe的输出，获取创建媒体日期
				output = result.stdout.strip()
				if output:
					create_time = output.strip()
					print(self.file_path + f'创建媒体日期: {create_time}')
					return create_time
				else:
					print(self.file_path + '：无法获取媒体创建日期')
			else:
				print(self.file_path + '：无法获取媒体创建日期')
		else:
			print('文件不存在')
	
	def get_image_creation_date(self):
		from PIL import Image
		from PIL.ExifTags import TAGS, GPSTAGS
		try:
			with Image.open(self.file_path) as img:
				exif_data = img._getexif()
				if exif_data is not None:
					for tag, value in exif_data.items():
						tag_name = TAGS.get(tag, tag)
						if tag_name == 'DateTimeOriginal':
							# 返回日期形式如 "2023:09:07 00:41:49"
							return value.replace(":", "").replace(" ", "_")
					return "拍摄日期未找到"
				else:
					return "没有 Exif 数据"
		except Exception as e:
			return f"发生错误: {str(e)}"


def get_date(file_full_path):
	getInfo = GetInfo(file_full_path)
	media_date = None
	try:
		media_date = getInfo.get_movie_date().split('T')[0].replace("-", "")
	except Exception as e:
		pass
	file_date = getInfo.get_file_date()
	if media_date is not None and file_date is not None:
		try:
			date = str(min(int(media_date), int(file_date)))
		except:
			raise ValueError(file_full_path + '：日期格式错误，无法转换为数字进行比较！')
	elif media_date is not None:
		date = media_date
	elif file_date is not None:
		date = file_date
	return date


if __name__ == '__main__':
	# 替换成你的图片文件路径
	dir_path = r"D:\Fenwick\Downloads\[揺り蓋]"
	dirs = os.listdir(dir_path)
	dirs.sort(key=str.lower)
	for dir in dirs:
		dir_full_path = os.path.join(dir_path, dir)
		if os.path.isdir(dir_full_path):
			medias = os.listdir(dir_full_path)
			file_full_path = os.path.join(dir_full_path, medias[0])
			if os.path.isfile(file_full_path):
				date = get_date(file_full_path)
				
				# new_name = dir.replace(' - ', ' ')
				# new_name = dir[0:13] + ' ' + dir[13:]
				new_name = date + ' ' + dir
				os.rename(dir_full_path, os.path.join(dir_path, new_name))
		elif os.path.isfile(dir_full_path):
			date = get_date(dir_full_path)
			# new_name = dir.replace(' - ', ' ')
			# new_name = dir[0:13] + ' ' + dir[13:]
			new_name = date + ' ' + dir
			os.rename(dir_full_path, os.path.join(dir_path, new_name))
	print("done!")
