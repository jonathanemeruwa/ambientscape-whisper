import os
import requests
import base64
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# UNIVERSAL BYPASS: Disables strict URL slash requirements for Google's architecture
app.url_map.strict_slashes = False

# Initialize official OpenAI SDK Client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# CORS ACCESS BRIDGE: Unlocks direct cross-domain data transmission passes
@app.after_request
def apply_global_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# CATCH-ALL ROOT ROUTE: Handles incoming root validation handshakes cleanly from Google
@app.route("/", methods=["GET", "POST", "HEAD", "OPTIONS"])
def server_root_handshake():
    return jsonify({
        "success": True, 
        "status": "online", 
        "message": "Ambientscape OpenAI Whisper Core Engine Live"
    }), 200

@app.route("/api/v1/transcribe-audio", methods=["POST", "OPTIONS"])
def transcribe_archival_audio():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
        
    local_filename = None
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"success": False, "error": "Empty payload container matrix."}), 400
            
        file_id = payload.get("fileId")
        direct_file_data = payload.get("fileData")

        local_filename = f"track_stream.mp3"

        # PATHWAY A: Ingest direct file bytes straight from the standalone browser page
        if direct_file_data:
            if isinstance(direct_file_data, str) and "," in direct_file_data:
                base64_string = direct_file_data.split(",")[-1]
            else:
                base64_string = direct_file_data
                
            raw_bytes = base64.b64decode(base64_string)
            with open(local_filename, "wb") as f:
                f.write(raw_bytes)
                
        # PATHWAY B: Fallback download track via Google Drive fileIds safely
        elif file_id:
            drive_url = f"https://google.com{file_id}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            audio_response = requests.get(drive_url, headers=headers, stream=True)
            if audio_response.status_code != 200:
                return jsonify({"success": False, "error": f"Drive stream connection error: {audio_response.status_code}"}), 400
            with open(local_filename, 'wb') as f:
                for file_chunk in audio_response.iter_content(chunk_size=4096):
                    if file_chunk: f.write(file_chunk)
        else:
            return jsonify({"success": False, "error": "No file reference source parameters detected."}), 400

        # Defensive size barrier evaluation
        file_size_mb = os.path.getsize(local_filename) / (1024 * 1024)
        if file_size_mb > 24.5:
            if os.path.exists(local_filename): os.remove(local_filename)
            return jsonify({"success": False, "error": f"Audio track is {file_size_mb:.1f}MB. OpenAI limits Whisper files to 25MB Max."}), 400

        # Transmit compiled asset straight to OpenAI Whisper for Speech-to-Text transcription
        with open(local_filename, "rb") as audio_file:
            transcript_response = client.audio.translations.create(
                model="whisper-1", 
                file=audio_file
            )
        
        if os.path.exists(local_filename):
            os.remove(local_filename)

        return jsonify({
            "success": True,
            "transcribedText": transcript_response.text
        })

    except Exception as e:
        if local_filename and os.path.exists(local_filename): os.remove(local_filename)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

