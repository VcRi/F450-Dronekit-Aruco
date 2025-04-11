import cv2
import numpy as np
import time

# 摄像头参数
CAMERA_DEVICE = "/dev/video0"
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1200
FPS = 30

# ArUco参数
DICTIONARY = cv2.aruco.DICT_4X4_50
MARKER_ID = 0

# 初始化摄像头
cap = cv2.VideoCapture(CAMERA_DEVICE)
if not cap.isOpened():
    print(f"无法打开摄像头 {CAMERA_DEVICE}！")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

# ArUco初始化
aruco_dict = cv2.aruco.Dictionary_get(DICTIONARY)
parameters = cv2.aruco.DetectorParameters_create()

def get_frame_center(frame):
    h, w = frame.shape[:2]
    return (w // 2, h // 2)

# 主程序
try:
    last_detection_time = 0
    detection_interval = 2.5  # 检测间隔(秒)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("摄像头读取失败！")
            break

        # 显示画面
        cv2.imshow("Camera View - 按ESC退出", frame)
        
        # 按固定间隔检测
        current_time = time.time()
        if current_time - last_detection_time >= detection_interval:
            last_detection_time = current_time
            
            # 检测ArUco标记
            corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
            
            if ids is not None and MARKER_ID in ids:
                idx = np.where(ids == MARKER_ID)[0][0]
                frame_center = get_frame_center(frame)
                marker_center = np.mean(corners[idx][0], axis=0).astype(int)
                
                offset_x = marker_center[0] - frame_center[0]
                offset_y = marker_center[1] - frame_center[1]

                # 输出调整指令
                if abs(offset_x) > 100:
                    print(f"[{time.strftime('%H:%M:%S')}] 向右移动" if offset_x > 0 else f"[{time.strftime('%H:%M:%S')}] 向左移动")
                if abs(offset_y) > 100:
                    print(f"[{time.strftime('%H:%M:%S')}] 向上移动" if offset_y < 0 else f"[{time.strftime('%H:%M:%S')}] 向下移动")
                if abs(offset_x) <= 100 and abs(offset_y) <= 100:
                    print(f"[{time.strftime('%H:%M:%S')}] 已居中，准备降落")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] 未检测到标记")

        # 按ESC退出
        if cv2.waitKey(1) == 27:
            break

finally:
    # 确保资源被正确释放
    cap.release()
    cv2.destroyAllWindows()
    print("程序结束")