import os
from fastapi import APIRouter, File, UploadFile
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
from database.database import get_connection
from psycopg2 import sql
from datetime import datetime

conn = get_connection()
cursor = conn.cursor()

# Access COCO metadata
metadata = MetadataCatalog.get("coco_2017_val")
COCO_CLASSES = metadata.thing_classes
print(metadata.thing_classes)  # This will print out the class names


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

  # Extract object labels
  detected_labels = [COCO_CLASSES[cls] for cls in classes if cls < len(COCO_CLASSES)]
  print('abc', detected_labels)

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

  # Collect unique classes from detection results
  unique_classes = list(set(detected_labels))  # Use a set to remove duplicates
  items = ", ".join(unique_classes)  # Convert the unique classes into a comma-separated string

  # Log the results for debugging
  print("Detection Results with Embeddings:")
  print(results)
  print("Unique Classes (Items):", items)

  # TODO: Store results in a vector database (e.g., Pinecone) here
  # You can use the 'results' dictionary to upload both embeddings and metadata

  '''
  save_image_to_db(
    user_id=1,  # You should dynamically determine the user ID
    filename=file.filename,
    items=items,
    image_data=image_bytes  # Directly use image bytes here
  )
  '''

  return {"detections": results}


  '''  results = [
    {"bbox": box.tolist(), "score": float(score), "class": int(cls)}
    for box, score, cls in zip(boxes, scores, classes)
  ]
  print(results)
  image = StreamingResponse(img_byte_arr, media_type="image/png")
  generate_image_embedding(image)
  
  return StreamingResponse(img_byte_arr, media_type="image/png")
  '''

def save_image_to_db(user_id, filename, items, image_data):
  try:
    # Get database connection
    conn = get_connection()
    cursor = conn.cursor()

    # Prepare SQL query to insert the image data
    query = sql.SQL("""
      INSERT INTO images (user_id, filename, items, image_data, uploaded_at)
      VALUES (%s, %s, %s, %s, %s)
    """)

    # Execute the query with the parameters
    cursor.execute(query, (user_id, filename, items, image_data, datetime.now()))

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(f"Image '{filename}' uploaded successfully!")

  except Exception as e:
    print("Error saving image to DB:", e)


  
'''
# RAG query
def generate_text_embedding(text):
  text_embeddings = embedding_model.encode([text])  # Sentence transformer model
  return text_embeddings[0]

# Example text query
query_text = "looking for my phone in the kitchen"

# Generate the query embedding
query_embedding = generate_text_embedding(query_text)

# Query Pinecone to find the most relevant image(s)
results = index.query(query_embedding, top_k=5, include_metadata=True)

# Display the results
for result in results["matches"]:
  print(f"Image ID: {result['id']}, Metadata: {result['metadata']}")
'''