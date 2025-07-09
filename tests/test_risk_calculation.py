"""
Unit tests for risk calculation functionality.

Tests the core FMEA risk assessment logic including RPN calculation,
risk level categorization, and risk analysis.
"""

import pytest
from datetime import datetime

from agentic_fmea import (
    FMEAEntry, FMEAReport, RiskCalculator, RiskThresholds,
    SystemType, Subsystem, DetectionMethod
)


class TestRiskCalculation:
    """Test RPN calculation and risk categorization."""
    
    def test_rpn_calculation(self):
        """Test that RPN is calculated correctly as Severity × Occurrence × Detection."""
        entry = FMEAEntry(
            id="test_rpn",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Test cause",
            effect="Test effect",
            severity=8,
            occurrence=6,
            detection=7,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=["Test mitigation"],
            agent_capabilities=["autonomy"],
            potential_effects=["Agent misalignment"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )
        
        assert entry.rpn == 336  # 8 × 6 × 7
    
    def test_risk_level_categorization(self):
        """Test that RPN values map to correct risk levels."""
        calculator = RiskCalculator()
        
        # Test default thresholds: Critical≥500, High≥200, Medium≥100, Low<100
        test_cases = [
            (1, 1, 1, "Low"),      # RPN = 1
            (5, 5, 3, "Low"),      # RPN = 75
            (5, 5, 4, "Medium"),   # RPN = 100
            (8, 5, 5, "High"),     # RPN = 200
            (10, 10, 5, "Critical"), # RPN = 500
            (10, 10, 10, "Critical") # RPN = 1000
        ]
        
        for severity, occurrence, detection, expected_level in test_cases:
            entry = self._create_test_entry(severity, occurrence, detection)
            actual_level = calculator.thresholds.categorize_rpn(entry.rpn).value
            assert actual_level == expected_level, (
                f"RPN {entry.rpn} should be {expected_level}, got {actual_level}"
            )
    
    def test_custom_risk_thresholds(self):
        """Test that custom risk thresholds work correctly."""
        custom_thresholds = RiskThresholds(critical=400, high=150, medium=75)
        calculator = RiskCalculator(thresholds=custom_thresholds)
        
        test_cases = [
            (50, "Low"),
            (75, "Medium"),
            (150, "High"),
            (400, "Critical")
        ]
        
        for rpn, expected_level in test_cases:
            actual_level = custom_thresholds.categorize_rpn(rpn)
            assert actual_level.value == expected_level
    
    def test_risk_score_calculation(self):
        """Test comprehensive risk score calculation."""
        calculator = RiskCalculator()
        entry = self._create_test_entry(8, 6, 7)  # RPN = 336
        
        risk_score = calculator.calculate_risk_score(entry)
        
        assert risk_score["rpn"] == 336
        assert risk_score["risk_level"].value == "High"
        assert risk_score["severity"] == 8
        assert risk_score["occurrence"] == 6
        assert risk_score["detection"] == 7
        assert risk_score["severity_label"] == "Very Critical"
        assert risk_score["occurrence_label"] == "Moderately High"
        assert risk_score["detection_label"] == "Low"
    
    def test_boundary_values(self):
        """Test boundary values for severity, occurrence, and detection."""
        # Test minimum values
        entry_min = self._create_test_entry(1, 1, 1)
        assert entry_min.rpn == 1
        calculator = RiskCalculator()
        assert calculator.thresholds.categorize_rpn(entry_min.rpn).value == "Low"
        
        # Test maximum values
        entry_max = self._create_test_entry(10, 10, 10)
        assert entry_max.rpn == 1000
        assert calculator.thresholds.categorize_rpn(entry_max.rpn).value == "Critical"
    
    def _create_test_entry(self, severity, occurrence, detection):
        """Helper method to create test FMEA entries."""
        return FMEAEntry(
            id=f"test_{severity}_{occurrence}_{detection}",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Test cause",
            effect="Test effect",
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=["Test mitigation"],
            agent_capabilities=["autonomy"],
            potential_effects=["Test effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )


class TestReportRiskAnalysis:
    """Test risk analysis across entire FMEA reports."""
    
    def test_report_risk_analysis(self):
        """Test risk analysis statistics for a complete report."""
        entries = [
            self._create_test_entry("low_risk", 2, 2, 2),      # RPN = 8
            self._create_test_entry("medium_risk", 5, 5, 4),   # RPN = 100
            self._create_test_entry("high_risk", 8, 5, 5),     # RPN = 200
            self._create_test_entry("critical_risk", 10, 10, 5) # RPN = 500
        ]
        
        report = FMEAReport(
            title="Test Report",
            system_description="Test System",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(report)
        
        # Check statistics
        stats = analysis["statistics"]
        assert stats["total_entries"] == 4
        assert stats["mean_rpn"] == 202.0  # (8 + 100 + 200 + 500) / 4
        assert stats["max_rpn"] == 500
        assert stats["min_rpn"] == 8
        
        # Check risk distribution
        risk_dist = analysis["risk_distribution"]
        assert risk_dist["Low"] == 1
        assert risk_dist["Medium"] == 1
        assert risk_dist["High"] == 1
        assert risk_dist["Critical"] == 1
        
        # Check top risks are sorted correctly
        top_risks = analysis["top_risks"]
        assert len(top_risks) == 4
        assert top_risks[0]["rpn"] == 500  # Highest first
        assert top_risks[3]["rpn"] == 8    # Lowest last
    
    def test_empty_report_analysis(self):
        """Test that empty reports are handled gracefully."""
        report = FMEAReport(
            title="Empty Report",
            system_description="Empty System",
            entries=[],
            created_date=datetime.now(),
            created_by="Test"
        )
        
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(report)
        
        assert "error" in analysis
        assert analysis["error"] == "No entries to analyze"
    
    def test_subsystem_risk_analysis(self):
        """Test risk analysis by subsystem."""
        entries = [
            self._create_test_entry("memory_1", 8, 5, 5, Subsystem.MEMORY),     # RPN = 200
            self._create_test_entry("memory_2", 6, 6, 6, Subsystem.MEMORY),     # RPN = 216
            self._create_test_entry("planning_1", 5, 5, 4, Subsystem.PLANNING) # RPN = 100
        ]
        
        report = FMEAReport(
            title="Subsystem Test",
            system_description="Test System",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(report)
        
        subsystem_risk = analysis["subsystem_risk"]
        
        # Memory subsystem: 2 entries, total RPN = 416, max = 216, avg = 208
        assert subsystem_risk["memory"]["count"] == 2
        assert subsystem_risk["memory"]["total_rpn"] == 416
        assert subsystem_risk["memory"]["max_rpn"] == 216
        assert subsystem_risk["memory"]["avg_rpn"] == 208.0
        
        # Planning subsystem: 1 entry, total RPN = 100, max = 100, avg = 100
        assert subsystem_risk["planning"]["count"] == 1
        assert subsystem_risk["planning"]["total_rpn"] == 100
        assert subsystem_risk["planning"]["max_rpn"] == 100
        assert subsystem_risk["planning"]["avg_rpn"] == 100.0
    
    def _create_test_entry(self, entry_id, severity, occurrence, detection, 
                          subsystem=Subsystem.MEMORY):
        """Helper to create test entries with specified subsystem."""
        return FMEAEntry(
            id=entry_id,
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=subsystem,
            cause="Test cause",
            effect="Test effect",
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=["Test mitigation"],
            agent_capabilities=["autonomy"],
            potential_effects=["Test effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )


class TestRiskRecommendations:
    """Test risk-based recommendation generation."""
    
    def test_critical_risk_recommendations(self):
        """Test that critical risk entries get appropriate recommendations."""
        calculator = RiskCalculator()
        entry = self._create_test_entry(10, 10, 5)  # RPN = 500 (Critical)
        
        recommendations = calculator.recommend_actions(entry)
        
        # Should include critical-level recommendations
        rec_text = " ".join(recommendations).lower()
        assert "immediate action required" in rec_text
        assert "halt system deployment" in rec_text
        assert "emergency monitoring" in rec_text
    
    def test_low_risk_recommendations(self):
        """Test that low risk entries get basic recommendations."""
        calculator = RiskCalculator()
        entry = self._create_test_entry(2, 2, 2)  # RPN = 8 (Low)
        
        recommendations = calculator.recommend_actions(entry)
        
        # Should include low-priority recommendations
        rec_text = " ".join(recommendations).lower()
        assert "low priority" in rec_text
        assert "routine monitoring" in rec_text
    
    def test_high_detection_score_recommendations(self):
        """Test recommendations for hard-to-detect failure modes."""
        calculator = RiskCalculator()
        entry = self._create_test_entry(5, 5, 8)  # Detection = 8 (hard to detect)
        
        recommendations = calculator.recommend_actions(entry)
        
        rec_text = " ".join(recommendations).lower()
        assert "automated detection" in rec_text
        assert "audit procedures" in rec_text
    
    def _create_test_entry(self, severity, occurrence, detection):
        """Helper to create test entries."""
        return FMEAEntry(
            id=f"rec_test_{severity}_{occurrence}_{detection}",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Test cause",
            effect="Test effect",
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=["Test mitigation"],
            agent_capabilities=["autonomy"],
            potential_effects=["Test effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )