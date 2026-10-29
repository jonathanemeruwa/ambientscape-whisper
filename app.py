import os
import json
import base64
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.url_map.strict_slashes = False

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# SINGLE DOMAIN HTML MODULE: Serves your unblocked frontend dashboard straight from your server core
HTML_PORTAL = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ambientscape Audio Transcription Engine</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #141312; color: #ffffff; padding: 20px; margin: 0; }
    .container { max-width: 600px; margin: 0 auto; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
    h2 { text-transform: uppercase; letter-spacing: 0.08em; font-size: 18px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 10px; margin-top: 0; }
    input[type="file"] { width: 100%; box-sizing: border-box; padding: 12px; background: #ffffff; color: #1a1a1a; border-radius: 4px; border: none; margin-bottom: 20px;}
    button { background: #ffffff; color: #111111; border: none; padding: 15px; width: 100%; font-weight: 700; text-transform: uppercase; border-radius: 4px; cursor: pointer; font-size: 12px; transition: background 0.2s; }
    button:hover { background: #e1e0da; }
    button:disabled { background: #444; color: #888; cursor: not-allowed; }
    .status { display: none; margin-top: 20px; padding: 12px; background: rgba(43, 114, 227, 0.1); border: 1px solid rgba(43, 114, 227, 0.3); border-radius: 4px; font-size: 13px; text-align: center; }
    .result-box { display: none; margin-top: 25px; background: #ffffff; color: #1a1a1a; padding: 20px; border-radius: 4px; }
    .result-content { font-size: 14px; line-height: 1.6; white-space: pre-wrap; font-family: monospace; background: #f7f5f0; padding: 12px; border-radius: 4px; }
  </style>
</head>
<body>
<div class="container">
  <h2>Sound Carrier Forensic Interpreter</h2>
  <input type="file" id="audioFile" accept="audio/*">
  <button id="transcribeBtn" onclick="executeChunkedAcousticAnalysis()">Extract Spoken Lyrics</button>
  <div id="statusIndicator" class="status">Streaming audio binary safely to your OpenAI Whisper cloud...</div>
  <div id="resultWrapper" class="result-box">
    <div style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: #666; margin-bottom: 10px;">📝 Verified OpenAI Transcript Output</div>
    <div id="textContent" class="result-content"></div>
  </div>
</div>
<script>
async function executeChunkedAcousticAnalysis() {
  const fileInput = document.getElementById("audioFile");
  const transcribeBtn = document.getElementById("transcribeBtn");
  const statusIndicator = document.getElementById("statusIndicator");
  const resultWrapper = document.getElementById("resultWrapper");
  const textContent = document.getElementById("textContent");
  
  if (!fileInput.files || fileInput.files.length === 0) { alert("Please select an audio file first."); return; }
  const targetTrackFile = fileInput.files[0];
  
  transcribeBtn.disabled = true;
  statusIndicator.style.display = "block";
  resultWrapper.style.display = "none";
  
  const CHUNK_SIZE = 1024 * 1024; 
  const totalChunks = Math.ceil(targetTrackFile.size / CHUNK_SIZE);
  const uploadId = "upload_" + Date.now();
  
  // UNBLOCKED TARGET ROUTE: Hits the exact same relative server domain layout seamlessly!
  const pythonEndpoint = "/api/v1/transcribe-audio";
  
  for (let currentChunk = 0; currentChunk < totalChunks; currentChunk++) {
    const start = currentChunk * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, targetTrackFile.size);
    const fileSlice = targetTrackFile.slice(start, end);
    
    statusIndicator.innerText = `Streaming audio block ${currentChunk + 1} of ${totalChunks}...`;
    
    const base64Data = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const resultString = reader.result;
        const commaIndex = resultString.indexOf(",");
        resolve(commaIndex !== -1 ? resultString.substring(commaIndex + 1) : resultString);
      };
      reader.readAsDataURL(fileSlice);
    });
    
    try {
      const response = await fetch(pythonEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fileData: base64Data,
          filename: targetTrackFile.name,
          uploadId: uploadId,
          isChunked: true,
          chunkIndex: currentChunk,
          totalChunks: totalChunks
        })
      });
      
      const data = await response.json();
      if (!data.success) { throw new Error(data.error || "Chunk assembly breakdown"); }
      
      if (currentChunk === totalChunks - 1) {
        statusIndicator.style.display = "none";
        transcribeBtn.disabled = false;
        textContent.innerText = data.transcribedText || "[No speech signatures detected]";
        resultWrapper.style.display = "block";
                // =======================================================================
        // GOOGLE SHEET MASTER LOGGING PIPELINE INTEGRATION
        // =======================================================================
        fetch("https://script.google.com/macros/s/AKfycbzscByQr-1jQEJrTp7ldOOSHv2zd3dmJ6207CeIYt8SRI_ldLugM-FaQOq_AbdD5uErNw/exec", {
          method: "POST",
          mode: "no-cors",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            filename: targetTrackFile.name,
            carrierType: "Digital Audio Transfer",
            researcherNotes: "Direct standalone transcription engine transmission.",
            audioData: null
          })
        }).then(() => console.log("Database entry logged successfully."));

      }
    } catch (err) {
      statusIndicator.style.display = "none";
      transcribeBtn.disabled = false;
      alert("Transmission Pipeline Blocked: " + err.message);
      return;
    }
  }
}
</script>
</body>
</html>
"""

@app.route("/", methods=["GET", "HEAD", "OPTIONS"])
def server_root_handshake():
    return HTML_PORTAL

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
        
        with open(local_filename, "ab" if chunk_idx > 0 else "wb") as f:
            f.write(raw_bytes)
        if chunk_idx == total_chunks - 1:
            with open(local_filename, "rb") as file_audio:
                transcript_response = client.audio.translations.create(
                    model="whisper-1",
                    file=file_audio,
                    prompt="Listen closely to the spoken archival announcement at the very beginning of this track. First, predict and extract the metadata using this exact header format: [PREDICTED TITLE: ... | PREDICTED ARTIST: ... | PREDICTED RECORD LABEL: ... | PREDICTED LABELLER: ...]. After writing that header, provide the full, clean conversational translation text below it."
                )
            
            if os.path.exists(local_filename):
                os.remove(local_filename)
                
            return jsonify({"success": True, "transcribedText": transcript_response.text})

        return jsonify({"success": True, "message": "Fragment stashed cleanly."}), 200
            
            

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
