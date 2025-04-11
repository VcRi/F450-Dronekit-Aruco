import RPi.GPIO as GPIO
import time

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
    print("打开爪子")
    pwm.ChangeDutyCycle(8)  # 8%占空比（打开）
    time.sleep(1)  # 等待1s

# 定义函数：闭合爪子
def close_claw():
    print("闭合爪子")
    pwm.ChangeDutyCycle(5)  # 5%占空比（闭合）
    time.sleep(1)  # 等待1s


try:
    while True:
        open_claw()  # 打开爪子
        time.sleep(5)  # 等待5s

        close_claw()  # 闭合爪子
        time.sleep(5)  # 等待5s

except KeyboardInterrupt:
    # Ctrl+C，停止程序
    print("程序停止")

finally:
    # 停止PWM并清理GPIO设置
    pwm.stop()
    GPIO.cleanup()
    print("GPIO已清理")
