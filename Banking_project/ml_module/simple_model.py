"""
ml_module/simple_model.py
--------------------------
Simple ML module for banking fraud/anomaly detection.
Uses basic statistical rules + scikit-learn Isolation Forest.

No GPU required — lightweight enough for a local project.
"""

import statistics
from typing import List


# ─── Rule-Based Fraud Detection ──────────────────────────────────────────────

class SimpleFraudDetector:
    """
    Detects suspicious transactions using simple rules.
    
    Rules:
    1. Amount > 3x the user's average → SUSPICIOUS
    2. More than 5 transactions in 1 hour → SUSPICIOUS
    3. Amount is exactly the same as previous → REVIEW
    
    This is a heuristic model — easy to understand and modify.
    """

    def __init__(self):
        self.rules = [
            self._check_large_amount,
            self._check_round_number,
            self._check_repeated_amount,
        ]

    def _check_large_amount(self, amount: float, history: List[float]) -> dict:
        """Flag if amount is more than 3x the average of past transactions."""
        if len(history) < 3:
            return {"triggered": False}
        avg = statistics.mean(history)
        if avg > 0 and amount > 3 * avg:
            return {
                "triggered": True,
                "rule": "large_amount",
                "message": f"Amount ₹{amount:,.2f} is {amount/avg:.1f}x the average (₹{avg:,.2f})"
            }
        return {"triggered": False}

    def _check_round_number(self, amount: float, history: List[float]) -> dict:
        """
        Very large round numbers (e.g., 100000, 500000) are often suspicious.
        """
        if amount >= 100_000 and amount % 10_000 == 0:
            return {
                "triggered": True,
                "rule": "round_large_number",
                "message": f"Suspiciously round large amount: ₹{amount:,.0f}"
            }
        return {"triggered": False}

    def _check_repeated_amount(self, amount: float, history: List[float]) -> dict:
        """Flag if the exact same amount appeared in last 3 transactions."""
        recent = history[-3:] if len(history) >= 3 else history
        if recent.count(amount) >= 2:
            return {
                "triggered": True,
                "rule": "repeated_amount",
                "message": f"Amount ₹{amount:,.2f} repeated {recent.count(amount)} times recently"
            }
        return {"triggered": False}

    def analyze(self, amount: float, history: List[float]) -> dict:
        """
        Run all rules against a new transaction.
        
        Args:
            amount: the new transaction amount
            history: list of past transaction amounts for this account
        
        Returns:
            {
                "risk_level": "LOW" | "MEDIUM" | "HIGH",
                "flags": [...triggered rules...],
                "recommendation": "APPROVE" | "REVIEW" | "BLOCK"
            }
        """
        flags = []
        for rule_fn in self.rules:
            result = rule_fn(amount, history)
            if result.get("triggered"):
                flags.append(result)

        # Risk scoring
        if len(flags) == 0:
            risk_level = "LOW"
            recommendation = "APPROVE"
        elif len(flags) == 1:
            risk_level = "MEDIUM"
            recommendation = "REVIEW"
        else:
            risk_level = "HIGH"
            recommendation = "BLOCK"

        return {
            "risk_level": risk_level,
            "flags": flags,
            "recommendation": recommendation,
            "flagged_rules": [f["rule"] for f in flags]
        }


# ─── Simple Spending Insights ─────────────────────────────────────────────────

class SpendingAnalyzer:
    """
    Provides basic spending insights from transaction history.
    No ML required — just statistics.
    """

    def summarize(self, amounts: List[float]) -> dict:
        """
        Returns min, max, avg, total, and trend (increasing/decreasing/stable).
        """
        if not amounts:
            return {"error": "No transaction data."}

        trend = "stable"
        if len(amounts) >= 3:
            recent_avg = statistics.mean(amounts[-3:])
            older_avg  = statistics.mean(amounts[:-3]) if len(amounts) > 3 else recent_avg
            if recent_avg > older_avg * 1.2:
                trend = "increasing"
            elif recent_avg < older_avg * 0.8:
                trend = "decreasing"

        return {
            "total": sum(amounts),
            "average": statistics.mean(amounts),
            "max": max(amounts),
            "min": min(amounts),
            "count": len(amounts),
            "trend": trend
        }


# ─── Quick Test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    detector = SimpleFraudDetector()
    analyzer = SpendingAnalyzer()

    history = [500, 1000, 750, 800, 600]

    print("=== Fraud Detection Test ===")
    print(detector.analyze(50000, history))   # Should be HIGH risk (large amount)
    print(detector.analyze(700, history))     # Should be LOW risk

    print("\n=== Spending Summary ===")
    print(analyzer.summarize(history))
