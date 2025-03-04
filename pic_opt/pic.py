#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright (c) 2025. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

# @Time    : 2025 1月 12 20:25
# @Author  : fenwickxie
# @PROJECT : officeauto
# @File    : pic.py
# @Software: PyCharm
import cv2
import numpy as np
from PIL import Image

# 读取图像
image = cv2.imdecode(np.fromfile(r"D:\fenwickxie\Pictures\Picture\certificate photo\白底 260×378.jpg", np.uint8),
                     cv2.IMREAD_COLOR)

# 将OpenCV图像转换为PIL图像
image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

# 另存为指定DPI的RGB图像
image_pil.save(r"D:\fenwickxie\Pictures\Picture\certificate photo\output_image.jpg", quality=95, dpi=(300, 300),
               optimize=False, progressive=False)
if __name__ == '__main__':
    pass