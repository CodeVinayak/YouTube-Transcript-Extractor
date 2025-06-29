from flask import Flask, request, render_template_string, send_file
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import timedelta
import re
import io
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)

app = Flask(__name__)

# Beautiful HTML + CSS template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>YouTube Transcript Extractor</title>
    <style>
        body {
            background: linear-gradient(135deg, #e3f2fd, #90caf9);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 0;
            margin: 0;
        }

        .container {
            max-width: 700px;
            margin: 60px auto;
            background-color: #ffffff;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
        }

        h2 {
            text-align: center;
            color: #1976d2;
        }

        form {
            text-align: center;
            margin-top: 20px;
        }

        input[type="text"] {
            width: 80%;
            padding: 12px;
            border: 1px solid #90caf9;
            border-radius: 10px;
            font-size: 16px;
        }

        button {
            margin-top: 15px;
            background-color: #1976d2;
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 16px;
            border-radius: 10px;
            cursor: pointer;
        }

        button:hover {
            background-color: #1565c0;
        }

        pre {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
        }

        .error {
            color: red;
            text-align: center;
            margin-top: 10px;
        }

        .download-form {
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>YouTube Hindi Transcript Extractor</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Enter YouTube Video URL" required>
            <br>
            <button type="submit">Get Transcript</button>
        </form>

        {% if transcript %}
            <h3>Transcript:</h3>
            <pre>{{ transcript }}</pre>
            <div class="download-form">
                <form method="POST" action="/download">
                    <input type="hidden" name="transcript_text" value="{{ transcript | tojson | safe }}">
                    <button type="submit">Download Transcript</button>
                </form>
            </div>
        {% elif error %}
            <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
'''

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    error = ""
    if request.method == "POST":
        url = request.form["url"]
        video_id = extract_video_id(url)

        if not video_id:
            error = "Invalid YouTube URL."
        else:
            try:
                entries = YouTubeTranscriptApi.get_transcript(video_id, languages=["hi"])
                transcript = "\n".join(
                    [f"[{str(timedelta(seconds=int(e['start'])))}] {e['text']}" for e in entries]
                )
            except Exception as e:
                error = f"Error fetching transcript: {str(e)}"

    return render_template_string(HTML_TEMPLATE, transcript=transcript, error=error)

@app.route("/download", methods=["POST"])
def download():
    text = request.form["transcript_text"]
    buffer = io.BytesIO()
    buffer.write(text.encode('utf-8'))
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="transcript.txt",
        mimetype="text/plain"
    )

if __name__ == "__main__":
    app.run(debug=True)
