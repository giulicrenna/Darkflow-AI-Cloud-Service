def darkflow_to_yolo(top: float, left: float, width: float, height: float) -> dict:
    top /= 100
    left /= 100
    width /= 100
    height /= 100
    
    return {
        "y" : top + height/2,
        "x" : left + width/2,
        "w" : width,
        "h" : height
    }

def yolo_to_darkflow(x: float, y: float, width: float, height: float) -> dict:
    x *= 100
    y *= 100
    width *= 100
    height *= 100
    
    return {
        "top" : y - height/2,
        "left" : x - width/2,
        "width" : width,
        "height" : height
    }
    
def xyxy_to_darkflow(x1: float, y1: float, x2: float, y2: float, height_real: float, width_real: int) -> dict:
    x1 /= width_real/100
    y1 /= height_real/100
    x2 /= width_real/100
    y2 /= height_real/100
    
    return {
        "top" : y1,
        "left" : x1,
        "width" : x2-x1,
        "height" : y2-y1
    }

