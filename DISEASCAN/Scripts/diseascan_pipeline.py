# diseascan_pipeline.py

TARGET_CLASSES = ["akiec", "bcc", "bkl", "df", "melanoma", "nevus", "vasc"]

# Exact mapping (you can expand this later)
EXACT_MAP = {
    "akiec": "akiec",
    "bcc": "bcc",
    "bkl": "bkl",
    "df": "df",
    "melanoma": "melanoma",
    "nv": "nevus",
    "nevus": "nevus",
    "vasc": "vasc"
}

def normalize_label(label):
    if label is None:
        return None

    label = str(label).lower().strip()

    # ✅ Exact match
    if label in EXACT_MAP:
        return EXACT_MAP[label]

    # =========================
    # 🔥 PRIORITY RULES (ORDER MATTERS)
    # =========================

    # AKIEC (must come BEFORE keratosis rule)
    if "actinic" in label or "bowen" in label or "intraepithelial" in label:
        return "akiec"

    # MELANOMA
    if "melanoma" in label:
        return "melanoma"

    # NEVUS
    if "nevus" in label or "nevi" in label or label == "nv":
        return "nevus"

    # BCC
    if "basal cell" in label or "bcc" in label:
        return "bcc"

    # DF
    if "dermatofibroma" in label or "histiocytoma" in label:
        return "df"

    # VASC
    if "angioma" in label or "vascular" in label or "hemangioma" in label:
        return "vasc"

    # BKL (keep keratosis LAST)
    if "keratosis" in label or "lentigo" in label or "lplk" in label:
        return "bkl"

    return None