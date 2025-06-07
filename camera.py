'''
Opencv-python读取IP摄像头视频流/USB摄像头
'''

import cv2
from ultralytics import YOLO

def detect(m_pth='runs/detect/train9/weights/best.pt',camera_ip='rtsp://admin:qwer135790.@192.168.1.64:554/live'):
    # 加载模型
    model = YOLO(m_pth)

    # 创建一个窗口 名字叫做Window
    cv2.namedWindow('Window', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    '''
    #打开USB摄像头
    cap = cv2.VideoCapture(0)
    '''

    # 摄像头的IP地址,http://用户名：密码@IP地址：端口/
    # ip_camera_url = 'rtsp://admin:admin@10.106.137.190:8554/live
    # 创建一个VideoCapture
    cap = cv2.VideoCapture(camera_ip)

    print('IP摄像头是否开启： {}'.format(cap.isOpened()))

    # 显示缓存数
    print(cap.get(cv2.CAP_PROP_BUFFERSIZE))
    # 设置缓存区的大小
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # 调节摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 设置FPS
    print('setfps', cap.set(cv2.CAP_PROP_FPS, 25))
    print(cap.get(cv2.CAP_PROP_FPS))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 将BGR转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 使用YOLO进行检测
        results = model.predict(source=rgb_frame, size=640)

        # 绘制检测框
        for result in results:
            boxes = result.boxes
            xyxy = boxes.xyxy  # 获取检测框的坐标
            conf = boxes.conf  # 获取置信度
            cls = boxes.cls    # 获取类别
            for i in range(len(xyxy)):
                x1, y1, x2, y2 = int(xyxy[i][0]), int(xyxy[i][1]), int(xyxy[i][2]), int(xyxy[i][3])
                conf_score = conf[i]
                class_label = cls[i]
                color = (int(class_label * 100 % 256), int(class_label * 200 % 256), int(class_label * 300 % 256))
                label = f'{model.names[int(class_label)]} {conf_score:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 4)

            # 编码帧为JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # 发送帧
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# 当一切结束后，释放VideoCapture对象
    cap.release()
    cv2.destroyAllWindows()