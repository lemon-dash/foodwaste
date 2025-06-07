from ultralytics import YOLO
import cv2
import os
from PIL import Image

def detect(m_pth='runs/detect/train9/weights/best.pt',s_pth='food_20.jpg'):
    model = YOLO(m_pth)
    results = model.predict(source=s_pth)
    # 读取原始图像
    img = cv2.imread(s_pth)
    # 初始化变量以存储最大置信度和对应的类别
    max_conf = 0
    max_conf_class = ''
    # 定义颜色映射函数
    def get_color(cls):
        # 使用简单的哈希函数将类别索引映射到颜色
        color = (int(cls * 100 % 256), int(cls * 200 % 256), int(cls * 300 % 256))
        return color
    # 绘制检测框和标签
    for result in results:
        boxes = result.boxes
        xyxy = boxes.xyxy  # 获取检测框的坐标
        conf = boxes.conf  # 获取置信度
        cls = boxes.cls    # 获取类别
        for i in range(len(xyxy)):
            x1, y1, x2, y2 = int(xyxy[i][0]), int(xyxy[i][1]), int(xyxy[i][2]), int(xyxy[i][3])
            conf_score = conf[i]
            class_label = cls[i]
            color = get_color(int(class_label))
            label = f'{model.names[int(class_label)]} {conf_score:.2f}'
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 4)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 4)
         # 跳过类别 0:plate
            if int(class_label) == 0:
                continue
            # 更新最大置信度和对应的类别
            if conf_score > max_conf:
                max_conf = conf_score
                max_conf_class = model.names[int(class_label)]
    # 保存绘制后的图像
    output_path = os.path.splitext(s_pth)[0] + '_detected.jpg'
    cv2.imwrite(output_path, img)
    if max_conf_class == '':
       conclusion = None
    else:
        conclusion = '检测结果为：'+max_conf_class
    return conclusion
    

if __name__ == '__main__':
    # model = YOLO('runs/detect/train9/weights/best.pt')
    # model.predict(source='food_20.jpg',save=True)
    detect()