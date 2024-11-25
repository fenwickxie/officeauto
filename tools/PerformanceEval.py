import time
from functools import wraps


def calculate_time(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		print("Function {} is running...".format(func.__name__))
		start_time = time.time()
		result = func(*args, **kwargs)
		end_time = time.time()
		print(f"Function {func.__name__} took {(end_time - start_time) * 1000:.3f}ms to run")
		return result
	
	return wrapper
