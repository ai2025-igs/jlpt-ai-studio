# -*- coding: utf-8 -*-
"""
generate_audio.py
Multi-role Japanese Neural TTS pipeline using edge-tts.
Synthesizes authentic dual-voice Choukai MP3 files for N1, N2, N3, and N4 listening items:
- NARRATOR / QUESTION: ja-JP-NanamiNeural (rate=+0%, pitch=+0Hz)
- MALE: ja-JP-KeitaNeural (rate=-2%, pitch=-3Hz)
- FEMALE: ja-JP-NanamiNeural (rate=+2%, pitch=+5Hz)
"""
import asyncio
import json
import re
from pathlib import Path
import edge_tts

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = BASE_DIR / "audio"

VOICE_CONFIG = {
    "NARRATOR": {"voice": "ja-JP-NanamiNeural", "rate": "+0%", "pitch": "+0Hz"},
    "QUESTION": {"voice": "ja-JP-NanamiNeural", "rate": "-2%", "pitch": "-2Hz"},
    "MALE":     {"voice": "ja-JP-KeitaNeural",  "rate": "-2%", "pitch": "-3Hz"},
    "MALE2":    {"voice": "ja-JP-KeitaNeural",  "rate": "+3%", "pitch": "+3Hz"},
    "FEMALE":   {"voice": "ja-JP-NanamiNeural", "rate": "+2%", "pitch": "+5Hz"},
}

def clean_jp_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return text.strip()

async def synthesize_turn_bytes(text: str, role: str) -> bytes:
    cfg = VOICE_CONFIG.get(role.upper(), VOICE_CONFIG["NARRATOR"])
    comm = edge_tts.Communicate(
        text=clean_jp_text(text),
        voice=cfg["voice"],
        rate=cfg["rate"],
        pitch=cfg["pitch"]
    )
    chunks = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)

async def process_question(q: dict, lvl: str, sem: asyncio.Semaphore) -> str:
    qid = q["id"]
    rel_audio = q.get("audioFile") or f"audio/{lvl.lower()}/{qid}.mp3"
    q["audioFile"] = rel_audio
    out_file = BASE_DIR / rel_audio
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if out_file.exists() and out_file.stat().st_size > 2048:
        return f"CACHED {out_file.name} ({out_file.stat().st_size} B)"

    async with sem:
        dialogue = q.get("dialogue") or []
        audio_parts = []
        if dialogue:
            for turn in dialogue:
                jp = clean_jp_text(turn.get("jp", ""))
                if not jp:
                    continue
                role = turn.get("role", "NARRATOR")
                part_bytes = await synthesize_turn_bytes(jp, role)
                audio_parts.append(part_bytes)
        else:
            jp = clean_jp_text(q.get("ttsText") or q.get("stem", ""))
            part_bytes = await synthesize_turn_bytes(jp, "NARRATOR")
            audio_parts.append(part_bytes)

        full_mp3 = b"".join(audio_parts)
        out_file.write_bytes(full_mp3)
        return f"GENERATED {out_file.name} ({len(full_mp3)} B)"

async def main():
    sem = asyncio.Semaphore(6)
    tasks = []
    seen_audio_files = set()

    for lvl in ["n1", "n2", "n3", "n4", "n5"]:
        bank_path = DATA_DIR / f"{lvl}_bank.json"
        if not bank_path.exists():
            continue
        data = json.loads(bank_path.read_text(encoding="utf-8"))
        for q in data:
            if q.get("category") == "LISTENING":
                rel_audio = q.get("audioFile") or f"audio/{lvl.lower()}/{q['id']}.mp3"
                if rel_audio not in seen_audio_files:
                    seen_audio_files.add(rel_audio)
                    tasks.append(process_question(q, lvl, sem))

    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)

    print(f"Total unique Choukai MP3 files ready: {len(results)}")

if __name__ == "__main__":
    asyncio.run(main())
