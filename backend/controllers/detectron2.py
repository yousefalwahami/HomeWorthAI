import os
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from io import BytesIO
import torch
import numpy as np  # Import numpy
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
from PIL import Image, ImageDraw
from detectron2.data import MetadataCatalog

# Access COCO metadata
metadata = MetadataCatalog.get("coco_2017_val")
COCO_CLASSES = metadata.thing_classes
print(metadata.thing_classes)  # This will print out the class names


print(torch.__version__)
print(torch.cuda.is_available())  # Should print False if it's CPU-only
#print(torch.device(get_cfg.MODEL.DEVICE))
print(torch.device)


# Initialize the Detectron2 model
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Set threshold for detection

# Explicitly set the device to CPU
cfg.MODEL.DEVICE = "cpu"

predictor = DefaultPredictor(cfg)

router = APIRouter()

@router.post("/detect_objects")
async def detect_objects(file: UploadFile = File(...)):
  # Read the image file
  image_bytes = await file.read()
  image = Image.open(BytesIO(image_bytes))

  # Convert to a format Detectron2 can use (numpy array)
  image = image.convert("RGB")
  image_np = np.array(image)  # Directly convert to numpy array (no need for torch)

  # Run object detection
  outputs = predictor(image_np)

  # Process results (e.g., extracting detected objects)
  instances = outputs["instances"]
  boxes = instances.pred_boxes.tensor.numpy()  # Bounding boxes of detected objects
  scores = instances.scores.numpy()  # Confidence scores of detections
  classes = instances.pred_classes.numpy()  # Class labels of detected objects

  # Draw bounding boxes on the image
  draw = ImageDraw.Draw(image)
  for box, score, cls in zip(boxes, scores, classes):
    if score > 0.5:  # Only draw boxes with a score above the threshold
      x1, y1, x2, y2 = box
      draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
      # Adjust text position: move the text slightly to the right (x1 + 5)
      class_name = COCO_CLASSES[cls]
      text_position = (x1 + 5, y1)  # Shift text 5 pixels to the right of the bbox
      #draw.text(text_position, f"{cls} ({score:.2f})", fill="red")
      draw.text(text_position, f"{class_name} ({score:.2f})", fill="red")

  # Convert the image to a byte stream to return as a response
  img_byte_arr = BytesIO()
  image.save(img_byte_arr, format='PNG')
  img_byte_arr.seek(0)

  results = [
    {"bbox": box.tolist(), "score": float(score), "class": int(cls)}
    for box, score, cls in zip(boxes, scores, classes)
  ]
  print(results)
  
  return StreamingResponse(img_byte_arr, media_type="image/png")

  
  '''

  # Convert numpy scalars to native Python types (e.g., float, int)
  results = [
    {"bbox": box.tolist(), "score": float(score), "class": int(cls)}
    for box, score, cls in zip(boxes, scores, classes)
  ]
  
  return {"detections": results}
  '''