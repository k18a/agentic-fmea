"""
Risk assessment utilities for agentic AI FMEA.

This module provides functions for calculating Risk Priority Numbers (RPN),
generating risk matrices, and analyzing risk distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .entry import FMEAEntry, FMEAReport


class RiskLevel(str, Enum):
    """Risk level categories based on RPN."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class RiskThresholds:
    """Configurable risk thresholds for RPN categorization."""
    critical: int = 500
    high: int = 200
    medium: int = 100

    def categorize_rpn(self, rpn: int) -> RiskLevel:
        """Categorize an RPN value into risk level."""
        if rpn >= self.critical:
            return RiskLevel.CRITICAL
        elif rpn >= self.high:
            return RiskLevel.HIGH
        elif rpn >= self.medium:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


class RiskCalculator:
    """Calculates and analyzes risk metrics for FMEA entries."""

    def __init__(self, thresholds: Optional[RiskThresholds] = None):
        """
        Initialize the risk calculator.

        Args:
            thresholds: Custom risk thresholds. If None, uses default.
        """
        self.thresholds = thresholds or RiskThresholds()

    def calculate_rpn(self, severity: int, occurrence: int, detection: int) -> int:
        """Calculate Risk Priority Number."""
        return severity * occurrence * detection

    def calculate_risk_score(self, entry: FMEAEntry) -> Dict[str, Any]:
        """Calculate comprehensive risk score for an entry."""
        rpn = entry.rpn
        risk_level = self.thresholds.categorize_rpn(rpn)

        return {
            "rpn": rpn,
            "risk_level": risk_level,
            "severity": entry.severity,
            "occurrence": entry.occurrence,
            "detection": entry.detection,
            "severity_label": self._get_severity_label(entry.severity),
            "occurrence_label": self._get_occurrence_label(entry.occurrence),
            "detection_label": self._get_detection_label(entry.detection)
        }

    def _get_severity_label(self, severity: int) -> str:
        """Get descriptive label for severity score."""
        labels = {
            1: "Negligible", 2: "Minor", 3: "Moderate", 4: "Significant",
            5: "Major", 6: "Severe", 7: "Critical", 8: "Very Critical",
            9: "Catastrophic", 10: "Extreme"
        }
        return labels.get(severity, "Unknown")

    def _get_occurrence_label(self, occurrence: int) -> str:
        """Get descriptive label for occurrence score."""
        labels = {
            1: "Remote", 2: "Very Low", 3: "Low", 4: "Moderately Low",
            5: "Moderate", 6: "Moderately High", 7: "High", 8: "Very High",
            9: "Extremely High", 10: "Certain"
        }
        return labels.get(occurrence, "Unknown")

    def _get_detection_label(self, detection: int) -> str:
        """Get descriptive label for detection score."""
        labels = {
            1: "Very High (Easily Detected)", 2: "High", 3: "Moderately High",
            4: "Moderate", 5: "Low", 6: "Moderately Low", 7: "Low",
            8: "Very Low", 9: "Extremely Low", 10: "Cannot Detect"
        }
        return labels.get(detection, "Unknown")

    def analyze_report_risk(self, report: FMEAReport) -> Dict[str, Any]:
        """Analyze risk distribution across an entire FMEA report."""
        if not report.entries:
            return {"error": "No entries to analyze"}

        rpns = [entry.rpn for entry in report.entries]
        risk_levels = [self.thresholds.categorize_rpn(rpn) for rpn in rpns]

        # Basic statistics
        stats = {
            "total_entries": len(report.entries),
            "mean_rpn": np.mean(rpns),
            "median_rpn": np.median(rpns),
            "max_rpn": max(rpns),
            "min_rpn": min(rpns),
            "std_rpn": np.std(rpns)
        }

        # Risk level distribution
        risk_distribution = {level.value: 0 for level in RiskLevel}
        for level in risk_levels:
            risk_distribution[level.value] += 1

        # Top risk entries
        top_risks = sorted(
            report.entries, key=lambda x: x.rpn, reverse=True
        )[:10]

        # Risk by subsystem
        subsystem_risk = {}
        for entry in report.entries:
            subsystem = entry.subsystem.value
            if subsystem not in subsystem_risk:
                subsystem_risk[subsystem] = {
                    "count": 0, "total_rpn": 0, "max_rpn": 0
                }

            subsystem_risk[subsystem]["count"] += 1
            subsystem_risk[subsystem]["total_rpn"] += entry.rpn
            subsystem_risk[subsystem]["max_rpn"] = max(
                subsystem_risk[subsystem]["max_rpn"], entry.rpn
            )

        # Calculate average RPN per subsystem
        for subsystem in subsystem_risk:
            subsystem_risk[subsystem]["avg_rpn"] = (
                subsystem_risk[subsystem]["total_rpn"]
                / subsystem_risk[subsystem]["count"]
            )

        return {
            "statistics": stats,
            "risk_distribution": risk_distribution,
            "top_risks": [
                {"id": entry.id, "rpn": entry.rpn, "taxonomy_id": entry.taxonomy_id}
                for entry in top_risks
            ],
            "subsystem_risk": subsystem_risk
        }

    def generate_risk_matrix(
        self, entries: List[FMEAEntry],
        x_axis: str = "occurrence",
        y_axis: str = "severity"
    ) -> np.ndarray:
        """
        Generate a risk matrix visualization data.

        Args:
            entries: List of FMEA entries
            x_axis: Which dimension to use for x-axis (occurrence, severity, detection)
            y_axis: Which dimension to use for y-axis (occurrence, severity, detection)

        Returns:
            2D numpy array representing the risk matrix
        """
        if not entries:
            return np.zeros((10, 10))

        matrix = np.zeros((10, 10))

        for entry in entries:
            x_val = getattr(entry, x_axis) - 1  # Convert to 0-based index
            y_val = getattr(entry, y_axis) - 1  # Convert to 0-based index

            # Add RPN value to the matrix cell
            matrix[y_val, x_val] += entry.rpn

        return matrix

    def plot_risk_matrix(
        self, entries: List[FMEAEntry],
        x_axis: str = "occurrence",
        y_axis: str = "severity",
        title: str = "Risk Matrix"
    ) -> plt.Figure:
        """
        Plot a risk matrix visualization.

        Args:
            entries: List of FMEA entries
            x_axis: Which dimension to use for x-axis
            y_axis: Which dimension to use for y-axis
            title: Title for the plot

        Returns:
            Matplotlib figure object
        """
        matrix = self.generate_risk_matrix(entries, x_axis, y_axis)

        fig, ax = plt.subplots(figsize=(10, 8))

        # Create heatmap
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')

        # Set labels
        ax.set_xlabel(x_axis.capitalize())
        ax.set_ylabel(y_axis.capitalize())
        ax.set_title(title)

        # Set tick labels
        ax.set_xticks(range(10))
        ax.set_yticks(range(10))
        ax.set_xticklabels(range(1, 11))
        ax.set_yticklabels(range(1, 11))

        # Add colorbar
        plt.colorbar(im, ax=ax, label='Total RPN')

        # Add text annotations
        for i in range(10):
            for j in range(10):
                if matrix[i, j] > 0:
                    ax.text(j, i, f'{int(matrix[i, j])}',
                            ha="center", va="center", color="black")

        plt.tight_layout()
        return fig

    def plot_risk_distribution(self, report: FMEAReport) -> plt.Figure:
        """Plot risk level distribution for a report."""
        analysis = self.analyze_report_risk(report)
        risk_dist = analysis["risk_distribution"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Bar chart of risk levels
        levels = list(risk_dist.keys())
        counts = list(risk_dist.values())
        colors = ['red', 'orange', 'yellow', 'green']

        ax1.bar(levels, counts, color=colors)
        ax1.set_title('Risk Level Distribution')
        ax1.set_ylabel('Number of Entries')
        ax1.set_xlabel('Risk Level')

        # Add count labels on bars
        for i, count in enumerate(counts):
            if count > 0:
                ax1.text(i, count + 0.1, str(count), ha='center', va='bottom')

        # RPN histogram
        rpns = [entry.rpn for entry in report.entries]
        ax2.hist(rpns, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
        ax2.set_title('RPN Distribution')
        ax2.set_xlabel('Risk Priority Number (RPN)')
        ax2.set_ylabel('Frequency')

        # Add threshold lines
        ax2.axvline(x=self.thresholds.critical, color='red', linestyle='--',
                    label=f'Critical ({self.thresholds.critical})')
        ax2.axvline(x=self.thresholds.high, color='orange', linestyle='--',
                    label=f'High ({self.thresholds.high})')
        ax2.axvline(x=self.thresholds.medium, color='yellow', linestyle='--',
                    label=f'Medium ({self.thresholds.medium})')
        ax2.legend()

        plt.tight_layout()
        return fig

    def recommend_actions(self, entry: FMEAEntry) -> List[str]:
        """Recommend actions based on risk level and characteristics."""
        recommendations = []

        risk_score = self.calculate_risk_score(entry)
        risk_level = risk_score["risk_level"]

        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediate action required - halt system deployment until resolved",
                "Implement emergency monitoring and alerting",
                "Establish incident response procedures",
                "Consider system redesign to eliminate failure mode"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "High priority - implement mitigation before deployment",
                "Establish monitoring and detection mechanisms",
                "Develop contingency plans",
                "Regular risk assessment reviews"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Medium priority - address in next development cycle",
                "Implement preventive measures",
                "Monitor for trends",
                "Document lessons learned"
            ])
        else:  # LOW
            recommendations.extend([
                "Low priority - address as resources permit",
                "Maintain awareness of potential issues",
                "Include in routine monitoring"
            ])

        # Add specific recommendations based on failure mode characteristics
        if entry.detection >= 7:  # Hard to detect
            recommendations.append("Implement automated detection mechanisms")
            recommendations.append("Establish regular audit procedures")

        if entry.severity >= 8:  # High severity
            recommendations.append("Implement fail-safe mechanisms")
            recommendations.append("Add redundancy to critical paths")

        if entry.occurrence >= 7:  # High occurrence
            recommendations.append("Address root causes in system design")
            recommendations.append("Implement preventive controls")

        return recommendations
