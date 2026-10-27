import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any

def run_hypothesis_test(
    sample_a: pd.Series,
    sample_b: pd.Series,
    label_a: str = "High Volume Days",
    label_b: str = "Normal Volume Days",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Executes a formal two-sample Welch's t-test for difference in means,
    reporting H0, H1, alpha, t-statistic, p-value, decision, and academic interpretation.
    """
    clean_a = sample_a.dropna().values
    clean_b = sample_b.dropna().values

    if len(clean_a) < 5 or len(clean_b) < 5:
        return {
            "error": "Insufficient sample sizes for valid hypothesis testing (minimum 5 per group)."
        }

    mean_a, std_a = float(np.mean(clean_a)), float(np.std(clean_a, ddof=1))
    mean_b, std_b = float(np.mean(clean_b)), float(np.std(clean_b, ddof=1))

    # Welch's t-test (equal_var=False)
    t_stat, p_val = stats.ttest_ind(clean_a, clean_b, equal_var=False)

    reject_null = bool(p_val < alpha)

    h0_text = f"The mean return of {label_a} is equal to the mean return of {label_b} (mu_1 = mu_2)."
    h1_text = f"The mean return of {label_a} is significantly different from {label_b} (mu_1 != mu_2)."

    if reject_null:
        decision_text = f"Reject H0 at alpha = {alpha}."
        interpretation = (
            f"The difference in mean returns between {label_a} ({mean_a:.4%}) and {label_b} ({mean_b:.4%}) "
            f"is statistically significant (t = {t_stat:.4f}, p = {p_val:.5f}). "
            f"There is empirical evidence that returns differ across these market regimes."
        )
    else:
        decision_text = f"Fail to reject H0 at alpha = {alpha}."
        interpretation = (
            f"The difference in mean returns between {label_a} ({mean_a:.4%}) and {label_b} ({mean_b:.4%}) "
            f"is not statistically significant at the {alpha*100}% level (t = {t_stat:.4f}, p = {p_val:.5f}). "
            f"We cannot conclude that returns are structurally different between the two regimes."
        )

    return {
        "test_name": "Welch's Two-Sample t-test (Unequal Variances)",
        "null_hypothesis": h0_text,
        "alternative_hypothesis": h1_text,
        "significance_level": alpha,
        "sample_a_label": label_a,
        "sample_a_size": int(len(clean_a)),
        "sample_a_mean": round(mean_a, 6),
        "sample_a_std": round(std_a, 6),
        "sample_b_label": label_b,
        "sample_b_size": int(len(clean_b)),
        "sample_b_mean": round(mean_b, 6),
        "sample_b_std": round(std_b, 6),
        "t_statistic": round(float(t_stat), 4),
        "p_value": round(float(p_val), 6),
        "reject_null": reject_null,
        "decision": decision_text,
        "interpretation": interpretation
    }
