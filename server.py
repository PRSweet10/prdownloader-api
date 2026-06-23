import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="PR Downloader API")

class URLRequest(BaseModel):
    url: str
    format: str = "Video MP4"  # Default format

@app.get("/")
def health_check():
    return {"status": "ok", "message": "PR Downloader API is running"}

@app.post("/api/extract")
async def extract_info(request: URLRequest):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'cookies.txt', # Use cookies if available
    }

    if "Audio" in request.format:
        ydl_opts['format'] = 'bestaudio/best'
    else:
        # Request a pre-merged mp4 that contains both video and audio
        # This is critical for iOS since it cannot run ffmpeg locally to merge streams.
        ydl_opts['format'] = 'best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            # Handling playlist
            if 'entries' in info:
                # Just take the first video for simplicity
                if len(info['entries']) > 0:
                    info = info['entries'][0]
                else:
                    raise HTTPException(status_code=400, detail="Playlist is empty")

            direct_url = info.get('url')
            title = info.get('title', 'Unknown Video')
            thumbnail = info.get('thumbnail', '')
            ext = info.get('ext', 'mp4')
            headers = info.get('http_headers', {})

            if not direct_url:
                raise HTTPException(status_code=400, detail="Could not extract direct URL")

            return {
                "status": "success",
                "title": title,
                "url": direct_url,
                "thumbnail": thumbnail,
                "ext": ext,
                "headers": headers
            }
            
    except Exception as e:
        print(f"Error extracting URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
