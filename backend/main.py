import os
import time
import httpx
import zipfile
import json
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
from PIL import Image

load_dotenv()

app = FastAPI(title="MirrorMe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

YOUCAM_API_KEY = os.getenv("YOUCAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUCAM_BASE = "https://yce-api-01.makeupar.com/s2s/v2.0"

groq_client = Groq(api_key=GROQ_API_KEY)

GARMENT_CATALOG = [
    {
        "id": "g001",
        "name": "Beige Elegant Outfit",
        "color": "Warm Beige",
        "color_hex": "#C8A882",
        "neckline": "Classic crew",
        "fabric": "Cotton blend",
        "category": "full_body",
        "price": "$89",
        "image_url": "https://res.cloudinary.com/tqvpvmwn/image/upload/v1784583228/pexels-dima-valkov-1186343-6211619_yhiy70.jpg",
        "tags": ["casual", "elegant", "neutral"]
    },
    {
        "id": "g002",
        "name": "Cobalt Blue Blouse",
        "color": "Cobalt Blue",
        "color_hex": "#0047AB",
        "neckline": "Relaxed V-neck",
        "fabric": "Silk blend",
        "category": "upper_body",
        "price": "$72",
        "image_url": "https://res.cloudinary.com/tqvpvmwn/image/upload/v1784583226/pexels-saulo-leite-1491182-17502689_icspnp.jpg",
        "tags": ["office", "bold", "jewel tone"]
    },
    {
        "id": "g003",
        "name": "Red Statement Dress",
        "color": "Deep Red",
        "color_hex": "#8B0000",
        "neckline": "Scoop neck",
        "fabric": "Jersey",
        "category": "full_body",
        "price": "$95",
        "image_url": "https://res.cloudinary.com/tqvpvmwn/image/upload/v1784583224/pexels-wayne-fotografias-1812121-14924694_gxbe1f.jpg",
        "tags": ["bold", "evening", "statement"]
    },
    {
        "id": "g004",
        "name": "Ivory Linen Blouse",
        "color": "Soft Ivory",
        "color_hex": "#FFFFF0",
        "neckline": "Relaxed crew",
        "fabric": "Linen",
        "category": "upper_body",
        "price": "$55",
        "image_url": "https://plugins-media.makeupar.com/strapi/assets/clothes_03_cccd5d4803.jpeg",
        "tags": ["casual", "daywear", "soft"]
    },
    {
        "id": "g005",
        "name": "Burgundy Midi Dress",
        "color": "Deep Burgundy",
        "color_hex": "#800020",
        "neckline": "Scoop neck",
        "fabric": "Jersey",
        "category": "full_body",
        "price": "$75",
        "image_url": "https://res.cloudinary.com/tqvpvmwn/image/upload/v1784583224/pexels-wayne-fotografias-1812121-14924694_gxbe1f.jpg",
        "tags": ["smart casual", "versatile", "rich tone"]
    },
    {
        "id": "g006",
        "name": "Charcoal Wide-Leg Suit",
        "color": "Charcoal",
        "color_hex": "#36454F",
        "neckline": "Lapel collar",
        "fabric": "Wool blend",
        "category": "full_body",
        "price": "$145",
        "image_url": "https://res.cloudinary.com/tqvpvmwn/image/upload/v1784583228/pexels-dima-valkov-1186343-6211619_yhiy70.jpg",
        "tags": ["power dressing", "formal", "neutral"]
    },
    {
        "id": "g007",
        "name": "Terracotta Linen Set",
        "color": "Terracotta",
        "color_hex": "#E2725B",
        "neckline": "Relaxed V",
        "fabric": "Linen",
        "category": "full_body",
        "price": "$98",
        "image_url": "https://res.cloudinary.com/tqvpvmwn/image/upload/v1784583228/pexels-dima-valkov-1186343-6211619_yhiy70.jpg",
        "tags": ["earthy", "summer", "warm tone"]
    },
    {
        "id": "g008",
        "name": "Navy Wrap Blouse",
        "color": "Navy",
        "color_hex": "#000080",
        "neckline": "Deep V wrap",
        "fabric": "Silk blend",
        "category": "upper_body",
        "price": "$72",
        "image_url": "https://res.cloudinary.com/tqvpvmwn/image/upload/v1784583226/pexels-saulo-leite-1491182-17502689_icspnp.jpg",
        "tags": ["classic", "versatile", "cool tone"]
    }
]


def resize_image(image_bytes: bytes) -> bytes:
    """Resize image to meet YouCam 480px minimum requirement."""
    print(f"[RESIZE] Input size: {len(image_bytes)} bytes")
    img = Image.open(io.BytesIO(image_bytes))
    print(f"[RESIZE] Original dimensions: {img.size}, mode: {img.mode}")
    w, h = img.size
    min_side = min(w, h)
    if min_side < 600:
        scale = 600 / min_side
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        print(f"[RESIZE] Resized to: {img.size}")
    if img.mode != 'RGB':
        img = img.convert('RGB')
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=95)
    result = output.getvalue()
    print(f"[RESIZE] Output size: {len(result)} bytes")
    return result


def youcam_headers():
    return {
        "Authorization": f"Bearer {YOUCAM_API_KEY}",
        "Content-Type": "application/json"
    }


async def upload_to_youcam(image_bytes: bytes, filename: str, endpoint: str) -> str:
    """Upload image to YouCam S3 and return file_id."""
    file_size = len(image_bytes)
    safe_filename = "photo.jpg"
    print(f"[UPLOAD] Uploading {file_size} bytes to endpoint: {endpoint}")

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{YOUCAM_BASE}/file/{endpoint}",
            headers=youcam_headers(),
            json={"files": [{"content_type": "image/jpeg", "file_name": safe_filename, "file_size": file_size}]}
        )
        resp_data = resp.json()
        print(f"[UPLOAD] File init response: {resp_data.get('status')}")

        if resp_data.get("status") != 200:
            raise HTTPException(status_code=400, detail=f"YouCam file init failed: {resp_data}")

        file_info = resp_data["data"]["files"][0]
        file_id = file_info["file_id"]
        upload_url = file_info["requests"][0]["url"]
        upload_headers = file_info["requests"][0]["headers"]

        upload_resp = await client.put(
            upload_url,
            content=image_bytes,
            headers=upload_headers
        )
        print(f"[UPLOAD] S3 upload status: {upload_resp.status_code}")

        if upload_resp.status_code not in [200, 204]:
            raise HTTPException(status_code=400, detail=f"S3 upload failed: {upload_resp.status_code}")

        return file_id


