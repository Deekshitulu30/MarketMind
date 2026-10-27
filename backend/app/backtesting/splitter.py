import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime

class ChronologicalWalkForwardSplitter:
    """
    Splits time-series datasets into chronological expanding walk-forward folds.
    Ensures zero future-information leakage between training and testing splits.
    """
    @staticmethod
    def generate_walk_forward_folds(
        df_meta: pd.DataFrame,
        n_folds: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Creates expanding window folds.
        Example for 4-5 years:
        Fold 1: Train [0% - 50%], Test [50% - 66%]
        Fold 2: Train [0% - 66%], Test [66% - 83%]
        Fold 3: Train [0% - 83%], Test [83% - 100%]
        """
        n_samples = len(df_meta)
        folds = []

        # Minimum training fraction = 45%
        train_fractions = [0.50, 0.68, 0.84][:n_folds]

        for i, train_frac in enumerate(train_fractions):
            train_end_idx = int(n_samples * train_frac)
            if i < len(train_fractions) - 1:
                test_end_idx = int(n_samples * train_fractions[i+1])
            else:
                test_end_idx = n_samples

            train_dates = df_meta["date"].iloc[:train_end_idx]
            test_dates = df_meta["date"].iloc[train_end_idx:test_end_idx]

            folds.append({
                "fold_id": i + 1,
                "train_indices": (0, train_end_idx),
                "test_indices": (train_end_idx, test_end_idx),
                "train_start_date": train_dates.min().strftime("%Y-%m-%d"),
                "train_end_date": train_dates.max().strftime("%Y-%m-%d"),
                "test_start_date": test_dates.min().strftime("%Y-%m-%d"),
                "test_end_date": test_dates.max().strftime("%Y-%m-%d"),
                "train_size": train_end_idx,
                "test_size": test_end_idx - train_end_idx
            })

        return folds
