import sqlite3
import plistlib

def decode_plist_from_db(database_path, file_id, output_file):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        
        # Fetch the BLOB data for the specified fileID
        cur.execute("SELECT file FROM Files WHERE fileID = ?", (file_id,))
        file_data = cur.fetchone()
        
        if file_data is None:
            print(f"No data found for fileID: {file_id}")
            return
        
        # Write the binary plist to a temporary file
        with open(output_file, "wb") as temp_file:
            temp_file.write(file_data[0])
        
        # Decode the plist file
        with open(output_file, "rb") as temp_file:
            plist_data = plistlib.load(temp_file)
        
        # Print the decoded plist content
        print("Decoded Plist Data:")
        print(plist_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Parameters
database_path = "../Manifest.db"  # Path to your SQLite database
file_id = "fa543fd9115f9c13ba1a2ad2990731b0d4a2eccf"  # Replace with the fileID you want to decode
output_file = "temp.plist"  # Temporary output file for the plist data

# Run the function
decode_plist_from_db(database_path, file_id, output_file)
