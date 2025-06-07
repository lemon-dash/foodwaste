import cv2
from ultralytics import YOLO

def detect(m_pth='runs/detect/train9/weights/best.pt',v_pth='moni.mp4'):
    model = YOLO(m_pth)
    cap = cv2.VideoCapture(v_pth)
    # 获取视频的帧率和尺寸
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    names = v_pth.split('.')
    o_pth = f'{names[0]}_detected.{names[1]}'
    out = cv2.VideoWriter(o_pth, fourcc, fps, (width, height))
    # 逐帧读取视频
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # 将帧转换为 RGB 格式（YOLO 模型需要 RGB 格式）
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 使用 YOLO 模型进行目标检测
        results = model.predict(frame_rgb)
        # 将检测结果绘制到帧上
        for result in results:
            boxes = result.boxes
            xyxy = boxes.xyxy  # 获取检测框的坐标
            conf = boxes.conf  # 获取置信度
            cls = boxes.cls    # 获取类别

            for i in range(len(xyxy)):
                x1, y1, x2, y2 = int(xyxy[i][0]), int(xyxy[i][1]), int(xyxy[i][2]), int(xyxy[i][3])
                conf_score = conf[i]
                class_label = cls[i]
                label = f'{model.names[int(class_label)]} {conf_score:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 10)
        # 将处理后的帧写入输出视频
        out.write(frame)

    # 释放资源
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    detect()