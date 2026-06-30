# Demo Video Narration: MiMo TTS + FFmpeg

**Purpose:** Add AI-narrated voiceover to programmatically-generated demo videos (e.g., Remotion).

## Prerequisites
- MiMo MCP running (TTS tool available)
- FFmpeg installed (`brew install ffmpeg` on macOS)
- Video file ready (Remotion output or other)

## Steps

### 1. Generate narration with MiMo TTS

```python
# Via Mimo MCP tool
mimo_tts(text="your narration script", voice="Chloe")
```

Voice options: Chloe, Mia, Milo, Dean, 冰糖, 茉莉, 苏打, 白桦, or cloned voice_id.

**Narration script guidelines:**
- Write for ~30s for a short demo, ~60s for product walkthrough
- Keep sentences short (breath points)
- State value proposition in first 3 seconds
- Match scene transitions (if possible, split into per-scene segments)

### 2. Locate the generated audio

```bash
# MiMo stores audio in its working directory
ls -lt ~/.workbuddy/mimo-mcp/data/artifacts/tts/2026*/ | head -3
# Most recent .wav file
LATEST=$(ls -t ~/.workbuddy/mimo-mcp/data/artifacts/tts/20*/*.wav 2>/dev/null | head -1)
```

### 3. Mix audio with video using FFmpeg

```bash
FFMPEG=$(which ffmpeg)
$FFMPEG -y \
  -i video.mp4 \
  -i narration.wav \
  -c:v copy \
  -c:a aac -b:a 192k \
  -shortest \
  video-narrated.mp4
```

**Flags explained:**
- `-c:v copy` — copy video stream without re-encoding (fast)
- `-c:a aac -b:a 192k` — encode audio as AAC 192kbps
- `-shortest` — stop at the shorter of video or narration (narration longer? cut. Video longer? audio ends early)

### 4. Deploy to web server

```bash
cp video-narrated.mp4 ~/www/factcheck/doublecheck.mp4
```

## Pitfalls

- **Narration timing mismatch:** If narration is 49s but video is 36s, `-shortest` cuts narration. Write narration to match video duration, or split into per-scene segments manually.
- **MiMo output format:** WAV (large, ~2.4MB for 50s). FFmpeg converts to AAC for final output (~10KB audio in a 2MB MP4).
- **Narration naturalness:** Chloe voice is the most natural English voice. For Chinese, use 冰糖 or 茉莉.
- **Async rendering:** If the Remotion video needs re-rendering, do that before generating narration (or generate both in parallel if duration is fixed).
