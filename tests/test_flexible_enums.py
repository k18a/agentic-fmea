"""
Unit tests for flexible enum functionality.

Tests the new OTHER enum values and custom fields system that allows
for more flexible handling of real-world edge cases.
"""

import pytest
from datetime import datetime

from agentic_fmea import (
    FMEAEntry, SystemType, Subsystem, DetectionMethod
)


class TestFlexibleEnumBasics:
    """Test basic functionality of flexible enums."""
    
    def test_other_enum_values_exist(self):
        """Test that OTHER enum values are properly defined."""
        # Test SystemType.OTHER
        assert SystemType.OTHER == "other"
        assert SystemType.OTHER in [item.value for item in SystemType]
        
        # Test Subsystem.OTHER
        assert Subsystem.OTHER == "other"
        assert Subsystem.OTHER in [item.value for item in Subsystem]
        
        # Test DetectionMethod.OTHER
        assert DetectionMethod.OTHER == "other"
        assert DetectionMethod.OTHER in [item.value for item in DetectionMethod]
    
    def test_backwards_compatibility(self):
        """Test that existing enum values still work unchanged."""
        # Test existing SystemType values
        entry = self._create_test_entry(
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            detection_method=DetectionMethod.LIVE_TELEMETRY
        )
        
        assert entry.system_type == SystemType.SINGLE_AGENT
        assert entry.subsystem == Subsystem.MEMORY
        assert entry.detection_method == DetectionMethod.LIVE_TELEMETRY
        assert entry.custom_system_type is None
        assert entry.custom_subsystem is None
        assert entry.custom_detection_method is None
    
    def test_custom_system_type_valid(self):
        """Test valid usage of custom system type."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            custom_system_type="Custom ML Pipeline System"
        )
        
        assert entry.system_type == SystemType.OTHER
        assert entry.custom_system_type == "Custom ML Pipeline System"
    
    def test_custom_subsystem_valid(self):
        """Test valid usage of custom subsystem."""
        entry = self._create_test_entry(
            subsystem=Subsystem.OTHER,
            custom_subsystem="Custom Data Processing Module"
        )
        
        assert entry.subsystem == Subsystem.OTHER
        assert entry.custom_subsystem == "Custom Data Processing Module"
    
    def test_custom_detection_method_valid(self):
        """Test valid usage of custom detection method."""
        entry = self._create_test_entry(
            detection_method=DetectionMethod.OTHER,
            custom_detection_method="Custom Anomaly Detection"
        )
        
        assert entry.detection_method == DetectionMethod.OTHER
        assert entry.custom_detection_method == "Custom Anomaly Detection"
    
    def test_all_custom_fields_together(self):
        """Test using all custom fields together."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            subsystem=Subsystem.OTHER,
            detection_method=DetectionMethod.OTHER,
            custom_system_type="Custom Hybrid System",
            custom_subsystem="Custom Processing Unit",
            custom_detection_method="Custom Monitoring System"
        )
        
        assert entry.system_type == SystemType.OTHER
        assert entry.subsystem == Subsystem.OTHER
        assert entry.detection_method == DetectionMethod.OTHER
        assert entry.custom_system_type == "Custom Hybrid System"
        assert entry.custom_subsystem == "Custom Processing Unit"
        assert entry.custom_detection_method == "Custom Monitoring System"
    
    def _create_test_entry(self, id="test_entry", system_type=SystemType.SINGLE_AGENT,
                          subsystem=Subsystem.MEMORY, detection_method=DetectionMethod.LIVE_TELEMETRY,
                          custom_system_type=None, custom_subsystem=None, custom_detection_method=None,
                          severity=5, occurrence=5, detection=5,
                          cause="Test cause", effect="Test effect"):
        """Helper method to create test entries with flexible parameters."""
        return FMEAEntry(
            id=id,
            taxonomy_id="test_taxonomy",
            system_type=system_type,
            subsystem=subsystem,
            cause=cause,
            effect=effect,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=detection_method,
            mitigation=["Test mitigation"],
            agent_capabilities=["test_capability"],
            potential_effects=["test_effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test User",
            custom_system_type=custom_system_type,
            custom_subsystem=custom_subsystem,
            custom_detection_method=custom_detection_method
        )


class TestFlexibleEnumValidation:
    """Test validation rules for flexible enums."""
    
    def test_missing_custom_system_type(self):
        """Test that missing custom_system_type raises error when OTHER is used."""
        with pytest.raises(ValueError, match="custom_system_type must be provided when system_type is OTHER"):
            self._create_test_entry(
                system_type=SystemType.OTHER,
                custom_system_type=None
            )
    
    def test_empty_custom_system_type(self):
        """Test that empty custom_system_type raises error."""
        with pytest.raises(ValueError, match="custom_system_type cannot be empty or whitespace"):
            self._create_test_entry(
                system_type=SystemType.OTHER,
                custom_system_type=""
            )
        
        with pytest.raises(ValueError, match="custom_system_type cannot be empty or whitespace"):
            self._create_test_entry(
                system_type=SystemType.OTHER,
                custom_system_type="   "
            )
    
    def test_missing_custom_subsystem(self):
        """Test that missing custom_subsystem raises error when OTHER is used."""
        with pytest.raises(ValueError, match="custom_subsystem must be provided when subsystem is OTHER"):
            self._create_test_entry(
                subsystem=Subsystem.OTHER,
                custom_subsystem=None
            )
    
    def test_empty_custom_subsystem(self):
        """Test that empty custom_subsystem raises error."""
        with pytest.raises(ValueError, match="custom_subsystem cannot be empty or whitespace"):
            self._create_test_entry(
                subsystem=Subsystem.OTHER,
                custom_subsystem=""
            )
        
        with pytest.raises(ValueError, match="custom_subsystem cannot be empty or whitespace"):
            self._create_test_entry(
                subsystem=Subsystem.OTHER,
                custom_subsystem="   "
            )
    
    def test_missing_custom_detection_method(self):
        """Test that missing custom_detection_method raises error when OTHER is used."""
        with pytest.raises(ValueError, match="custom_detection_method must be provided when detection_method is OTHER"):
            self._create_test_entry(
                detection_method=DetectionMethod.OTHER,
                custom_detection_method=None
            )
    
    def test_empty_custom_detection_method(self):
        """Test that empty custom_detection_method raises error."""
        with pytest.raises(ValueError, match="custom_detection_method cannot be empty or whitespace"):
            self._create_test_entry(
                detection_method=DetectionMethod.OTHER,
                custom_detection_method=""
            )
        
        with pytest.raises(ValueError, match="custom_detection_method cannot be empty or whitespace"):
            self._create_test_entry(
                detection_method=DetectionMethod.OTHER,
                custom_detection_method="   "
            )
    
    def test_custom_field_without_other_enum(self):
        """Test that custom fields cannot be used without OTHER enum."""
        # Test custom_system_type without OTHER
        with pytest.raises(ValueError, match="custom_system_type should only be provided when system_type is OTHER"):
            self._create_test_entry(
                system_type=SystemType.SINGLE_AGENT,
                custom_system_type="Custom System"
            )
        
        # Test custom_subsystem without OTHER
        with pytest.raises(ValueError, match="custom_subsystem should only be provided when subsystem is OTHER"):
            self._create_test_entry(
                subsystem=Subsystem.MEMORY,
                custom_subsystem="Custom Subsystem"
            )
        
        # Test custom_detection_method without OTHER
        with pytest.raises(ValueError, match="custom_detection_method should only be provided when detection_method is OTHER"):
            self._create_test_entry(
                detection_method=DetectionMethod.LIVE_TELEMETRY,
                custom_detection_method="Custom Detection"
            )
    
    def test_partial_other_usage(self):
        """Test that you can use OTHER for some enums but not others."""
        # Only system_type is OTHER
        entry1 = self._create_test_entry(
            system_type=SystemType.OTHER,
            subsystem=Subsystem.MEMORY,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            custom_system_type="Custom System Type"
        )
        
        assert entry1.system_type == SystemType.OTHER
        assert entry1.subsystem == Subsystem.MEMORY
        assert entry1.detection_method == DetectionMethod.LIVE_TELEMETRY
        assert entry1.custom_system_type == "Custom System Type"
        assert entry1.custom_subsystem is None
        assert entry1.custom_detection_method is None
        
        # Only subsystem is OTHER
        entry2 = self._create_test_entry(
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.OTHER,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            custom_subsystem="Custom Subsystem"
        )
        
        assert entry2.system_type == SystemType.SINGLE_AGENT
        assert entry2.subsystem == Subsystem.OTHER
        assert entry2.detection_method == DetectionMethod.LIVE_TELEMETRY
        assert entry2.custom_system_type is None
        assert entry2.custom_subsystem == "Custom Subsystem"
        assert entry2.custom_detection_method is None
    
    def _create_test_entry(self, id="test_entry", system_type=SystemType.SINGLE_AGENT,
                          subsystem=Subsystem.MEMORY, detection_method=DetectionMethod.LIVE_TELEMETRY,
                          custom_system_type=None, custom_subsystem=None, custom_detection_method=None,
                          severity=5, occurrence=5, detection=5,
                          cause="Test cause", effect="Test effect"):
        """Helper method to create test entries with flexible parameters."""
        return FMEAEntry(
            id=id,
            taxonomy_id="test_taxonomy",
            system_type=system_type,
            subsystem=subsystem,
            cause=cause,
            effect=effect,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=detection_method,
            mitigation=["Test mitigation"],
            agent_capabilities=["test_capability"],
            potential_effects=["test_effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test User",
            custom_system_type=custom_system_type,
            custom_subsystem=custom_subsystem,
            custom_detection_method=custom_detection_method
        )


class TestFlexibleEnumRealWorldScenarios:
    """Test real-world scenarios that motivated the flexible enum system."""
    
    def test_custom_ai_architecture(self):
        """Test modeling a custom AI architecture not covered by standard enums."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            subsystem=Subsystem.OTHER,
            detection_method=DetectionMethod.OTHER,
            custom_system_type="Federated Learning Network",
            custom_subsystem="Edge Device Coordinator",
            custom_detection_method="Blockchain-based Consensus Monitoring",
            cause="Malicious model updates from compromised edge devices",
            effect="Degraded global model performance and potential data leakage"
        )
        
        assert entry.system_type == SystemType.OTHER
        assert entry.custom_system_type == "Federated Learning Network"
        assert entry.subsystem == Subsystem.OTHER
        assert entry.custom_subsystem == "Edge Device Coordinator"
        assert entry.detection_method == DetectionMethod.OTHER
        assert entry.custom_detection_method == "Blockchain-based Consensus Monitoring"
        assert "Malicious model updates" in entry.cause
        assert "Degraded global model performance" in entry.effect
    
    def test_domain_specific_system(self):
        """Test modeling a domain-specific system like healthcare AI."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            subsystem=Subsystem.OTHER,
            detection_method=DetectionMethod.OTHER,
            custom_system_type="Clinical Decision Support System",
            custom_subsystem="HIPAA Compliance Module",
            custom_detection_method="Medical Professional Review Process",
            cause="Incorrect patient risk stratification due to biased training data",
            effect="Inappropriate treatment recommendations leading to patient harm"
        )
        
        assert entry.custom_system_type == "Clinical Decision Support System"
        assert entry.custom_subsystem == "HIPAA Compliance Module"
        assert entry.custom_detection_method == "Medical Professional Review Process"
        assert "biased training data" in entry.cause
        assert "patient harm" in entry.effect
    
    def test_legacy_system_integration(self):
        """Test modeling integration with legacy systems."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            subsystem=Subsystem.OTHER,
            custom_system_type="Legacy ERP Integration Agent",
            custom_subsystem="COBOL Interface Layer",
            cause="SQL injection through legacy database interface",
            effect="Unauthorized access to sensitive financial data"
        )
        
        assert entry.custom_system_type == "Legacy ERP Integration Agent"
        assert entry.custom_subsystem == "COBOL Interface Layer"
        assert entry.detection_method == DetectionMethod.LIVE_TELEMETRY  # Standard enum still used
        assert entry.custom_detection_method is None
    
    def test_custom_detection_methods(self):
        """Test various custom detection methods from different domains."""
        detection_methods = [
            "Peer Review by Domain Experts",
            "Regulatory Compliance Auditing",
            "Customer Feedback Analysis",
            "A/B Testing with Control Groups",
            "Third-party Security Assessment",
            "Blockchain Transaction Verification"
        ]
        
        for i, method in enumerate(detection_methods):
            entry = self._create_test_entry(
                id=f"custom_detection_{i}",
                detection_method=DetectionMethod.OTHER,
                custom_detection_method=method
            )
            
            assert entry.detection_method == DetectionMethod.OTHER
            assert entry.custom_detection_method == method
    
    def test_unicode_in_custom_fields(self):
        """Test that custom fields handle Unicode characters correctly."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            subsystem=Subsystem.OTHER,
            detection_method=DetectionMethod.OTHER,
            custom_system_type="Multi-lingual AI Assistant (支持中文)",
            custom_subsystem="Emotion Recognition Module (感情認識)",
            custom_detection_method="Human-in-the-loop Validation (人工审核)"
        )
        
        assert "中文" in entry.custom_system_type
        assert "感情認識" in entry.custom_subsystem
        assert "人工审核" in entry.custom_detection_method
    
    def _create_test_entry(self, id="test_entry", system_type=SystemType.SINGLE_AGENT,
                          subsystem=Subsystem.MEMORY, detection_method=DetectionMethod.LIVE_TELEMETRY,
                          custom_system_type=None, custom_subsystem=None, custom_detection_method=None,
                          severity=5, occurrence=5, detection=5,
                          cause="Test cause", effect="Test effect"):
        """Helper method to create test entries with flexible parameters."""
        return FMEAEntry(
            id=id,
            taxonomy_id="test_taxonomy",
            system_type=system_type,
            subsystem=subsystem,
            cause=cause,
            effect=effect,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=detection_method,
            mitigation=["Test mitigation"],
            agent_capabilities=["test_capability"],
            potential_effects=["test_effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test User",
            custom_system_type=custom_system_type,
            custom_subsystem=custom_subsystem,
            custom_detection_method=custom_detection_method
        )


class TestFlexibleEnumIntegration:
    """Test integration with existing functionality."""
    
    def test_rpn_calculation_with_custom_fields(self):
        """Test that RPN calculation works correctly with custom fields."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            custom_system_type="Custom System",
            severity=7,
            occurrence=8,
            detection=5
        )
        
        assert entry.rpn == 7 * 8 * 5  # 280
    
    def test_risk_categorization_with_custom_fields(self):
        """Test that risk categorization works with custom fields."""
        entry = self._create_test_entry(
            system_type=SystemType.OTHER,
            custom_system_type="High Risk Custom System",
            severity=9,
            occurrence=8,
            detection=7
        )
        
        from agentic_fmea.risk import RiskCalculator
        calculator = RiskCalculator()
        risk_level = calculator.thresholds.categorize_rpn(entry.rpn)
        
        assert entry.rpn == 504  # 9 * 8 * 7
        assert risk_level.value == "Critical"
    
    def test_report_filtering_with_custom_fields(self):
        """Test that report filtering works with custom fields."""
        from agentic_fmea import FMEAReport
        
        entries = [
            self._create_test_entry(
                id="standard_entry",
                system_type=SystemType.SINGLE_AGENT,
                subsystem=Subsystem.MEMORY
            ),
            self._create_test_entry(
                id="custom_entry",
                system_type=SystemType.OTHER,
                subsystem=Subsystem.OTHER,
                custom_system_type="Custom System",
                custom_subsystem="Custom Subsystem"
            )
        ]
        
        report = FMEAReport(
            title="Mixed Entry Types Report",
            system_description="Test report with mixed entry types",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test User"
        )
        
        # Test that filtering still works
        memory_entries = report.get_entries_by_subsystem(Subsystem.MEMORY)
        assert len(memory_entries) == 1
        assert memory_entries[0].id == "standard_entry"
        
        other_entries = report.get_entries_by_subsystem(Subsystem.OTHER)
        assert len(other_entries) == 1
        assert other_entries[0].id == "custom_entry"
        assert other_entries[0].custom_subsystem == "Custom Subsystem"

    def _create_test_entry(self, id="test_entry", system_type=SystemType.SINGLE_AGENT,
                          subsystem=Subsystem.MEMORY, detection_method=DetectionMethod.LIVE_TELEMETRY,
                          custom_system_type=None, custom_subsystem=None, custom_detection_method=None,
                          severity=5, occurrence=5, detection=5,
                          cause="Test cause", effect="Test effect"):
        """Helper method to create test entries with flexible parameters."""
        return FMEAEntry(
            id=id,
            taxonomy_id="test_taxonomy",
            system_type=system_type,
            subsystem=subsystem,
            cause=cause,
            effect=effect,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=detection_method,
            mitigation=["Test mitigation"],
            agent_capabilities=["test_capability"],
            potential_effects=["test_effect"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test User",
            custom_system_type=custom_system_type,
            custom_subsystem=custom_subsystem,
            custom_detection_method=custom_detection_method
        )