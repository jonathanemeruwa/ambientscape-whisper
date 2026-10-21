import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Initialize official OpenAI SDK Client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/api/v1/transcribe-audio", methods=["POST"])
def transcribe_archival_audio():
    local_filename = None
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"success": False, "error": "Empty payload container matrix."}), 400
            
        file_id = payload.get("fileId")
        if not file_id:
            return jsonify({"success": False, "error": "Missing target file ID alignment."}), 400

        # 1. DOWNLOAD THE AUDIO ASSET STREAM VIA GOOGLE DRIVE CORRIDORS
        drive_url = f"https://google.com{file_id}"
        
        # Using a verified browser User-Agent header to bypass standard automated bot blockers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        audio_response = requests.get(drive_url, headers=headers, stream=True)
        if audio_response.status_code != 200:
            return jsonify({"success": False, "error": f"Google Drive source returned status: {audio_response.status_code}"}), 400

        local_filename = f"track_{file_id}.mp3"
        
        # Stream file safely to server space chunk by chunk
        with open(local_filename, 'wb') as f:
            for file_chunk in audio_response.iter_content(chunk_size=4096):
                if file_chunk:
                    f.write(file_chunk)

        # 2. DEFENSIVE GUARDRAIL: Verify file stays safely underneath OpenAI's hard 25MB wall
        file_size_mb = os.path.getsize(local_filename) / (1024 * 1024)
        if file_size_mb > 24.5:
            if os.path.exists(local_filename):
                os.remove(local_filename)
            return jsonify({
                "success": False, 
                "error": f"Audio file is {file_size_mb:.1f}MB. OpenAI limits Whisper to 25MB. Compress track format first."
            }), 400

        # 3. TRANSMIT BINARY FILE STRAIGHT TO OPENAI WHISPER FOR SPEECH-TO-TEXT
        with open(local_filename, "rb") as audio_file:
            transcript_response = client.audio.translations.create(
                model="whisper-1", 
                file=audio_file
            )
        
        # Clean up local file storage instantly
        if os.path.exists(local_filename):
            os.remove(local_filename)

        return jsonify({
            "success": True,
            "transcribedText": transcript_response.text
        })

    except Exception as e:
        if local_filename and os.path.exists(local_filename):
            os.remove(local_filename)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Standard server deployment configuration parameters
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
