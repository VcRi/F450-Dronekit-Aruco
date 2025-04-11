#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import RPi.GPIO as GPIO
from pymavlink import mavutil 

# 设置GPIO模式为BCM
GPIO.setmode(GPIO.BCM)
# 定义GPIO引脚
PWM_PIN = 12  # GPIO12（32号引脚）
# 设置GPIO引脚为输出模式
GPIO.setup(PWM_PIN, GPIO.OUT)
# 创建PWM实例，频率设置为50Hz（适用于大多数舵机）
pwm = GPIO.PWM(PWM_PIN, 50)
# 启动PWM，初始占空比为0（电机停止）
pwm.start(0)

# 定义函数：打开爪子
def open_claw():
    print("爪子已打开，请在5s内放上物品")
    pwm.ChangeDutyCycle(8)  # 8%占空比（打开）
    time.sleep(1)  # 等待1秒，确保动作完成

# 定义函数：闭合爪子
def close_claw():
    print("爪子已闭合")
    pwm.ChangeDutyCycle(5)  # 5%占空比（闭合）
    time.sleep(1)  # 等待1秒，确保动作完成

# 在起飞之前，打开爪子5秒，然后合上爪子，等待3秒
print("起飞前操作：抓取物品")
open_claw()  # 打开爪子
time.sleep(5)  # 等待5秒
close_claw()  # 闭合爪子
print("等待3秒，开始连接设备")
time.sleep(3)  # 等待3秒


# 当前连接的 Pixhawk 飞控的端口
connection_string = '/dev/ttyUSB0'  # 现在使用的是 USB 转 TTL 接口，连接 Pixhawk 飞控
print('连接到设备: %s' % connection_string)
vehicle = connect('/dev/ttyUSB0', wait_ready=True, baud=57600) #降低波特率后成功


# 定义 arm_and_takeoff 函数，使无人机解锁并起飞到目标高度
# 参数 aTargetAltitude 即为目标高度，单位为米
def arm_and_takeoff(aTargetAltitude):
    # 起飞前检查
    print("进行起飞前检查")
    # vehicle.is_armable 会检查飞控是否启动完成
    while not vehicle.is_armable:
        print(" 等待设备初始化...")
        time.sleep(1)

    # 解锁无人机（电机将开始旋转）
    print("解锁电机")
    # 将无人机的飞行模式切换成 "GUIDED"（一般在 GUIDED 模式下控制无人机）
    vehicle.mode = VehicleMode("GUIDED")
    # 通过设置 vehicle.armed 状态变量为 True，解锁无人机
    vehicle.armed = True

    # 在无人机起飞之前，确认电机已经解锁
    while not vehicle.armed:
        print(" 等待解锁...")
        time.sleep(1)

    # 发送起飞指令
    print("起飞！")
    # simple_takeoff 将发送指令，使无人机起飞并上升到目标高度
    vehicle.simple_takeoff(aTargetAltitude)

    # 在无人机上升到目标高度之前，阻塞程序
    while True:
        print(" 当前高度: ", vehicle.location.global_relative_frame.alt)
        # 当高度上升到目标高度的 0.95 倍时，即认为达到了目标高度，退出循环
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("达到目标高度")
            break
        time.sleep(1)

# 调用上面声明的 arm_and_takeoff 函数，目标高度 3 米
arm_and_takeoff(2)

# 悬停 5 秒，并不断输出“正在悬停”和一些信息
# 这里是为了在悬停的时候输出信息才这么写。如果不需要输出信息，直接time.sleep(5)就可以
print("开始悬停")
start_time = time.time()
while time.time() - start_time < 5: 
    # 打印高度和完整GPS信息
    print(" 正在悬停，当前高度: ", vehicle.location.global_relative_frame.alt)
    print("当前模式：",vehicle.mode.name)
    time.sleep(1)

print("向左缓慢飞行")
left_speed = 0.5  # 设置向左飞行速度为0.5m/s
flight_time = 2    # 飞行时间4秒（0.5m/s × 4s = 2米）

# 获取起始位置
start_position = vehicle.location.global_relative_frame

# 发送向左速度指令
msg = vehicle.message_factory.set_position_target_local_ned_encode(
    0,       # 时间戳
    0, 0,    # 目标系统ID和目标组件ID
    mavutil.mavlink.MAV_FRAME_BODY_NED,  # 坐标系
    0b0000111111000111, # 控制速度的位掩码
    0, 0, 0, # 位置参数（忽略）
    0, -left_speed, 0, # 速度参数（X,Y,Z）- Y为负表示向左
    0, 0, 0, # 加速度参数（忽略）
    0, 0)    # 偏航参数（忽略）

# 发送指令并保持飞行状态
start_time = time.time()
while time.time() - start_time < flight_time:
    vehicle.send_mavlink(msg)
    vehicle.flush()
    print(" 正在向左飞行，当前高度: ", vehicle.location.global_relative_frame.alt)
    print("当前GPS：", vehicle.location.global_frame)
    time.sleep(0.1)

# 停止移动（发送零速度指令）
msg = vehicle.message_factory.set_position_target_local_ned_encode(
    0, 0, 0,
    mavutil.mavlink.MAV_FRAME_BODY_NED,
    0b0000111111000111,
    0, 0, 0,
    0, 0, 0,
    0, 0, 0,
    0, 0)
vehicle.send_mavlink(msg)
vehicle.flush()
print("向左飞行完成，准备降落")


# 发送 "降落" 指令
print("降落")
#这里根据需要选择降落的方式
# RTL模式，无人机会自动返回home点的正上方（RTL高度可以在地面站里更改），之后自动降落。但我不需要无人机返回航点，所以改用Land模式降落。
# vehicle.mode = VehicleMode("RTL")
vehicle.mode = VehicleMode("LAND")  # 直接降落

# 在降落过程中，不断输出当前高度
print("开始降落")
while vehicle.armed:  # 当无人机未降落完成时（电机仍在旋转）
    print(" 正在降落，当前高度: ", vehicle.location.global_relative_frame.alt)
    print("当前模式：",vehicle.mode.name)
    time.sleep(1)

# 降落完成后，退出之前，打开爪子
print("降落完成，打开爪子")
open_claw()  # 打开爪子
time.sleep(1)  # 等待1秒，确保动作完成

# 先停止PWM
pwm.stop()
# 然后清理GPIO设置
GPIO.cleanup()
print("GPIO已清理")

# 最后退出之前，清除 vehicle 对象
print("关闭设备连接")
vehicle.close()