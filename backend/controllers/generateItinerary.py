from fastapi import APIRouter, HTTPException
from database.database import get_connection
from datetime import datetime
import json

router = APIRouter()

@router.post("/generate_report/{user_id}")
async def generate_report(user_id: int):
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor()

        # Section 1: Fetch data from messages
        fetch_messages_query = """
            SELECT message, timestamp
            FROM messages
            JOIN chat_logs ON messages.chat_id = chat_logs.chat_id
            WHERE chat_logs.user_id = %s
        """
        cursor.execute(fetch_messages_query, (user_id,))
        messages = cursor.fetchall()
        # Test Section 1: Print fetched messages

        # Section 2: Fetch data from images
        fetch_images_query = """
            SELECT items, uploaded_at
            FROM images
            WHERE user_id = %s
        """
        cursor.execute(fetch_images_query, (user_id,))
        images = cursor.fetchall()
        # Test Section 2: Print fetched images
        print("Fetched images:", images)

        # Section 3: Generate itineraries
        itineraries = []
        for message in messages:
            itineraries.append({
                "item_name": f"Message Insight {message['timestamp']}",
                "description": message["message"],
                "quantity": 1,
                "source_references": json.dumps([{"type": "message", "timestamp": message["timestamp"]}]),
            })

        for image in images:
            image_items = image["items"].split(",")  # Assuming items are comma-separated
            for item in image_items:
                itineraries.append({
                    "item_name": item.strip(),
                    "description": "Extracted from image",
                    "quantity": 1,
                    "source_references": json.dumps([{"type": "image", "uploaded_at": image["uploaded_at"]}]),
                })
        # Test Section 3: Print generated itineraries
        print("Generated itineraries:", itineraries)

        # Section 4: Insert itineraries into the database
        insert_itinerary_query = """
            INSERT INTO itineraries (user_id, item_name, description, quantity, source_references, created_at)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING itinerary_id
        """
        inserted_itinerary_ids = []
        for itinerary in itineraries:
            cursor.execute(
                insert_itinerary_query,
                (
                    user_id,
                    itinerary["item_name"],
                    itinerary["description"],
                    itinerary["quantity"],
                    itinerary["source_references"],
                    datetime.now(),
                ),
            )
            inserted_itinerary_ids.append(cursor.fetchone()["itinerary_id"])
        # Test Section 4: Print inserted itinerary IDs
        print("Inserted itinerary IDs:", inserted_itinerary_ids)

        # Section 5: Insert report for the user
        report_title = f"Report for User {user_id}"
        insert_report_query = """
            INSERT INTO reports (user_id, report_title, created_at)
            VALUES (%s, %s, %s) RETURNING report_id
        """
        cursor.execute(insert_report_query, (user_id, report_title, datetime.now()))
        report_id = cursor.fetchone()["report_id"]
        # Test Section 5: Print report ID
        print("Generated report ID:", report_id)

        # Section 6: Link itineraries to the report in report_items
        link_items_query = """
            INSERT INTO report_items (report_id, itinerary_id)
            VALUES (%s, %s)
        """
        for itinerary_id in inserted_itinerary_ids:
            cursor.execute(link_items_query, (report_id, itinerary_id))
        # Test Section 6: Ensure report items linked successfully
        print("Linked report items to report ID:", report_id)

        # Commit the transaction
        conn.commit()

        # Final Response
        return {
            "report_id": report_id,
            "message": "Report generated successfully.",
            "items": itineraries,
        }

        return {'success': 'successs'}

    except Exception as e:
        print(f"Error generating report: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while generating the report.")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
