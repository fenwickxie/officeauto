import os.path

from file_opt import drop_duplicates, Rename
from file_opt.achieve import multithread_winrar_compress, multithread_winrar_uncompress

if __name__ == '__main__':
	# base_path = r'D:\Fenwick\Videos'
	# for dir in os.listdir(base_path):
		path = r"D:\ProgramData\Temp"
		# path = os.path.join(base_path, dir)
		if os.path.isdir(path):
			rename = Rename(path)
			# DropDuplicates.remove_duplicates(path, 1, 1)
			# # pre = os.path.basename(path)+'_'
			# rename.sort_and_rename_files(path, index_length=4)
			# rename.rename_by_num(1, '0', 1, 3)
			# rename.add_prefix_or_suffix('20', '', '')
			# rename.replace_character('.','',True)
			rename.change_extension('.7z')
			
			# multithread_winrar_compress(path, 2, 64, 0)
			# multithread_winrar_uncompress(path,2)
