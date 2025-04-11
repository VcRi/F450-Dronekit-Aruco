# F450-Dronekit-Aruco
（2025）F450+树莓派5（Ubuntu24.04)+Dronekit+Aruco二维码降落教程
<br>
<br>
供hduasl内部参考使用，基本遵循**苍穹四轴DIY**给出的教程，但是**由于各个库的版本更新，在环境配置过程中遇到了很多问题，原有教程难以解决，所以整理出一份资料，基本涵盖本项目所有关键点。**  

教程已发布在CSDN上，链接：https://blog.csdn.net/qq_63712959/article/details/147137176
<br>
**1、connect.py**

验证Dronekit库是否下载成功，是否能正确连接无人机

**2、control.py**   

控制机械爪开合

**3、camera_test.py**   

打开摄像头检测Aruco二维码
<br>
以下两份代码请提前做好仿真再使用：

**4、hover.py**   

抓取操作 + 起飞 + 空中悬停 + 降落 +机械爪打开

**5、move.py**    

抓取操作 + 起飞 + 空中悬停 + 移动一段距离 + 降落 +机械爪打开  
<br>
**DroneDeliverySystem.py**  
这份代码的最终实现方式我并不满意，就不放上来了
