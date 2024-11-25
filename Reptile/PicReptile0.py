# -*- coding: UTF-8 -*-
import json
import os

import requests
from bs4 import BeautifulSoup

headers = {
	'authority'               : 'pixabay.com',
	'method'                  : 'GET',
	'path'                    : '/zh/images/search/%E6%97%A5%E5%B8%B8%E7%94%9F%E6%B4%BB/',
	'scheme'                  : 'https',
	'accept'                   : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	'accept-encoding'          : 'gzip, deflate, br',
	'accept-language'          : 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
	'cache-control'            : 'max-age=0',
	'cookie'                   : 'csrftoken=1KZmyZFtt19QG8oYSf6PNS7LGQ6PyySmhHqhxfB74nzC5MhngdD7bAQeAKZ0XqyJ; lang=zh; anonymous_user_id=c5b2206b5a0b4c18b06c499cacc1d13a; dwf_strict_media_search=False; dwf_tag_ai_generated_media=False; __cf_bm=XLcpm.fbKAhwM3NX3M.lD4ZUtRiy2OI3ytdRBSUuQGI-1685206086-0-Ac5C/ntnb61kiCkPdeaDE48djI49SfzDiT4kmcaDWrnGt+6LwQ8yKdwC8Br+Popu67I5xq6f6SC7yDajcGBuiu0=; _sp_ses.aded=*; _ga=GA1.2.1066721550.1685206089; _gid=GA1.2.1616401526.1685206089; _sp_id.aded=47b9415d-f23b-4c44-bb2a-31edc5030cd4.1685206089.1.1685206172.1685206089.129846e0-d4b7-4304-92ba-d674b14c4925; OptanonConsent=isGpcEnabled=0&datestamp=Sun+May+28+2023+00%3A49%3A31+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.31.0&isIABGlobal=false&hosts=&consentId=efdb0da0-1189-4433-b1d0-9c6b93679f8d&interactionCount=1&landingPath=https%3A%2F%2Fpixabay.com%2Fzh%2Fimages%2Fsearch%2F%25E6%2597%25A5%25E5%25B8%25B8%25E7%2594%259F%25E6%25B4%25BB%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1',
	'referer'                  : 'https://cn.bing.com/',
	'sec-ch-ua'                : '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
	'sec-ch-ua-mobile'         : '?0',
	'sec-ch-ua-platform'       : 'Windows',
	'sec-fetch-dest'           : 'document',
	'sec-fetch-mode'           : 'navigate',
	'sec-fetch-site'           : 'cross-site',
	'sec-fetch-user'           : '?1',
	'upgrade-insecure-requests': '1',
	'user-agent'               : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57'
}


def download_barcode_images(search, save_path, images_num):
	# 创建保存图片的目录
	if not os.path.exists(save_path):
		os.makedirs(save_path)
	
	count = 0
	try:
		# 发送HTTP GET请求获取图片
		response1 = requests.get(search, headers=headers)
		
		if response1.status_code == 200:
			# 使用Beautiful Soup解析网页内容
			soup = BeautifulSoup(response1.text, 'html.parser')
			# 查找所有的<a>标签
			# img_tags = soup.find_all('a')
			img_tags = soup.find_all('img')
			# 提取图片链接
			image_urls = []
			
			for img in img_tags:
				try:
					# image_url = json.loads(img['m'])["murl"]
					image_url = img['src']
					image_urls.append(image_url)
					
					try:
						# 发送HTTP GET请求获取图片
						response = requests.get(image_url, headers=headers)
						
						if response.status_code == 200:
							# 从URL中提取文件名
							filename = os.path.join(save_path, os.path.basename(image_url))
							# 保存图片到本地
							with open(filename, 'wb') as f:
								f.write(response.content)
							
							count += 1
							print(f"Downloaded image {count}/{images_num}")
					except requests.exceptions.RequestException as e:
						print(f"Error: {str(e)}")
						pass
					finally:
						if count >= images_num:
							break
				except Exception as e:
					# print(e)
					pass
	
	# for image_url in image_urls:
	# try:
	# 	# 发送HTTP GET请求获取图片
	# 	response = requests.get(image_url)
	#
	# 	if response.status_code == 200:
	# 		# 从URL中提取文件名
	# 		filename = os.path.join(save_directory, f"barcode_{count}.jpg")
	# 		content = response.content
	# 		# 保存图片到本地
	# 		with open(filename, 'wb') as f:
	# 			f.write(content)
	#
	# 		count += 1
	# 		print(f"Downloaded image {count}/{num_images}")
	# except requests.exceptions.RequestException as e:
	# 	print(f"Error: {str(e)}")
	# 	pass
	# finally:
	# 	if count >= num_images:
	# 		break
	except requests.exceptions.RequestException as e:
		print(f"Error: {str(e)}")
		pass


url = "https://pixabay.com/zh/images/search/%E6%97%A5%E5%B8%B8%E7%94%9F%E6%B4%BB/"  # 替换为实际的图片URL
params = {
	'q'    : '工业场景 条码标签',
	'count': 200
}
save_directory = r"D:\vance\Downloads"  # 图片保存目录
num_images = 100  # 要下载的图片数量

download_barcode_images(url, save_directory, num_images)
