import os
import base64
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.url_map.strict_slashes = False

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.after_request
def apply_global_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route("/", methods=["GET", "POST", "HEAD", "OPTIONS"])
def server_root_handshake():
    return jsonify({"success": True, "status": "online"}), 200

@app.route("/api/v1/transcribe-audio", methods=["POST", "OPTIONS"])
def transcribe_archival_audio():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
        
    try:
        payload = request.get_json() or {}
        file_data = payload.get("fileData")
        filename = payload.get("filename", "track_stream.mp3")
        upload_id = payload.get("uploadId", "default")
        chunk_idx = payload.get("chunkIndex", 0)
        total_chunks = payload.get("totalChunks", 1)
        
        local_filename = f"stashed_{upload_id}_{filename}"
        raw_bytes = base64.b64decode(file_data)
        
        # Sequentially stitch data blocks onto your server's disk space
        with open(local_filename, "ab" if chunk_idx > 0 else "wb") as f:
            f.write(raw_bytes)
            
        # If there are more fragments coming down the pipeline, reply with success and wait
        if chunk_idx < total_chunks - 1:
            return jsonify({"success": True, "message": "Fragment cached successfully."}), 200

        # FINAL CHUNK ARRIVED: Call OpenAI Whisper using your complete file layout
        with open(local_filename, "rb") as audio_file:
            transcript_response = client.audio.translations.create(
                model="whisper-1", 
                file=audio_file
            )
        
        if os.path.exists(local_filename): os.remove(local_filename)
        return jsonify({"success": True, "transcribedText": transcript_response.text})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
