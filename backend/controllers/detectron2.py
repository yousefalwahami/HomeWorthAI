import os
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from io import BytesIO
import torch
import numpy as np
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
from PIL import Image, ImageDraw
from detectron2.data import MetadataCatalog
from transformers import CLIPProcessor, CLIPModel
from utils.pinecone_db import query_index, store_embeddings_in_pinecone
from database.database import get_connection
from datetime import datetime

# Access COCO metadata
metadata = MetadataCatalog.get("coco_2017_val")
COCO_CLASSES = metadata.thing_classes

# print(torch.__version__)
# print(torch.cuda.is_available())  # Should print False if it's CPU-only
# #print(torch.device(get_cfg.MODEL.DEVICE))
# print(torch.device)


# Initialize the Detectron2 model
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Set threshold for detection
cfg.MODEL.DEVICE = "cpu"# Explicitly set the device to CPU
predictor = DefaultPredictor(cfg)

# Initialize CLIP for embeddings
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

router = APIRouter()

def save_image_to_db(user_id, filename, items, image_data):
  conn = get_connection()
  cursor = None

  try:
    query = f"""
      INSERT INTO images (user_id, filename, items, image_data, uploaded_at)
      VALUES (%s, %s, %s, %s, %s) RETURNING image_id
    """
    cursor = conn.cursor()
    cursor.execute(query, (user_id, filename, items, image_data, datetime.now()))
    image_id = cursor.fetchone()['image_id']
    conn.commit()
    cursor.close()
    conn.close()

    return image_id

  except Exception as e:
    print("Error saving image to DB:", e)
    return None
  
  finally:
    if cursor:
      cursor.close()
    if conn:
      conn.close()


@router.post("/detect_objects")
async def detect_objects(
    file: UploadFile = File(...),
    user_id: int = Form(None) 
):
  # Read the image file
  image_bytes = await file.read()
  image = Image.open(BytesIO(image_bytes))
  image_inputs = clip_processor(images=image, return_tensors="pt")
  print(user_id)
  

    # Get the image embedding from CLIP (returns a tensor with shape [batch_size, 512])
  with torch.no_grad():
    image_embeddings = clip_model.get_image_features(**image_inputs)

  # Convert the embedding to a numpy array or directly use the tensor (if needed)
  image_embeddings = image_embeddings.cpu().numpy()

  # The image embedding is now a 512-dimensional vector


  # Convert to a format Detectron2 can use (numpy array)
  image = image.convert("RGB")
  image_np = np.array(image)  # Directly convert to numpy array (no need for torch)

  # Run object detection
  outputs = predictor(image_np)

  # Process results (e.g., extracting detected objects)
  instances = outputs["instances"]
  classes = instances.pred_classes.numpy()  # Class labels of detected objects

  # Extract object labels
  detected_labels = [COCO_CLASSES[cls] for cls in classes if cls < len(COCO_CLASSES)]
  '''
  # Generate embeddings using CLIP for detected object labels
  inputs = clip_processor(text=detected_labels, return_tensors="pt", padding=True)
  with torch.no_grad():
    text_embeddings = clip_model.get_text_features(**inputs)
  text_embeddings = text_embeddings.cpu().numpy()  # Convert to numpy for easier handling
  

  # Metadata for the objects
  results = [
    {"bbox": box.tolist(), "score": float(score), "class": COCO_CLASSES[cls], "embedding": embedding.tolist()}
    for box, score, cls, embedding in zip(boxes, scores, classes, text_embeddings)
  ]
  

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
  '''
  # Collect unique classes from detection results
  unique_classes = list(set(detected_labels))  # Use a set to remove duplicates
  items = ", ".join(unique_classes)  # Convert the unique classes into a comma-separated string

  '''
  # Log the results for debugging
  print("Detection Results with Embeddings:")
  print(results)
  print("Unique Classes (Items):", items)
  '''

  image_id = save_image_to_db(
    user_id=user_id, 
    filename=file.filename,
    items=items,
    image_data=image_bytes  
  )
  
  dict_item_context = {"items": unique_classes}
  embedding_result = store_embeddings_in_pinecone(dict_item_context=dict_item_context, embeddings=image_embeddings, chat_id=0, file=file.filename, user_id=user_id, image_id=image_id, type="image")
  
  return {"detections": embedding_result}


@router.get("/get_image/{image_id}")
async def get_image(image_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        print(f"Fetching image for image_id: {image_id}")

        # Query to get image data
        cursor.execute("SELECT image_data FROM images WHERE image_id = %s", (image_id,))
        image_data = cursor.fetchone()
        print("Raw image_data fetched from DB:", image_data['image_data'])

        # Check if image was found
        if not image_data['image_data']:
            raise HTTPException(status_code=404, detail="Image not found or image data is empty.")

        # Convert memoryview to bytes
        image_bytes = bytes(image_data['image_data'])
        print("Length of image bytes:", len(image_data['image_data']))

        # Convert the image bytes to a file-like object and open the image using PIL
        image = Image.open(BytesIO(image_data['image_data']))

        # Save the image to a BytesIO object
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        print("Image successfully processed.")

        # Return the image as a StreamingResponse
        return StreamingResponse(img_byte_arr, media_type="image/png")

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching image: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
