from __future__ import annotations

import argparse
import json

from prediction.ml_workflow import train_and_save_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train WM match outcome model")
    parser.add_argument("--csv", required=True, help="Path to historical matches CSV")
    parser.add_argument(
        "--output",
        default="models_artifacts/match_outcome_model.joblib",
        help="Output model artifact path",
    )
    args = parser.parse_args()

    result = train_and_save_model(args.csv, args.output)
    print(
        json.dumps(
            {
                "artifact_path": result.artifact_path,
                "train_rows": result.train_rows,
                "accuracy": result.accuracy,
                "log_loss": result.log_loss,
                "trained_at": result.trained_at,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
