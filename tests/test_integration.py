"""
Integration tests for the complete agentic-fmea workflow.

Tests the end-to-end functionality including taxonomy loading,
FMEA entry creation, risk analysis, and report generation.
"""

import pytest
from datetime import datetime
import tempfile
from pathlib import Path

from agentic_fmea import (
    TaxonomyLoader, FMEAEntry, FMEAReport, RiskCalculator, FMEAReportGenerator,
    SystemType, Subsystem, DetectionMethod
)


class TestCompleteWorkflow:
    """Test the complete FMEA workflow from start to finish."""
    
    def test_memory_poisoning_case_study_workflow(self):
        """Test the complete workflow using the memory poisoning case study."""
        # Step 1: Load taxonomy and get failure mode
        loader = TaxonomyLoader()
        memory_poisoning = loader.get_failure_mode("memory_poisoning")
        assert memory_poisoning is not None
        
        # Step 2: Create FMEA entries based on case study
        entries = [
            # Entry 1: Initial memory poisoning injection
            FMEAEntry(
                id="memory_poison_injection",
                taxonomy_id="memory_poisoning",
                system_type=SystemType.SINGLE_AGENT,
                subsystem=Subsystem.MEMORY,
                cause="Malicious email with embedded instructions processed by agent",
                effect="Agent autonomously stores malicious instructions in semantic memory",
                severity=8,  # High severity - can lead to data exfiltration
                occurrence=6,  # Moderate occurrence - depends on email filtering
                detection=7,  # Hard to detect - appears as normal email processing
                detection_method=DetectionMethod.LIVE_TELEMETRY,
                mitigation=[
                    "Input validation and sanitization",
                    "Semantic analysis of memory content",
                    "Contextual integrity checks",
                    "Memory access controls"
                ],
                agent_capabilities=["autonomy", "memory", "environment_observation"],
                potential_effects=["Agent misalignment", "Agent action abuse", "Data exfiltration"],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                created_by="Security Team"
            ),
            
            # Entry 2: Memory retrieval and execution
            FMEAEntry(
                id="memory_poison_execution",
                taxonomy_id="memory_poisoning",
                system_type=SystemType.SINGLE_AGENT,
                subsystem=Subsystem.MEMORY,
                cause="Agent retrieves poisoned memory during email processing",
                effect="Agent executes malicious instructions, forwarding sensitive emails",
                severity=9,  # Very high severity - direct data breach
                occurrence=8,  # High occurrence - happens whenever memory is accessed
                detection=6,  # Moderate detection - unusual forwarding behavior
                detection_method=DetectionMethod.AUTOMATED_MONITORING,
                mitigation=[
                    "Memory provenance tracking",
                    "Authorization checks before actions",
                    "Anomaly detection for unusual email patterns",
                    "Human-in-the-loop for sensitive actions"
                ],
                agent_capabilities=["autonomy", "memory", "environment_interaction"],
                potential_effects=["Agent action abuse", "Data exfiltration", "User trust erosion"],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                created_by="Security Team"
            )
        ]
        
        # Verify RPN calculations match expected values
        assert entries[0].rpn == 336  # 8 × 6 × 7
        assert entries[1].rpn == 432  # 9 × 8 × 6
        
        # Step 3: Create FMEA report
        report = FMEAReport(
            title="Memory Poisoning Attack - Agentic AI Email Assistant",
            system_description="""Agentic AI email assistant with textual memory implemented using RAG.
            The system can autonomously process emails and make decisions about information to memorize.""",
            entries=entries,
            created_date=datetime.now(),
            created_by="Security Team"
        )
        
        # Verify report structure
        assert len(report.entries) == 2
        assert report.risk_summary()["High"] == 2  # Both entries are high risk
        
        # Step 4: Perform risk analysis
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(report)
        
        # Verify analysis results
        assert analysis["statistics"]["total_entries"] == 2
        assert analysis["statistics"]["mean_rpn"] == 384.0  # (336 + 432) / 2
        assert analysis["statistics"]["max_rpn"] == 432
        assert analysis["top_risks"][0]["rpn"] == 432  # Highest risk first
        
        # Step 5: Generate recommendations
        recommendations_1 = calculator.recommend_actions(entries[0])
        recommendations_2 = calculator.recommend_actions(entries[1])
        
        assert len(recommendations_1) > 0
        assert len(recommendations_2) > 0
        
        # Step 6: Generate comprehensive report
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Verify report content
        assert "Memory Poisoning Attack" in markdown_report
        assert "memory_poison_injection" in markdown_report
        assert "memory_poison_execution" in markdown_report
        assert "Risk Priority Number" in markdown_report or "RPN" in markdown_report
        
        # Step 7: Generate CSV export
        csv_content = generator.generate_csv_export(report)
        lines = csv_content.strip().split('\n')
        assert len(lines) == 3  # Header + 2 entries
        assert "memory_poison_injection" in csv_content
        assert "memory_poison_execution" in csv_content
    
    def test_multi_failure_mode_analysis(self):
        """Test analysis across multiple different failure modes."""
        loader = TaxonomyLoader()
        
        # Create entries for different failure modes
        entries = [
            self._create_entry("mem_poison", "memory_poisoning", 8, 6, 7),
            self._create_entry("agent_comp", "agent_compromise", 9, 5, 6),
            self._create_entry("bias_amp", "bias_amplification", 6, 7, 8),
            self._create_entry("halluc", "hallucinations", 7, 6, 5)
        ]
        
        report = FMEAReport(
            title="Multi-Failure Mode Analysis",
            system_description="Comprehensive analysis across multiple failure modes",
            entries=entries,
            created_date=datetime.now(),
            created_by="Security Team"
        )
        
        # Verify each failure mode can be found in taxonomy
        for entry in entries:
            failure_mode = loader.get_failure_mode(entry.taxonomy_id)
            assert failure_mode is not None
        
        # Perform analysis
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(report)
        
        # Should have entries across different risk levels
        assert analysis["statistics"]["total_entries"] == 4
        risk_dist = analysis["risk_distribution"]
        total_distributed = sum(risk_dist.values())
        assert total_distributed == 4
        
        # Generate report and verify it includes all failure modes
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        for entry in entries:
            assert entry.id in markdown_report
    
    def test_report_generation_completeness(self):
        """Test that generated reports include all expected sections."""
        # Create a diverse set of entries
        entries = [
            self._create_entry("critical", "memory_poisoning", 10, 10, 5),  # Critical
            self._create_entry("high", "agent_compromise", 8, 5, 5),       # High
            self._create_entry("medium", "bias_amplification", 5, 5, 4),   # Medium
            self._create_entry("low", "hallucinations", 3, 3, 3)           # Low
        ]
        
        report = FMEAReport(
            title="Complete Report Test",
            system_description="Test system for comprehensive reporting",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test Team"
        )
        
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Check for required sections
        required_sections = [
            "# FMEA Report:",
            "## Executive Summary",
            "## Risk Analysis",
            "### Top Risk Entries",
            "### Risk by Subsystem",
            "## All FMEA Entries",
            "## Detailed Analysis of High-Risk Entries",
            "## Recommendations"
        ]
        
        for section in required_sections:
            assert section in markdown_report, f"Missing section: {section}"
        
        # Check that risk statistics are present
        assert "Total Failure Modes Analyzed:" in markdown_report
        assert "Mean RPN:" in markdown_report
        assert "Risk Distribution" in markdown_report
        
        # Check that all entries appear in the report
        for entry in entries:
            assert entry.id in markdown_report
    
    def test_error_handling_workflow(self):
        """Test that errors are handled gracefully throughout the workflow."""
        # Test with empty report
        empty_report = FMEAReport(
            title="Empty Report",
            system_description="Report with no entries",
            entries=[],
            created_date=datetime.now(),
            created_by="Test"
        )
        
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(empty_report)
        assert "error" in analysis
        
        # Generator should still work with empty report
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(empty_report)
        assert "Empty Report" in markdown_report
        assert len(markdown_report) > 0
        
        # CSV export should work with empty report
        csv_content = generator.generate_csv_export(empty_report)
        lines = csv_content.strip().split('\n')
        assert len(lines) == 1  # Just header
    
    def test_file_operations(self):
        """Test file saving and loading operations."""
        entries = [
            self._create_entry("test_1", "memory_poisoning", 8, 6, 7),
            self._create_entry("test_2", "agent_compromise", 7, 5, 6)
        ]
        
        report = FMEAReport(
            title="File Operations Test",
            system_description="Test report for file operations",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        generator = FMEAReportGenerator()
        
        # Test markdown file saving
        with tempfile.TemporaryDirectory() as temp_dir:
            md_path = Path(temp_dir) / "test_report.md"
            generator.save_markdown_report(report, str(md_path))
            
            assert md_path.exists()
            content = md_path.read_text(encoding='utf-8')
            assert "File Operations Test" in content
            assert "test_1" in content
            assert "test_2" in content
        
        # Test CSV file saving
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test_export.csv"
            generator.save_csv_export(report, str(csv_path))
            
            assert csv_path.exists()
            content = csv_path.read_text(encoding='utf-8')
            assert "test_1" in content
            assert "test_2" in content
            assert "memory_poisoning" in content
    
    def _create_entry(self, entry_id, taxonomy_id, severity, occurrence, detection):
        """Helper to create test entries."""
        return FMEAEntry(
            id=entry_id,
            taxonomy_id=taxonomy_id,
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause=f"Test cause for {entry_id}",
            effect=f"Test effect for {entry_id}",
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            detection_method=DetectionMethod.LIVE_TELEMETRY,
            mitigation=[f"Test mitigation for {entry_id}"],
            agent_capabilities=["autonomy"],
            potential_effects=[f"Test effect for {entry_id}"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )


class TestRealWorldScenarios:
    """Test scenarios that mirror real-world usage patterns."""
    
    def test_security_assessment_scenario(self):
        """Test a realistic security assessment scenario."""
        # Simulate a security team assessing multiple attack vectors
        loader = TaxonomyLoader()
        
        # Get security-focused failure modes
        security_modes = loader.get_failure_modes_by_pillar("security")
        assert len(security_modes) > 0
        
        # Create entries for top security concerns
        security_entries = []
        
        # Memory poisoning (high priority)
        security_entries.append(FMEAEntry(
            id="sec_memory_poison",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.MULTI_AGENT_COLLABORATIVE,
            subsystem=Subsystem.MEMORY,
            cause="Untrusted data sources feeding agent memory",
            effect="Persistent malicious behavior in agent responses",
            severity=9, occurrence=6, detection=7,
            detection_method=DetectionMethod.AUTOMATED_MONITORING,
            mitigation=["Memory sanitization", "Source validation", "Regular memory audits"],
            agent_capabilities=["autonomy", "memory", "collaboration"],
            potential_effects=["Agent misalignment", "Data exfiltration"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Security Team"
        ))
        
        # Agent compromise (critical priority)
        security_entries.append(FMEAEntry(
            id="sec_agent_compromise",
            taxonomy_id="agent_compromise",
            system_type=SystemType.MULTI_AGENT_COLLABORATIVE,
            subsystem=Subsystem.IDENTITY,
            cause="Insufficient agent authentication and authorization",
            effect="Malicious agent infiltrates system and manipulates workflows",
            severity=10, occurrence=4, detection=8,
            detection_method=DetectionMethod.STATIC_ANALYSIS,
            mitigation=["Strong agent identity verification", "Encrypted communications", "Behavioral monitoring"],
            agent_capabilities=["autonomy", "collaboration"],
            potential_effects=["Agent misalignment", "System compromise"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Security Team"
        ))
        
        # Create security assessment report
        security_report = FMEAReport(
            title="Security Risk Assessment - Multi-Agent System",
            system_description="Security analysis of collaborative multi-agent AI system for enterprise deployment",
            entries=security_entries,
            created_date=datetime.now(),
            created_by="Security Team",
            scope="Security-focused FMEA for production deployment readiness"
        )
        
        # Perform risk analysis
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(security_report)
        
        # Verify high-risk findings
        assert analysis["statistics"]["total_entries"] == 2
        high_risk = [entry for entry in security_entries if calculator.thresholds.categorize_rpn(entry.rpn).value in ["High", "Critical"]]
        assert len(high_risk) == 2  # Both should be high risk
        
        # Generate actionable report
        generator = FMEAReportGenerator()
        security_markdown = generator.generate_markdown_report(security_report)
        
        # Verify security-specific content
        assert "Security Risk Assessment" in security_markdown
        assert "Critical" in security_markdown or "High" in security_markdown
        assert "mitigation" in security_markdown.lower()
    
    def test_development_team_scenario(self):
        """Test a scenario where development team uses FMEA for design decisions."""
        # Development team identifying risks during system design
        entries = []
        
        # Different subsystems with varying risk profiles
        subsystem_risks = [
            (Subsystem.PLANNING, "planning_risk", 7, 5, 6),
            (Subsystem.MEMORY, "memory_risk", 8, 6, 7),
            (Subsystem.TOOLING, "tooling_risk", 6, 7, 5),
            (Subsystem.COMMUNICATION, "comm_risk", 5, 8, 6)
        ]
        
        for subsystem, risk_id, severity, occurrence, detection in subsystem_risks:
            entry = FMEAEntry(
                id=risk_id,
                taxonomy_id="memory_poisoning",  # Using same taxonomy for simplicity
                system_type=SystemType.MULTI_AGENT_HIERARCHICAL,
                subsystem=subsystem,
                cause=f"Design weakness in {subsystem.value} subsystem",
                effect=f"Potential failure in {subsystem.value} functionality",
                severity=severity,
                occurrence=occurrence,
                detection=detection,
                detection_method=DetectionMethod.CODE_REVIEW,
                mitigation=[f"Improved {subsystem.value} design", "Additional testing"],
                agent_capabilities=["autonomy"],
                potential_effects=["System degradation"],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                created_by="Development Team"
            )
            entries.append(entry)
        
        dev_report = FMEAReport(
            title="Development Risk Assessment - System Design Phase",
            system_description="Risk analysis during architectural design of hierarchical multi-agent system",
            entries=entries,
            created_date=datetime.now(),
            created_by="Development Team"
        )
        
        # Analyze risks by subsystem
        calculator = RiskCalculator()
        analysis = calculator.analyze_report_risk(dev_report)
        
        # Should have risk data for each subsystem
        subsystem_risk = analysis["subsystem_risk"]
        assert len(subsystem_risk) == 4
        
        # Each subsystem should have exactly one entry
        for subsystem_name in ["planning", "memory", "tooling", "communication"]:
            assert subsystem_name in subsystem_risk
            assert subsystem_risk[subsystem_name]["count"] == 1
        
        # Generate development-focused report
        generator = FMEAReportGenerator()
        dev_markdown = generator.generate_markdown_report(dev_report)
        
        assert "Development Risk Assessment" in dev_markdown
        assert "Risk by Subsystem" in dev_markdown
    
    def test_compliance_documentation_scenario(self):
        """Test generating FMEA documentation for compliance purposes."""
        # Create comprehensive entries covering different risk types
        compliance_entries = [
            # Safety-critical entry
            FMEAEntry(
                id="safety_critical_001",
                taxonomy_id="prioritization_safety_issues",
                system_type=SystemType.EVALUATIVE,
                subsystem=Subsystem.PLANNING,
                cause="Agent prioritizes efficiency over safety constraints",
                effect="Potential physical harm to users or equipment",
                severity=10, occurrence=3, detection=6,
                detection_method=DetectionMethod.HUMAN_OVERSIGHT,
                mitigation=["Safety-first priority weighting", "Emergency stop mechanisms", "Human safety override"],
                agent_capabilities=["autonomy", "environment_interaction"],
                potential_effects=["User harm", "Equipment damage"],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                created_by="Safety Engineer",
                scenario="Autonomous manufacturing agent optimizes for speed, ignoring safety protocols"
            ),
            
            # Privacy/compliance entry
            FMEAEntry(
                id="privacy_compliance_001",
                taxonomy_id="loss_of_data_provenance",
                system_type=SystemType.MULTI_AGENT_DISTRIBUTED,
                subsystem=Subsystem.KNOWLEDGE_BASE,
                cause="Data lineage lost during inter-agent communication",
                effect="Unable to comply with data protection regulations",
                severity=8, occurrence=7, detection=8,
                detection_method=DetectionMethod.AUDIT_TRAIL,
                mitigation=["Comprehensive data lineage tracking", "Privacy-preserving protocols", "Regular compliance audits"],
                agent_capabilities=["collaboration", "knowledge_access"],
                potential_effects=["Regulatory violations", "Privacy breaches"],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                created_by="Compliance Officer",
                scenario="Multi-agent system processes personal data across jurisdictions without proper tracking"
            )
        ]
        
        compliance_report = FMEAReport(
            title="Regulatory Compliance FMEA - Autonomous AI System",
            system_description="Comprehensive risk analysis for regulatory compliance in autonomous AI deployment",
            entries=compliance_entries,
            created_date=datetime.now(),
            created_by="Compliance Team",
            version="1.0",
            scope="Safety and privacy compliance assessment",
            assumptions=["System operates in regulated environment", "Human oversight available"],
            limitations=["Analysis based on current regulatory framework"]
        )
        
        # Generate comprehensive compliance report
        generator = FMEAReportGenerator()
        compliance_markdown = generator.generate_markdown_report(compliance_report)
        
        # Verify compliance-specific content
        assert "Regulatory Compliance" in compliance_markdown
        assert "safety_critical_001" in compliance_markdown
        assert "privacy_compliance_001" in compliance_markdown
        assert "safety" in compliance_markdown.lower()
        assert "privacy" in compliance_markdown.lower() or "data protection" in compliance_markdown.lower()
        
        # CSV export for regulatory submission
        csv_content = generator.generate_csv_export(compliance_report)
        assert "safety_critical_001" in csv_content
        assert "privacy_compliance_001" in csv_content