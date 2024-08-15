import ADBHelper
import RaphaelScriptHelper
import testDict
import cv2
import numpy as np

import random
import os

print(ADBHelper.getDevicesList())

RaphaelScriptHelper.deviceID = "emulator-5554"
RaphaelScriptHelper.deviceType = 1


def click_open_AI_button():
    x1, y1 = 832, 550
    x2, y2 = 900, 620

    random_x = random.randint(x1, x2)
    random_y = random.randint(y1, y2)
    random_pos = (random_x, random_y)
    RaphaelScriptHelper.touch(random_pos)

def check_if_open_AI():
    # 使用较高的匹配精度
    high_accuracy = 0.96

    # 截取整个屏幕
    RaphaelScriptHelper.ADBHelper.screenCapture(RaphaelScriptHelper.deviceID, "current_screen.png")

    # 读取截图
    img = cv2.imread("current_screen.png")

    # 读取AI图标模板
    ai_icon_template = cv2.imread(testDict.AI_Button, 0)  # 假设testDict中有ai_icon的路径

    # 将截图转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 执行模板匹配
    result = cv2.matchTemplate(gray, ai_icon_template, cv2.TM_CCOEFF_NORMED)

    # 获取最佳匹配位置和相似度
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= high_accuracy:
        print(f"检测到AI图标，匹配度: {max_val:.2f}")
        return True
    else:
        print(f"未检测到AI图标，最高匹配度: {max_val:.2f}")
        return False
# check_if_open_AI()

def is_in_station():
    in_station = RaphaelScriptHelper.find_pic(testDict.out_station)
    if in_station:
        print('在空间站中')
    else:
        print('不在空间站内')

is_in_station()
def find_status_area(static_elements):
    all_positions = []
    for element in static_elements:
        positions = RaphaelScriptHelper.find_pic_all(element)
        if positions:
            all_positions.extend(positions)

    if len(all_positions) < 3:
        return None

    # 根据 y 坐标排序
    all_positions.sort(key=lambda pos: pos[1])

    # 检查是否有三个元素的 y 坐标相近
    for i in range(len(all_positions) - 2):
        y1, y2, y3 = all_positions[i][1], all_positions[i + 1][1], all_positions[i + 2][1]
        if abs(y1 - y2) <= 5 and abs(y1 - y3) <= 5:  # 假设 y 坐标差在 5 像素内认为是同一行
            # 返回最左边的 x 坐标和最上面的 y 坐标
            x = min(all_positions[i][0], all_positions[i + 1][0], all_positions[i + 2][0])
            return (x, y1)

    return None


def safe_check(retry=True):
    # 定义三个静态元素
    static_elements = [testDict.safe_element_1, testDict.safe_element_2, testDict.safe_element_3]

    # 找到状态区域
    status_area_pos = find_status_area(static_elements)

    if status_area_pos is None:
        print("无法找到状态区域")
        if retry:
            print("尝试点击local_list并重新识别")
            RaphaelScriptHelper.find_pic_touch(testDict.local_list)
            RaphaelScriptHelper.random_delay()
            return safe_check(retry=False)  # 递归调用，但不再重试
        return False

    # 截取整个屏幕
    RaphaelScriptHelper.ADBHelper.screenCapture(RaphaelScriptHelper.deviceID, "current_screen.png")

    # 读取截图
    img = cv2.imread("current_screen.png")

    status_width, status_height = 200, 30  # 假设的值，需要根据实际情况调整

    x, y = status_area_pos
    status_area = img[y:y + status_height, x:x + status_width]

    # 在原图上绘制矩形框
    cv2.rectangle(img, (x, y), (x + status_width, y + status_height), (0, 255, 0), 2)

    # 保存标记了区域的图像
    cv2.imwrite("marked_screen.png", img)

    # 保存裁剪出的状态区域
    cv2.imwrite("status_area.png", status_area)
    # 读取数字0的模板
    template = cv2.imread(testDict.number_zero, 0)

    # 将状态区域转换为灰度图
    gray = cv2.cvtColor(status_area, cv2.COLOR_BGR2GRAY)

    # 执行模板匹配
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)

    # 设置阈值
    threshold = 0.8
    locations = np.where(result >= threshold)

    # 计算匹配的数量
    match_count = len(locations[0])

    # 如果找到3个匹配，则认为是安全状态
    if match_count == 3:
        print("当前为安全状态")
        return True
    else:
        print(f"当前为不安全状态 (匹配到 {match_count} 个0)")
        return False

# # 使用示例
# if safe_check():
#     print("可以继续执行后续操作")
#     RaphaelScriptHelper.find_pic_touch(testDict.out_station)
#
#     RaphaelScriptHelper.random_delay()
#
#     RaphaelScriptHelper.delay(15)
#     open_AI()
# else:
#     print("需要采取安全措施")
