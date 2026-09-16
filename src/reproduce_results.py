from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EVAL = ROOT / "evaluation"


def main():
    golden = pd.read_csv(
        EVAL / "golden_eval_americanair_220_FINAL.csv"
    )

    safety = pd.read_csv(
        EVAL / "evidence_safety_gate_americanair.csv"
    )

    improved = pd.read_csv(
        EVAL / "improved_safety_gate_americanair.csv"
    )

    evidence = pd.read_csv(
        EVAL / "evidence_judge_human_agreement_100.csv"
    )

    intent = pd.read_csv(
        EVAL / "intent_classifier_eval_americanair.csv"
    )

    print("=" * 70)
    print("HIVER SDE INTERN — REPRODUCIBILITY SUMMARY")
    print("=" * 70)

    print(f"\nGolden evaluation cases: {len(golden)}")

    intent_accuracy = (
        intent["predicted_intent"] == intent["human_intent"]
    ).mean()

    print(f"Intent accuracy: {intent_accuracy:.4f}")

    auto = safety["system_decision"].eq("AUTO")
    human_auto = safety["human_decision"].eq("AUTO")

    tp = (auto & human_auto).sum()
    fp = (auto & ~human_auto).sum()
    fn = (~auto & human_auto).sum()
    tn = (~auto & ~human_auto).sum()

    precision = tp / (tp + fp) if (tp + fp) else 0
    safe_coverage = tp / human_auto.sum() if human_auto.sum() else 0
    unsafe_rate = fp / len(safety)

    print(f"Safety-gate v1 AUTO decisions: {auto.sum()}")
    print(f"Safety-gate v1 ESCALATE decisions: {(~auto).sum()}")
    print(f"Automation precision: {precision:.4f}")
    print(f"Safe automation coverage: {safe_coverage:.4f}")
    print(f"Unsafe automation rate: {unsafe_rate:.4f}")

    agreement = evidence["agreement"].mean()

    print(f"\nEvidence judge-human agreement: {agreement:.4f}")

    improved_auto = improved["system_decision"].eq("AUTO")

    print(
        f"Stricter safety gate AUTO decisions: "
        f"{improved_auto.sum()}"
    )

    print("\nNote:")
    print(
        "These metrics are diagnostic evaluation results on the "
        "220-case golden set and should not be interpreted as "
        "production performance estimates."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
