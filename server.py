from flask import Flask, request, jsonify
import subprocess
import os
import re
import sqlite3

app = Flask(__name__)

DATABASE_PATH = "tags.db" 

@app.route('/search_tag', methods=['POST'])
def search_tag():
    try:
        # Path to the interactive.py script
        interactive_script_path = os.path.join(os.getcwd(), "interactive.py")
        result = subprocess.run(
            ["python3", interactive_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            return jsonify({"status": "error", "message": result.stderr.strip()}), 500

        # Parse the raw data to extract the tag ID
        output = result.stdout
        match = re.search(r"raw:\s*0*([0-9a-fA-F]+)", output)
        if not match:
            return jsonify({"status": "fail", "message": "No valid tag ID found", "output": output.strip()}), 404

        parsed_tag_id = match.group(1)

        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()

        cursor.execute("SELECT EXISTS(SELECT 1 FROM tags WHERE tag_id = ?)", (parsed_tag_id,))
        tag_exists = cursor.fetchone()[0]

        connection.close()

        # Send the result back to the client
        return jsonify({
            "status": "success",
            "tag_id": parsed_tag_id,
            "exists_in_database": bool(tag_exists)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)