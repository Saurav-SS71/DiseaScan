import numpy as np
from typing import Any, Callable
from dataclasses import dataclass


@dataclass
class Prediction:
    label: str
    confidence: float
    rank: int


@dataclass
class StableInferenceResult:
    top_predictions: list[Prediction]   # Top 3 predictions
    averaged_probs: np.ndarray          # Full averaged probability array
    num_runs: int                       # How many runs were averaged


def stable_predict(
    model_fn: Callable[[Any], np.ndarray],
    image: Any,
    class_names: list[str],
    num_runs: int = 5,
    top_k: int = 3,
) -> StableInferenceResult:
    """
    Runs inference multiple times on the same image, averages the
    probability distributions, and returns a stable prediction.

    Args:
        model_fn:    A callable that takes an image and returns a 1-D
                     numpy array of class probabilities (softmax output).
                     Drop-in for model.predict(), model(), pipeline(), etc.
        image:       The input passed unchanged to model_fn on every run.
        class_names: Ordered list of class labels matching the model output.
        num_runs:    Number of forward passes (3–5 recommended). Must be ≥ 1.
        top_k:       Number of top predictions to return (default 3).

    Returns:
        StableInferenceResult with top predictions and averaged probabilities.
    """
    if not (1 <= num_runs <= 10):
        raise ValueError("num_runs should be between 1 and 10.")
    if len(class_names) == 0:
        raise ValueError("class_names must not be empty.")

    # ── Collect probability arrays ────────────────────────────────────────
    all_probs: list[np.ndarray] = []
    for _ in range(num_runs):
        probs = np.asarray(model_fn(image), dtype=np.float64)
        if probs.ndim != 1 or len(probs) != len(class_names):
            raise ValueError(
                f"model_fn must return a 1-D array of length {len(class_names)}; "
                f"got shape {probs.shape}."
            )
        all_probs.append(probs)

    # ── Average across runs ───────────────────────────────────────────────
    avg_probs = np.mean(all_probs, axis=0)

    # Re-normalise in case of minor floating-point drift
    avg_probs = avg_probs / avg_probs.sum()

    # ── Extract top-k predictions ─────────────────────────────────────────
    top_indices = np.argsort(avg_probs)[::-1][:top_k]
    top_predictions = [
        Prediction(
            label=class_names[i],
            confidence=float(avg_probs[i]),
            rank=rank + 1,
        )
        for rank, i in enumerate(top_indices)
    ]

    return StableInferenceResult(
        top_predictions=top_predictions,
        averaged_probs=avg_probs,
        num_runs=num_runs,
    )


# ── Pretty printer ────────────────────────────────────────────────────────────
def print_result(result: StableInferenceResult) -> None:
    print(f"\n{'─'*40}")
    print(f"  Stable Inference  ({result.num_runs} runs averaged)")
    print(f"{'─'*40}")
    for pred in result.top_predictions:
        bar = "█" * int(pred.confidence * 30)
        print(f"  #{pred.rank}  {pred.label:<20} {pred.confidence:6.2%}  {bar}")
    print(f"{'─'*40}\n")


# ── Example usage ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # --- Swap this block for your real model ---
    def mock_model(image):
        """Simulates a model that returns slightly different probs each call."""
        base = np.array([0.05, 0.70, 0.10, 0.08, 0.07])
        noise = np.random.dirichlet(np.ones(5) * 20)   # small stochastic noise
        probs = base * 0.9 + noise * 0.1
        return probs / probs.sum()
    # -------------------------------------------

    CLASSES = ["cat", "dog", "bird", "fish", "rabbit"]
    dummy_image = None   # replace with your actual image / tensor

    result = stable_predict(
        model_fn=mock_model,
        image=dummy_image,
        class_names=CLASSES,
        num_runs=5,       # change to 3–5 as needed
        top_k=3,
    )

    print_result(result)

    # Access programmatically:
    best = result.top_predictions[0]
    print(f"Predicted class : {best.label}")
    print(f"Confidence      : {best.confidence:.2%}")