async def poll_task(endpoint: str, task_id: str, max_attempts: int = 60) -> dict:
    """Poll YouCam task until success or error."""
    print(f"[POLL] Polling {endpoint} task: {task_id}")
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(max_attempts):
            resp = await client.get(
                f"{YOUCAM_BASE}/task/{endpoint}/{task_id}",
                headers=youcam_headers()
            )
            data = resp.json()
            task_status = data.get("data", {}).get("task_status")
            print(f"[POLL] Attempt {attempt+1}: status = {task_status}")

            if task_status == "success":
                return data["data"]
            elif task_status == "error":
                error = data.get("data", {}).get("error", "unknown")
                error_msg = data.get("data", {}).get("error_message", "")
                print(f"[POLL] Error: {error} - {error_msg}")
                raise HTTPException(status_code=400, detail=f"YouCam task error: {error}")

            time.sleep(2)

    raise HTTPException(status_code=408, detail="Task timed out after 120 seconds")


async def parse_skin_scores(result_data: dict) -> dict:
    """Parse skin analysis result."""
    print(f"[PARSE] Result keys: {list(result_data.keys())}")
    results = result_data.get("results", {})
    print(f"[PARSE] Results keys: {list(results.keys()) if isinstance(results, dict) else type(results)}")

    if "output" in results:
        output = results["output"]
        scores = {}
        for item in output:
            scores[item["type"]] = {
                "ui_score": item.get("ui_score"),
                "raw_score": item.get("raw_score")
            }
        print(f"[PARSE] Parsed {len(scores)} scores from output array")
        return scores

    download_url = None
    if isinstance(results, dict):
        download_url = results.get("url") or results.get("download_url")

    if download_url:
        print(f"[PARSE] Downloading from URL: {download_url[:60]}...")
        async with httpx.AsyncClient(timeout=30) as client:
            zip_resp = await client.get(download_url)
            content_type = zip_resp.headers.get("content-type", "")
            print(f"[PARSE] Download content-type: {content_type}")

            try:
                zip_bytes = zip_resp.content
                with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                    print(f"[PARSE] ZIP contents: {zf.namelist()}")
                    for name in zf.namelist():
                        if "score_info.json" in name:
                            with zf.open(name) as f:
                                data = json.load(f)
                                print(f"[PARSE] Parsed score_info.json with keys: {list(data.keys())[:5]}")
                                return data
            except Exception as e:
                print(f"[PARSE] Not a ZIP: {e}")
                try:
                    data = zip_resp.json()
                    print(f"[PARSE] Parsed as JSON: {list(data.keys())[:5]}")
                    return data
                except Exception as e2:
                    print(f"[PARSE] Not JSON either: {e2}")

    print("[PARSE] Could not parse scores, returning empty dict")
    return {}


