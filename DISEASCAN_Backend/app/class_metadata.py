from dataclasses import dataclass
from typing import Literal

Severity = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class LesionMeta:
    code: str
    full_name: str
    severity: Severity
    description: str
    recommendation: str


# ── Master mapping ────────────────────────────────────────────────────────────

LESION_MAP: dict[str, LesionMeta] = {
    "akiec": LesionMeta(
        code="akiec",
        full_name="Actinic Keratosis / Intraepithelial Carcinoma",
        severity="high",
        description=(
            "A rough, scaly patch caused by years of sun exposure. "
            "Considered a pre-cancerous lesion that can progress to "
            "squamous cell carcinoma if left untreated."
        ),
        recommendation=(
            "Prompt dermatologist evaluation is strongly advised. "
            "Treatment options include cryotherapy, topical agents, or "
            "photodynamic therapy depending on extent."
        ),
    ),
    "bcc": LesionMeta(
        code="bcc",
        full_name="Basal Cell Carcinoma",
        severity="high",
        description=(
            "The most common form of skin cancer, arising from basal cells "
            "in the deepest layer of the epidermis. Rarely metastasises but "
            "can cause significant local tissue destruction if neglected."
        ),
        recommendation=(
            "Seek dermatologist or oncologist consultation without delay. "
            "Standard treatments include surgical excision, Mohs surgery, "
            "or radiation therapy."
        ),
    ),
    "bkl": LesionMeta(
        code="bkl",
        full_name="Benign Keratosis-like Lesion",
        severity="low",
        description=(
            "A broad category covering seborrheic keratoses, solar lentigines, "
            "and lichen-planus-like keratoses. These are non-cancerous growths "
            "that are very common with age."
        ),
        recommendation=(
            "No urgent medical action required. Routine annual skin check "
            "is recommended. Removal is optional and typically cosmetic."
        ),
    ),
    "df": LesionMeta(
        code="df",
        full_name="Dermatofibroma",
        severity="low",
        description=(
            "A common, benign fibrous nodule usually found on the legs. "
            "Often caused by minor injuries such as insect bites. "
            "Firm to the touch and may dimple inward when pinched."
        ),
        recommendation=(
            "Generally harmless and requires no treatment. "
            "Consult a dermatologist if the lesion changes in size, colour, "
            "or causes persistent discomfort."
        ),
    ),
    "mel": LesionMeta(
        code="mel",
        full_name="Melanoma",
        severity="high",
        description=(
            "The most dangerous form of skin cancer, arising from melanocytes. "
            "Can metastasise rapidly to lymph nodes and distant organs. "
            "Early detection is critical for favourable outcomes."
        ),
        recommendation=(
            "Immediate referral to a dermatologist or oncologist is essential. "
            "Do not delay — early-stage melanoma is highly treatable, while "
            "advanced stages require systemic therapy."
        ),
    ),
    "nv": LesionMeta(
        code="nv",
        full_name="Melanocytic Nevus (Mole)",
        severity="low",
        description=(
            "A common benign proliferation of melanocytes, typically appearing "
            "as a small, evenly pigmented spot. Most moles are harmless, though "
            "atypical or rapidly changing nevi warrant attention."
        ),
        recommendation=(
            "Monitor regularly using the ABCDE rule "
            "(Asymmetry, Border, Colour, Diameter, Evolution). "
            "Annual skin checks are advisable, especially with a family "
            "history of melanoma."
        ),
    ),
    "vasc": LesionMeta(
        code="vasc",
        full_name="Vascular Lesion",
        severity="medium",
        description=(
            "A group of lesions originating from blood vessels, including "
            "angiomas, angiokeratomas, and pyogenic granulomas. Most are "
            "benign, but pyogenic granulomas can bleed heavily and recur."
        ),
        recommendation=(
            "Dermatologist evaluation is recommended to confirm the subtype. "
            "Pyogenic granulomas should be treated promptly. "
            "Cosmetic removal is available for angiomas if desired."
        ),
    ),
}

# ── Severity colour hints (optional, useful for UIs) ─────────────────────────

SEVERITY_STYLE: dict[Severity, dict] = {
    "low":    {"colour": "#2ecc71", "label": "Low Risk"},
    "medium": {"colour": "#f39c12", "label": "Medium Risk"},
    "high":   {"colour": "#e74c3c", "label": "High Risk — Seek Medical Advice"},
}


# ── Helper: enrich stable_predict output ─────────────────────────────────────

def enrich_predictions(top_predictions: list) -> list[dict]:
    """
    Takes the top_predictions list from StableInferenceResult and attaches
    full metadata to each entry.

    Args:
        top_predictions: list of Prediction dataclasses from stable_inference.py

    Returns:
        List of dicts with prediction fields + full LesionMeta fields.
    """
    enriched = []
    for pred in top_predictions:
        meta = LESION_MAP.get(pred.label)
        if meta is None:
            raise KeyError(f"No metadata found for class code '{pred.label}'.")

        style = SEVERITY_STYLE[meta.severity]
        enriched.append({
            "rank":           pred.rank,
            "code":           meta.code,
            "full_name":      meta.full_name,
            "confidence":     pred.confidence,
            "severity":       meta.severity,
            "severity_label": style["label"],
            "severity_color": style["colour"],
            "description":    meta.description,
            "recommendation": meta.recommendation,
        })
    return enriched


# ── Pretty printer ────────────────────────────────────────────────────────────

def print_enriched(enriched: list[dict]) -> None:
    SEV_ICONS = {"low": "🟢", "medium": "🟡", "high": "🔴"}
    print(f"\n{'═'*60}")
    print("  Skin Lesion Analysis — Enriched Predictions")
    print(f"{'═'*60}")
    for e in enriched:
        icon = SEV_ICONS[e["severity"]]
        print(f"\n  #{e['rank']}  {e['full_name']}  ({e['code']})")
        print(f"       Confidence : {e['confidence']:.2%}")
        print(f"       Severity   : {icon}  {e['severity_label']}")
        print(f"       Info       : {e['description'][:80]}…")
        print(f"       Action     : {e['recommendation'][:80]}…")
    print(f"\n{'═'*60}\n")


# ── Drop-in demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simulate output from stable_inference.py
    from dataclasses import dataclass as dc

    @dc
    class _MockPred:
        label: str
        confidence: float
        rank: int

    mock_top3 = [
        _MockPred(label="mel",   confidence=0.72, rank=1),
        _MockPred(label="akiec", confidence=0.18, rank=2),
        _MockPred(label="nv",    confidence=0.06, rank=3),
    ]

    enriched = enrich_predictions(mock_top3)
    print_enriched(enriched)

    # Access any field directly:
    print("Top prediction full name :", enriched[0]["full_name"])
    print("Top prediction action    :", enriched[0]["recommendation"])
