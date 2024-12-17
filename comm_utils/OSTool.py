import os
import winreg


def get_app_install_path(program_name: str) -> str:
	# 读取注册表
	with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
		num_subkeys = winreg.QueryInfoKey(key)[0]
		i = 0
		while i < num_subkeys:
			try:
				# 读取子键名
				sub_key_name = winreg.EnumKey(key, i)
				# 打开子键
				with winreg.OpenKey(key, sub_key_name) as sub_key:
					# 读取子键值
					display_name = winreg.QueryValueEx(sub_key, 'DisplayName')[0]
					install_path = winreg.QueryValueEx(sub_key, 'InstallLocation')[0]
					if program_name.lower() in display_name.lower():
						return install_path
			except OSError:
				pass
			i += 1
		return None


def get_all_files_base(directory: str, include_subdirs: bool = False):
	files_full_path = []
	filenames = []
	
	for filename in os.listdir(directory):
		file_path = os.path.join(directory, filename)
		if os.path.isfile(file_path):
			files_full_path.append(file_path)
			filenames.append(filename)
		
		elif include_subdirs and os.path.isdir(file_path):
			files_full_path_temp, filenames_temp = get_all_files_base(file_path, include_subdirs)
			files_full_path.extend(files_full_path_temp)
			filenames.extend(filenames_temp)
	return [files_full_path, filenames]


def get_all_files_walk(directory: str, include_subdirs: bool = False):
	files_full_path = []
	filenames = []
	for root, dirs, _filenames in os.walk(directory):
		if include_subdirs:
			for _filename in _filenames:
				files_full_path.append(os.path.join(root, _filename))
			filenames.extend(_filenames)
		else:
			files_full_path.extend([os.path.join(root, filename) for filename in filenames])
			filenames.extend(filenames)
	return [files_full_path, filenames]


if __name__ == '__main__':
	files_full_path, filenames = get_all_files_walk(r"D:\Fenkx\Fenkx - General\AI\Dataset\BarCode\My Datasets\Test_Label_ALL_Original_Classified", True)
	files_full_path.sort(key=str.lower)
	filenames.sort(key=str.lower)
	print(all)
