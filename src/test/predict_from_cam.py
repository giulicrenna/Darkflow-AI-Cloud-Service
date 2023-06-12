from ultralytics import YOLO
import supervision as sv
import cv2
import os

ABS_PATH : str = os.getcwd()

os.environ["YOLOv5_VERBOSE"] = "False"

os.system('clear')

conf : int = 0.25  
max_det : int = 5

def main():    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    #model = YOLO(f"{ABS_PATH}/model/best.pt")
    model = YOLO("yolov5m.pt")

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    while True:
        ret, frame = cap.read()
        result = model(frame, agnostic_nms=True)[0]
        detections = sv.Detections.from_yolov8(result)
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]
        
        single_labels : list = [
            f"{model.model.names[class_id]}"
            for _, class_id, class_id, _
            in detections
        ]
        
        for i in single_labels:
            print(f'\t>{i}')
            
        frame = box_annotator.annotate(
            scene=frame, 
            detections=detections, 
            labels=labels
        ) 
        
        cv2.imshow("yolov8", frame)

        if (cv2.waitKey(30) == 27): 
           break
            
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()
    while True:
        try:
            pass
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            else:
                pass
    


