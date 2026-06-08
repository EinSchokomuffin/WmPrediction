from __future__ import annotations

import argparse
import json

from core.database import Base, engine
from models import db as _db_models
from prediction.ml_workflow import train_and_save_model
from tournament.service import service


def main() -> None:
    parser = argparse.ArgumentParser(description="Train WM match outcome model")
    parser.add_argument("--csv", required=True, help="Path to historical matches CSV")
    parser.add_argument(
        "--output",
        default="models_artifacts/match_outcome_model.joblib",
        help="Output model artifact path",
    )
    parser.add_argument(
        "--skip-db-persist",
        action="store_true",
        help="Train model artifact only and skip writing a model training run into the database.",
    )
    args = parser.parse_args()

    if args.skip_db_persist:
        result = train_and_save_model(args.csv, args.output)
        payload = {
            "artifact_path": result.artifact_path,
            "train_rows": result.train_rows,
            "accuracy": result.accuracy,
            "log_loss": result.log_loss,
            "trained_at": result.trained_at,
            "persisted": False,
        }
    else:
        Base.metadata.create_all(bind=engine)
        payload = service.train_model(args.csv, args.output)
        payload["persisted"] = True

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
