import re


def split_by_any_separator(input_string: str, separators: list):
	# 使用正则表达式的 '|' 操作符指定多个分隔符
	pattern = '|'.join(re.escape(separator) for separator in separators)
	result = re.split(pattern, input_string)
	return result
