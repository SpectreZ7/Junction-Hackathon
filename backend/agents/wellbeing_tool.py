
# wellbeing_agent.py
# v1.0 — Survey- based wellbeing scoring for ride-hailing drivers
# ------------------------------------------------------------------
# Inputs: CSV with columns (per driver):
#   driver_id (str)
#   sleep_hours_last_24h (float)
#   fatigue_level_1to5 (int 1..5)
#   stress_level_1to5  (int 1..5)
#   body_discomfort_1to5 (int 1..5)
#   mood_1to5 (int 1..5)
#   timestamp (ISO string) — optional
#
# Outputs:
#   - Scored CSV with wellbeing_score_0_100, risk_band, suggested_action
#   - Optional JSON lines (one JSON per driver) for orchestrator
#
# Usage examples:
#   python wellbeing_agent.py --in wellbeing_survey.csv --out wellbeing_survey_scored.csv
#   python wellbeing_agent.py --in wellbeing_survey.csv --out wellbeing_survey_scored.csv --json out.jsonl
#
# The scoring is intentionally transparent & tunable via weights in WellbeingConfig.

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional
import math

import pandas as pd


@dataclass
class WellbeingConfig:
    """Weights and thresholds controlling the wellbeing score model."""
    # sleep
    sleep_target_hours: float = 7.0
    sleep_penalty_per_hour: float = 6.0  # points deducted per hour below target 

    # Likert 1..5 penalties 
    fatigue_penalty_per_level: float = 7.0   # (level-1) * weight
    stress_penalty_per_level: float = 5.5
    body_penalty_per_level: float = 4.5

    # positive mood bonus (centered around 3 = neutral)
    mood_bonus_per_level_from_neutral: float = 3.0  # (mood-3)*bonus

    # Risk bands
    band_low_min: float = 80.0
    band_medium_min: float = 60.0
    band_high_min: float = 40.0

    # final score
    min_score: float = 0.0
    max_score: float = 100.0


class WellbeingAgent:
    """Survey-based wellbeing agent that scores drivers and yields actions.

    This agent does NOT look at operational data (hours/trips). 
    """

    def __init__(self, config: Optional[WellbeingConfig] = None):
        self.cfg = config or WellbeingConfig()

    # Scoring
    def score_row(self, r: Dict[str, Any]) -> Tuple[float, str, str, List[str]]:
        """ Parameters
        ----------
        r : dict-like with the required survey fields

        Returns
        -------
        score : float
        band : str in {low, medium, high, critical}
        suggestion : short action string
        factors : list of top factors affecting score (for explanation)
        """
        c = self.cfg

        # Extract
        sleep = self._to_float(r.get("sleep_hours_last_24h", 0.0), default=0.0)
        fatigue = self._to_int(r.get("fatigue_level_1to5", 3), lo=1, hi=5, default=3)
        stress  = self._to_int(r.get("stress_level_1to5", 3), lo=1, hi=5, default=3)
        body    = self._to_int(r.get("body_discomfort_1to5", 2), lo=1, hi=5, default=2)
        mood    = self._to_int(r.get("mood_1to5", 3), lo=1, hi=5, default=3)

        # penalties / bonuses calculated
        p_sleep   = max(0.0, c.sleep_target_hours - sleep) * c.sleep_penalty_per_hour
        p_fatigue = max(0, fatigue - 1) * c.fatigue_penalty_per_level
        p_stress  = max(0, stress - 1)  * c.stress_penalty_per_level
        p_body    = max(0, body - 1)    * c.body_penalty_per_level
        bonus_mood = (mood - 3) * c.mood_bonus_per_level_from_neutral

        raw = 100.0 - (p_sleep + p_fatigue + p_stress + p_body) + bonus_mood
        score = float(min(max(raw, c.min_score), c.max_score))

        # different risk bands
        if score >= c.band_low_min:
            band = "low"
        elif score >= c.band_medium_min:
            band = "medium"
        elif score >= c.band_high_min:
            band = "high"
        else:
            band = "critical"

        # suggestions
        nudges: List[str] = []
        factors: List[str] = []

        if fatigue >= 4 or stress >= 4:
            nudges.append("Take a 10–15 min reset now (walk + water).")
        if sleep < 6:
            nudges.append("Plan an earlier end today; target 7–9h sleep next cycle.")
        if body >= 4:
            nudges.append("Stretch shoulders/neck; adjust seat & lumbar support.")
        if mood <= 2:
            nudges.append("Try a 2‑min breathing exercise before the next ride.")
        if not nudges:
            nudges.append("Safe zone; take a 5‑min micro‑break after next drop‑off.")

        # top factors 
        factors.append(f"sleep {sleep:.1f}h (target {c.sleep_target_hours}h)")
        factors.append(f"fatigue {fatigue}/5")
        factors.append(f"stress {stress}/5")
        factors.append(f"discomfort {body}/5")
        factors.append(f"mood {mood}/5")

        return score, band, nudges[0], factors

    # Batch API 
    def score_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        scores, bands, actions, _factors = [], [], [], []
        for _, row in df.iterrows():
            s, b, a, f = self.score_row(row.to_dict())
            scores.append(round(s, 1))
            bands.append(b)
            actions.append(a)
            _factors.append(f)
        out["wellbeing_score_0_100"] = scores
        out["risk_band"] = bands
        out["suggested_action"] = actions
        out["top_factors"] = _factors
        return out

    def to_jsonl(self, df_scored: pd.DataFrame) -> List[str]:
        lines: List[str] = []
        for _, r in df_scored.iterrows():
            payload = {
                "agent_id": "wellbeing_agent_v1",
                "driver_id": r.get("driver_id"),
                "timestamp": r.get("timestamp"),
                "wellbeing": {
                    "score": float(r["wellbeing_score_0_100"]),
                    "band": r["risk_band"],
                    "suggested_action": r["suggested_action"],
                    "top_factors": r["top_factors"],
                }
            }
            lines.append(json.dumps(payload, ensure_ascii=False))
        return lines

    # Utils
    @staticmethod
    def _to_float(x: Any, default: float = 0.0) -> float:
        try:
            return float(x)
        except Exception:
            return float(default)

    @staticmethod
    def _to_int(x: Any, lo: int = 0, hi: int = 0, default: int = 0) -> int:
        try:
            v = int(round(float(x)))
            if lo != 0: v = max(lo, v)
            if hi != 0: v = min(hi, v)
            return v
        except Exception:
            return int(default)


# CLI
def _parse_args():
    p = argparse.ArgumentParser(description="Wellbeing agent — survey-only scorer")
    p.add_argument("--in", dest="input_csv", required=True, help="Path to survey CSV")
    p.add_argument("--out", dest="output_csv", required=True, help="Path to write scored CSV")
    p.add_argument("--json", dest="jsonl_path", default=None, help="Optional path to write orchestrator JSONL")
    return p.parse_args()


def main():
    args = _parse_args()
    df = pd.read_csv(args.input_csv)
    agent = WellbeingAgent()
    scored = agent.score_dataframe(df)
    scored.to_csv(args.output_csv, index=False)
    if args.jsonl_path:
        lines = agent.to_jsonl(scored)
        with open(args.jsonl_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    print(f"[wellbeing_agent] Wrote: {args.output_csv}" + (f" and {args.jsonl_path}" if args.jsonl_path else ""))


if __name__ == "__main__":
    main()
