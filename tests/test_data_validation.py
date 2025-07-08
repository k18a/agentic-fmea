"""
Unit tests for data validation and edge cases.

Tests input validation, error handling, and boundary conditions
for FMEA entries and reports.
"""

import pytest
from datetime import datetime

from agentic_fmea import (
    FMEAEntry, FMEAReport, SystemType, Subsystem, DetectionMethod
)


class TestFMEAEntryValidation:
    """Test validation rules for FMEA entries."""
    
    def test_valid_entry_creation(self):
        """Test that valid entries are created successfully."""
        entry = FMEAEntry(
            id="valid_test",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Valid cause",
            effect="Valid effect",
            severity=5,
            occurrence=5,
            detection=5,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=["Valid mitigation"],
            agent_capabilities=["autonomy"],
            potential_effects=["Valid effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test User"
        )
        
        assert entry.id == "valid_test"
        assert entry.rpn == 125  # 5 × 5 × 5
        assert entry.risk_level == "Medium"
    
    def test_severity_range_validation(self):
        """Test that severity must be between 1 and 10."""
        # Test invalid severity values
        for invalid_severity in [0, 11, -1, 15]:
            with pytest.raises(ValueError, match="severity must be between 1 and 10"):
                self._create_test_entry(severity=invalid_severity)
        
        # Test valid boundary values
        for valid_severity in [1, 10]:
            entry = self._create_test_entry(severity=valid_severity)
            assert entry.severity == valid_severity
    
    def test_occurrence_range_validation(self):
        """Test that occurrence must be between 1 and 10."""
        # Test invalid occurrence values
        for invalid_occurrence in [0, 11, -5, 20]:
            with pytest.raises(ValueError, match="occurrence must be between 1 and 10"):
                self._create_test_entry(occurrence=invalid_occurrence)
        
        # Test valid boundary values
        for valid_occurrence in [1, 10]:
            entry = self._create_test_entry(occurrence=valid_occurrence)
            assert entry.occurrence == valid_occurrence
    
    def test_detection_range_validation(self):
        """Test that detection must be between 1 and 10."""
        # Test invalid detection values
        for invalid_detection in [0, 11, -3, 100]:
            with pytest.raises(ValueError, match="detection must be between 1 and 10"):
                self._create_test_entry(detection=invalid_detection)
        
        # Test valid boundary values
        for valid_detection in [1, 10]:
            entry = self._create_test_entry(detection=valid_detection)
            assert entry.detection == valid_detection
    
    def test_empty_mitigation_validation(self):
        """Test that mitigation list cannot be empty."""
        with pytest.raises(ValueError, match="At least one mitigation strategy must be provided"):
            self._create_test_entry(mitigation=[])
    
    def test_all_combinations_boundary_values(self):
        """Test all combinations of boundary values work correctly."""
        boundary_values = [1, 10]
        
        for severity in boundary_values:
            for occurrence in boundary_values:
                for detection in boundary_values:
                    entry = self._create_test_entry(
                        severity=severity,
                        occurrence=occurrence,
                        detection=detection
                    )
                    expected_rpn = severity * occurrence * detection
                    assert entry.rpn == expected_rpn
    
    def _create_test_entry(self, severity=5, occurrence=5, detection=5, mitigation=None):
        """Helper method to create test entries with specified parameters."""
        if mitigation is None:
            mitigation = ["Test mitigation"]
        
        return FMEAEntry(
            id="test_validation",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Test cause",
            effect="Test effect",
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=mitigation,
            agent_capabilities=["autonomy"],
            potential_effects=["Test effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )


class TestFMEAReportValidation:
    """Test validation for FMEA reports."""
    
    def test_valid_report_creation(self):
        """Test that valid reports are created successfully."""
        entry = self._create_test_entry("test_1")
        
        report = FMEAReport(
            title="Valid Test Report",
            system_description="Test system description",
            entries=[entry],
            created_date=datetime.now(),
            created_by="Test User"
        )
        
        assert report.title == "Valid Test Report"
        assert len(report.entries) == 1
        assert report.version == "1.0"  # Default version
    
    def test_empty_report(self):
        """Test that reports with no entries are handled correctly."""
        report = FMEAReport(
            title="Empty Report",
            system_description="Empty system",
            entries=[],
            created_date=datetime.now(),
            created_by="Test User"
        )
        
        assert len(report.entries) == 0
        assert report.risk_summary == {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        assert len(report.high_risk_entries) == 0
        assert len(report.entries_by_risk) == 0
    
    def test_report_risk_summary(self):
        """Test that risk summary is calculated correctly."""
        entries = [
            self._create_test_entry("low", 2, 2, 2),      # RPN = 8 (Low)
            self._create_test_entry("medium", 5, 5, 4),   # RPN = 100 (Medium)
            self._create_test_entry("high", 8, 5, 5),     # RPN = 200 (High)
            self._create_test_entry("critical", 10, 10, 5) # RPN = 500 (Critical)
        ]
        
        report = FMEAReport(
            title="Risk Summary Test",
            system_description="Test system",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        expected_summary = {"Critical": 1, "High": 1, "Medium": 1, "Low": 1}
        assert report.risk_summary == expected_summary
    
    def test_high_risk_entries_filtering(self):
        """Test that high risk entries are filtered correctly."""
        entries = [
            self._create_test_entry("low", 2, 2, 2),      # RPN = 8 (Low)
            self._create_test_entry("medium", 5, 5, 4),   # RPN = 100 (Medium)
            self._create_test_entry("high", 8, 5, 5),     # RPN = 200 (High)
            self._create_test_entry("critical", 10, 10, 5) # RPN = 500 (Critical)
        ]
        
        report = FMEAReport(
            title="High Risk Test",
            system_description="Test system",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        high_risk = report.high_risk_entries
        assert len(high_risk) == 2  # High and Critical
        assert all(entry.risk_level in ["High", "Critical"] for entry in high_risk)
    
    def test_entries_by_risk_sorting(self):
        """Test that entries are sorted by RPN correctly."""
        entries = [
            self._create_test_entry("medium", 5, 5, 4),   # RPN = 100
            self._create_test_entry("critical", 10, 10, 5), # RPN = 500
            self._create_test_entry("low", 2, 2, 2),      # RPN = 8
            self._create_test_entry("high", 8, 5, 5)      # RPN = 200
        ]
        
        report = FMEAReport(
            title="Sorting Test",
            system_description="Test system",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        sorted_entries = report.entries_by_risk
        rpns = [entry.rpn for entry in sorted_entries]
        assert rpns == [500, 200, 100, 8]  # Descending order
    
    def test_get_entries_by_subsystem(self):
        """Test filtering entries by subsystem."""
        entries = [
            self._create_test_entry("memory_1", subsystem=Subsystem.MEMORY),
            self._create_test_entry("memory_2", subsystem=Subsystem.MEMORY),
            self._create_test_entry("planning_1", subsystem=Subsystem.PLANNING),
            self._create_test_entry("tooling_1", subsystem=Subsystem.TOOLING)
        ]
        
        report = FMEAReport(
            title="Subsystem Test",
            system_description="Test system",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        memory_entries = report.get_entries_by_subsystem(Subsystem.MEMORY)
        assert len(memory_entries) == 2
        assert all(entry.subsystem == Subsystem.MEMORY for entry in memory_entries)
        
        planning_entries = report.get_entries_by_subsystem(Subsystem.PLANNING)
        assert len(planning_entries) == 1
        assert planning_entries[0].subsystem == Subsystem.PLANNING
    
    def test_get_entries_by_taxonomy(self):
        """Test filtering entries by taxonomy ID."""
        entries = [
            self._create_test_entry("mem_1", taxonomy_id="memory_poisoning"),
            self._create_test_entry("mem_2", taxonomy_id="memory_poisoning"),
            self._create_test_entry("agent_1", taxonomy_id="agent_compromise"),
        ]
        
        report = FMEAReport(
            title="Taxonomy Test",
            system_description="Test system",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        memory_entries = report.get_entries_by_taxonomy("memory_poisoning")
        assert len(memory_entries) == 2
        assert all(entry.taxonomy_id == "memory_poisoning" for entry in memory_entries)
        
        agent_entries = report.get_entries_by_taxonomy("agent_compromise")
        assert len(agent_entries) == 1
        assert agent_entries[0].taxonomy_id == "agent_compromise"
    
    def _create_test_entry(self, entry_id, severity=5, occurrence=5, detection=5,
                          subsystem=Subsystem.MEMORY, taxonomy_id="memory_poisoning"):
        """Helper to create test entries."""
        return FMEAEntry(
            id=entry_id,
            taxonomy_id=taxonomy_id,
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


class TestEnumValidation:
    """Test that enum values are properly validated."""
    
    def test_system_type_enum(self):
        """Test that SystemType enum values work correctly."""
        valid_types = [
            SystemType.SINGLE_AGENT,
            SystemType.MULTI_AGENT_HIERARCHICAL,
            SystemType.MULTI_AGENT_COLLABORATIVE,
            SystemType.MULTI_AGENT_DISTRIBUTED,
            SystemType.USER_DRIVEN,
            SystemType.EVENT_DRIVEN,
            SystemType.DECLARATIVE,
            SystemType.EVALUATIVE
        ]
        
        for system_type in valid_types:
            entry = self._create_test_entry(system_type=system_type)
            assert entry.system_type == system_type
    
    def test_subsystem_enum(self):
        """Test that Subsystem enum values work correctly."""
        valid_subsystems = [
            Subsystem.PLANNING,
            Subsystem.MEMORY,
            Subsystem.TOOLING,
            Subsystem.COMMUNICATION,
            Subsystem.ENVIRONMENT_OBSERVATION,
            Subsystem.ENVIRONMENT_INTERACTION,
            Subsystem.KNOWLEDGE_BASE,
            Subsystem.COORDINATION,
            Subsystem.IDENTITY,
            Subsystem.CONTROL_FLOW
        ]
        
        for subsystem in valid_subsystems:
            entry = self._create_test_entry(subsystem=subsystem)
            assert entry.subsystem == subsystem
    
    def test_detection_method_enum(self):
        """Test that DetectionMethod enum values work correctly."""
        valid_methods = [
            DetectionMethod.STATIC_ANALYSIS,
            DetectionMethod.RED_TEAMING,
            DetectionMethod.LIVE_TELEMETRY,
            DetectionMethod.HUMAN_OVERSIGHT,
            DetectionMethod.AUTOMATED_MONITORING,
            DetectionMethod.TESTING,
            DetectionMethod.CODE_REVIEW,
            DetectionMethod.AUDIT_TRAIL
        ]
        
        for method in valid_methods:
            entry = self._create_test_entry(detection_method=method)
            assert entry.detection_method == method
    
    def _create_test_entry(self, system_type=SystemType.SINGLE_AGENT,
                          subsystem=Subsystem.MEMORY,
                          detection_method=DetectionMethod.LIVE_TELEMETRY):
        """Helper to create test entries with specified enum values."""
        return FMEAEntry(
            id="enum_test",
            taxonomy_id="memory_poisoning",
            system_type=system_type,
            subsystem=subsystem,
            cause="Test cause",
            effect="Test effect",
            severity=5,
            occurrence=5,
            detection=5,
            detection_method=detection_method,
            mitigation=["Test mitigation"],
            agent_capabilities=["autonomy"],
            potential_effects=["Test effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""
    
    def test_extreme_rpn_values(self):
        """Test that extreme RPN values are handled correctly."""
        # Minimum possible RPN
        min_entry = self._create_test_entry(1, 1, 1)  # RPN = 1
        assert min_entry.rpn == 1
        assert min_entry.risk_level == "Low"
        
        # Maximum possible RPN
        max_entry = self._create_test_entry(10, 10, 10)  # RPN = 1000
        assert max_entry.rpn == 1000
        assert max_entry.risk_level == "Critical"
    
    def test_large_mitigation_list(self):
        """Test that large mitigation lists are handled correctly."""
        large_mitigation_list = [f"Mitigation {i}" for i in range(100)]
        
        entry = self._create_test_entry(mitigation=large_mitigation_list)
        assert len(entry.mitigation) == 100
        assert entry.mitigation[0] == "Mitigation 0"
        assert entry.mitigation[99] == "Mitigation 99"
    
    def test_unicode_in_strings(self):
        """Test that Unicode characters in strings are handled correctly."""
        entry = FMEAEntry(
            id="unicode_test_🤖",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Cause with émojis 🔥 and spëcial characters",
            effect="Effect with 中文 characters",
            severity=5,
            occurrence=5,
            detection=5,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=["Mitigation with Ñoñó characters"],
            agent_capabilities=["autonomy"],
            potential_effects=["Effect with 🚨 emoji"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test User with àccénts"
        )
        
        assert "🤖" in entry.id
        assert "émojis" in entry.cause
        assert "中文" in entry.effect
        assert "Ñoñó" in entry.mitigation[0]
        assert "🚨" in entry.potential_effects[0]
        assert "àccénts" in entry.created_by
    
    def _create_test_entry(self, severity=5, occurrence=5, detection=5, mitigation=None):
        """Helper to create test entries."""
        if mitigation is None:
            mitigation = ["Test mitigation"]
        
        return FMEAEntry(
            id="edge_test",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Test cause",
            effect="Test effect",
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=mitigation,
            agent_capabilities=["autonomy"],
            potential_effects=["Test effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )