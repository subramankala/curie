---
name: pi-camera-whatsapp
description: Capture a live photo from the local Adeept robot camera on this Raspberry Pi host and send it back in the current OpenClaw chat, especially WhatsApp. Use by default for short phrases like take a photo, take photo, snap a picture, show me what you see, camera photo, or send a picture. If the user addresses the assistant as Curie and asks for a photo, prefer this skill. Do not use a phone camera or connected nodes for this skill.
metadata:
  {
    "openclaw":
      {
        "emoji": "📷",
        "os": ["linux"],
        "requires": { "bins": ["rpicam-still"] },
      },
  }
---

# pi-camera-whatsapp

Use this skill when the user wants a fresh image from the local Adeept robot camera on this Raspberry Pi host.

For normal OpenClaw chats, especially inbound WhatsApp chats, do not use `wacli`.
Capture the image locally and reply in the current conversation with the image as outbound media.

Default assumption for ambiguous requests:

- `take a photo`
- `take photo`
- `snap a picture`
- `show me what you see`
- `camera photo`
- `curie take a photo`

All of these should mean: use the local Adeept robot camera on this Pi unless the user explicitly says phone camera.

This robot has only one camera degree of freedom: tilt only.
If the user asks for a photo while looking `up`, `straight`, or `down`, reposition tilt first with the calibrated Adeept look helper, then capture.
Do not invent camera pan. For left/right viewpoints, use the dedicated `adeept-look` skill to rotate the chassis first if the user explicitly asks for that.

Routing rules:

- Always run locally on the Raspberry Pi host.
- Never use connected nodes for this skill.
- Never use a phone camera for this skill unless the user explicitly asks for the phone camera.

## Workflow

1. If needed, reposition the robot view:
   `python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py up|straight|down`
2. Run `scripts/take-photo.sh` from this skill directory.
3. Let it save into the agent workspace under `./out/`.
4. Reply with a short caption and set `mediaUrl` to the saved workspace-relative image path.

## Command

```bash
bash skills/pi-camera-whatsapp/scripts/take-photo.sh
```

Optional view positioning:

```bash
python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py straight
bash skills/pi-camera-whatsapp/scripts/take-photo.sh
```

Optional custom caption or filename stem is fine, but keep the output path inside `./out/`.

When OpenClaw is uncertain, prefer this exact host-local pattern:

```bash
bash /home/curie/openclaw/skills/pi-camera-whatsapp/scripts/take-photo.sh ./out camera straight
```

## Reply shape

Return a normal assistant reply for the current chat with:

- `text`: a short caption such as `Fresh camera photo.`
- `mediaUrl`: the generated `./out/...jpg` path

If the capture fails, explain the failure briefly instead of inventing an image.

## Notes

- Prefer `rpicam-still`; fall back to `libcamera-still` only if needed.
- Use `-n` to avoid preview windows.
- Do not write outside the workspace for routine chat replies.
- One photo is usually enough unless the user asks for more.
- Calibrated tilt positions on this robot are: `up=75`, `straight=48`, `down=20`.
- If OpenClaw starts talking about phones, mobile devices, or connected nodes, that is the wrong routing choice for this skill.
