# MiMo MCP TTS — Audio Path Resolution

## Problem
`mcp_mimo_mcp_mimo_tts` returns paths relative to the MCP server's working directory:
```json
{"audio_path": "data/artifacts/tts/20260620/ee6987a6e5d24e66a2b625b4198a5954.wav"}
```

This is NOT an absolute path — prepending the user's home directory won't work.

## Root Directory
The MiMo MCP server runs from:
```
~/.workbuddy/mimo-mcp/
```

Full artifact path:
```
~/.workbuddy/mimo-mcp/data/artifacts/tts/YYYYMMDD/<filename>.wav
```

## Resolution Workflow

### 1. If TTS returns a relative path
```bash
find ~/.workbuddy/mimo-mcp -name "<filename>" 2>/dev/null
```

### 2. Convert to Telegram-compatible Opus (voice bubble)
```bash
ffmpeg -y -i <wav_path> -c:a libopus -b:a 24k /tmp/<output_name>.ogg
```

### 3. Concatenate multiple WAVs into one Opus
```bash
ffmpeg -y -i "concat:<wav1>|<wav2>|<wav3>" -c:a libopus -b:a 24k /tmp/<output>.ogg
```

### 4. Send as voice message
```
MEDIA:/tmp/<output>.ogg
```
Telegram plays .ogg files sent as voice as native voice bubbles.

## Voice Design
Custom voices are created via `mimo_voice_design_create` and referenced by `voice_id=design_<uuid>`.
Harry's preferred Spanish teacher voice: `design_49712b031a14` (Carlos — 西班牙本土男声，慢速 0.85-0.9x, warm and clear).

## Pitfall
- MiMo TTS output is always WAV. Don't try to play it directly — convert to Opus first.
- The `bytes` field in the response is informational. Actual files may differ slightly in size.
