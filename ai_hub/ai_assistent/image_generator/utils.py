from __future__ import annotations
from typing import Optional

def ensure_vertex_model(project_id: Optional[str], location: Optional[str]):
    try:
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel
    except Exception as e:
        raise RuntimeError(f"Vertex AI SDK not available: {e}") from e

    if not project_id or not location:
        raise RuntimeError("GCP project/location not configured (GCP_PROJECT_ID, GCP_LOCATION).")

    try:
        vertexai.init(project=project_id, location=location)
        return ImageGenerationModel.from_pretrained("imagegeneration@005")
    except Exception as e:
        raise RuntimeError(f"Vertex init failed: {e}") from e

def extract_image_bytes(img_obj) -> bytes | None:
    if hasattr(img_obj, "_image_bytes") and img_obj._image_bytes:
        return img_obj._image_bytes

    if hasattr(img_obj, "as_bytes"):
        try:
            data = img_obj.as_bytes()
            if data:
                return data
        except Exception:
            pass

    try:
        from PIL import Image
        import io
        if isinstance(img_obj, Image.Image):
            buf = io.BytesIO()
            img_obj.save(buf, format="PNG")
            return buf.getvalue()
    except Exception:
        pass

    return getattr(img_obj, "image_bytes", None)

def extract_generation_reasons(result_obj) -> str:
    parts = []
    for attr in ("filters", "reasons", "warnings", "safety_ratings", "safety_attributes"):
        val = getattr(result_obj, attr, None)
        if val:
            parts.append(f"{attr}={val}")
    return "; ".join(parts)