def run_style_agent(skin_scores: dict) -> dict:
    """Run Groq agent to get garment recommendations."""

    def get_score(key, subkey=None):
        val = skin_scores.get(key, {})
        if subkey and isinstance(val, dict):
            val = val.get(subkey, {})
        if isinstance(val, dict):
            return float(val.get("raw_score") or val.get("ui_score") or val.get("score") or 50)
        if isinstance(val, (int, float)):
            return float(val)
        return 50.0

    radiance = get_score("radiance") or get_score("hd_radiance")
    redness = get_score("redness") or get_score("hd_redness")
    moisture = get_score("moisture") or get_score("hd_moisture")
    acne = get_score("acne") or get_score("hd_acne", "whole")
    texture = get_score("texture") or get_score("hd_texture", "whole")
    oiliness = get_score("oiliness") or get_score("hd_oiliness")
    overall = float(skin_scores.get("all", {}).get("score", 70))
    skin_age = skin_scores.get("skin_age", "unknown")

    print(f"[AGENT] Scores - radiance:{radiance} redness:{redness} moisture:{moisture} overall:{overall}")

    catalog_text = json.dumps([
        {"id": g["id"], "name": g["name"], "color": g["color"],
         "neckline": g["neckline"], "fabric": g["fabric"], "tags": g["tags"]}
        for g in GARMENT_CATALOG
    ], indent=2)

    prompt = f"""You are MirrorMe's Style Intelligence Agent. Analyze real skin data and recommend clothing.

SKIN ANALYSIS (from YouCam API):
- Overall Score: {overall:.1f}/100
- Skin Age: {skin_age}
- Radiance: {radiance:.1f}/100
- Redness: {redness:.1f}/100
- Moisture: {moisture:.1f}/100
- Acne: {acne:.1f}/100
- Texture: {texture:.1f}/100
- Oiliness: {oiliness:.1f}/100

RULES:
- Radiance > 75: Bold jewel tones amplify glow
- Radiance < 50: Soft ivory, blush, cream tones
- Redness < 50: Cool blues and greens counterbalance
- Moisture < 50: Avoid satin, use matte linen or cotton
- Acne < 50: Solid colors over busy prints
- Overall > 75: Bold choices encouraged
- Overall < 50: Soft flattering tones

GARMENTS:
{catalog_text}

Pick 3 garments. Respond ONLY with JSON, no other text:
{{
  "skin_insight": "One warm sentence about their skin today",
  "recommendations": [
    {{"garment_id": "g001", "confidence_score": 94, "why_it_works": "One sentence why"}},
    {{"garment_id": "g002", "confidence_score": 87, "why_it_works": "One sentence why"}},
    {{"garment_id": "g003", "confidence_score": 79, "why_it_works": "One sentence why"}}
  ]
}}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800
    )

    raw = response.choices[0].message.content.strip()
    print(f"[AGENT] Raw response: {raw[:100]}")

    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    return json.loads(raw)


@app.get("/")
async def root():
    return {"message": "MirrorMe API running", "status": "ok"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "youcam_key_set": bool(YOUCAM_API_KEY),
        "groq_key_set": bool(GROQ_API_KEY)
    }


@app.get("/catalog")
async def get_catalog():
    return {"garments": GARMENT_CATALOG}


@app.post("/analyze-skin")
async def analyze_skin(photo: UploadFile = File(...)):
    print(f"\n[ANALYZE] New request - filename: {photo.filename}, content_type: {photo.content_type}")

    image_bytes = await photo.read()
    print(f"[ANALYZE] Read {len(image_bytes)} bytes")

    # Resize image to meet YouCam requirements
    image_bytes = resize_image(image_bytes)

    # Upload to YouCam skin-analysis endpoint
    file_id = await upload_to_youcam(image_bytes, "photo.jpg", "skin-analysis")
    print(f"[ANALYZE] Got file_id: {file_id[:20]}...")

    # Create skin analysis task
    async with httpx.AsyncClient(timeout=30) as client:
        task_resp = await client.post(
            f"{YOUCAM_BASE}/task/skin-analysis",
            headers=youcam_headers(),
            json={
                "src_file_id": file_id,
                "dst_actions": [
                    "redness", "radiance", "moisture",
                    "acne", "texture", "oiliness", "skin_type"
                ],
                "format": "json"
            }
        )
        task_data = task_resp.json()
        print(f"[ANALYZE] Task creation response: {task_data.get('status')} - {task_data}")

    if task_data.get("status") != 200:
        raise HTTPException(status_code=400, detail=f"Skin analysis task failed: {task_data}")

    task_id = task_data["data"]["task_id"]

    # Poll for result
    result = await poll_task("skin-analysis", task_id)

    # Parse scores
    skin_scores = await parse_skin_scores(result)
    print(f"[ANALYZE] Skin scores: {json.dumps(skin_scores, default=str)[:200]}")

    # Run agent
    agent_output = run_style_agent(skin_scores)

    # Enrich recommendations
    garment_map = {g["id"]: g for g in GARMENT_CATALOG}
    enriched_recs = []
    for rec in agent_output["recommendations"]:
        garment = garment_map.get(rec["garment_id"], {})
        enriched_recs.append({
            **garment,
            "confidence_score": rec["confidence_score"],
            "why_it_works": rec["why_it_works"]
        })

    return {
        "skin_insight": agent_output["skin_insight"],
        "skin_scores": skin_scores,
        "recommendations": enriched_recs
    }


@app.post("/try-on")
async def try_on(photo: UploadFile = File(...), garment_id: str = "g001"):
    print(f"\n[TRYON] garment_id: {garment_id}")
    garment = next((g for g in GARMENT_CATALOG if g["id"] == garment_id), None)
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    image_bytes = await photo.read()
    image_bytes = resize_image(image_bytes)

    file_id = await upload_to_youcam(image_bytes, "photo.jpg", "cloth-v3")
    print(f"[TRYON] Got file_id: {file_id[:20]}...")

    async with httpx.AsyncClient(timeout=30) as client:
        task_resp = await client.post(
            f"{YOUCAM_BASE}/task/cloth-v3",
            headers=youcam_headers(),
            json={
                "src_file_id": file_id,
                "ref_file_url": garment["image_url"],
                "garment_category": garment["category"]
            }
        )
        task_data = task_resp.json()
        print(f"[TRYON] Task response: {task_data}")

    if task_data.get("status") != 200:
        raise HTTPException(status_code=400, detail=f"VTO task failed: {task_data}")

    task_id = task_data["data"]["task_id"]
    result = await poll_task("cloth-v3", task_id)

    result_url = result.get("results", {}).get("url")
    if not result_url:
        raise HTTPException(status_code=400, detail=f"No result URL: {result}")

    return {"vto_image_url": result_url, "garment": garment}