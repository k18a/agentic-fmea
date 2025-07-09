#!/usr/bin/env python3
"""
Comprehensive test suite for validating failure-mode-specific guidance implementation.

This test suite validates the transformation of the library from a generic FMEA tool
into an AI safety knowledge base with domain-specific guidance.
"""

import pytest
from datetime import datetime
from agentic_fmea import (
    TaxonomyLoader, FMEAEntry, FMEAReport, RiskCalculator, FMEAReportGenerator,
    SystemType, Subsystem, DetectionMethod
)


class TestGuidanceFieldsLoading:
    """Test that new guidance fields are properly loaded from taxonomy."""
    
    def test_memory_poisoning_has_guidance(self):
        """Test that memory_poisoning has comprehensive guidance fields."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("memory_poisoning")
        
        assert failure_mode is not None
        
        # Check that guidance fields exist and are populated
        assert failure_mode.recommended_mitigations is not None
        assert len(failure_mode.recommended_mitigations) > 0
        assert failure_mode.detection_strategies is not None
        assert len(failure_mode.detection_strategies) > 0
        assert failure_mode.implementation_notes is not None
        assert len(failure_mode.implementation_notes) > 0
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check specific content for memory poisoning
        assert any("memory" in mitigation.lower() for mitigation in failure_mode.recommended_mitigations)
        assert any("memory" in strategy.lower() for strategy in failure_mode.detection_strategies)
        assert any("memory" in note.lower() for note in failure_mode.implementation_notes)
    
    def test_agent_compromise_has_guidance(self):
        """Test that agent_compromise has comprehensive guidance fields."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("agent_compromise")
        
        assert failure_mode is not None
        
        # Check that guidance fields exist and are populated
        assert failure_mode.recommended_mitigations is not None
        assert len(failure_mode.recommended_mitigations) > 0
        assert failure_mode.detection_strategies is not None
        assert len(failure_mode.detection_strategies) > 0
        assert failure_mode.implementation_notes is not None
        assert len(failure_mode.implementation_notes) > 0
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check specific content for agent compromise
        assert any("agent" in mitigation.lower() for mitigation in failure_mode.recommended_mitigations)
        assert any("cryptographic" in mitigation.lower() for mitigation in failure_mode.recommended_mitigations)
    
    def test_bias_amplification_has_guidance(self):
        """Test that bias_amplification has comprehensive guidance fields."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("bias_amplification")
        
        assert failure_mode is not None
        
        # Check that guidance fields exist and are populated
        assert failure_mode.recommended_mitigations is not None
        assert len(failure_mode.recommended_mitigations) > 0
        assert failure_mode.detection_strategies is not None
        assert len(failure_mode.detection_strategies) > 0
        assert failure_mode.implementation_notes is not None
        assert len(failure_mode.implementation_notes) > 0
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check specific content for bias amplification
        assert any("bias" in mitigation.lower() for mitigation in failure_mode.recommended_mitigations)
        assert any("demographic" in strategy.lower() for strategy in failure_mode.detection_strategies)
    
    def test_hallucinations_has_guidance(self):
        """Test that hallucinations has comprehensive guidance fields."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("hallucinations")
        
        assert failure_mode is not None
        
        # Check that guidance fields exist and are populated
        assert failure_mode.recommended_mitigations is not None
        assert len(failure_mode.recommended_mitigations) > 0
        assert failure_mode.detection_strategies is not None
        assert len(failure_mode.detection_strategies) > 0
        assert failure_mode.implementation_notes is not None
        assert len(failure_mode.implementation_notes) > 0
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check specific content for hallucinations
        assert any("fact" in mitigation.lower() or "verification" in mitigation.lower() 
                  for mitigation in failure_mode.recommended_mitigations)
        assert any("confidence" in strategy.lower() or "consistency" in strategy.lower()
                  for strategy in failure_mode.detection_strategies)
    
    def test_failure_modes_without_guidance(self):
        """Test that failure modes without guidance fields handle None gracefully."""
        loader = TaxonomyLoader()
        # Test a failure mode that doesn't have guidance fields
        failure_mode = loader.get_failure_mode("agent_injection")
        
        assert failure_mode is not None
        
        # These should be None or empty for modes without guidance
        assert failure_mode.recommended_mitigations is None
        assert failure_mode.detection_strategies is None
        assert failure_mode.implementation_notes is None
        assert failure_mode.related_modes is None


class TestGuidanceRetrieval:
    """Test the get_guidance_for_failure_mode functionality."""
    
    def test_get_guidance_for_memory_poisoning(self):
        """Test retrieving comprehensive guidance for memory poisoning."""
        loader = TaxonomyLoader()
        guidance = loader.get_guidance_for_failure_mode("memory_poisoning")
        
        assert guidance is not None
        assert guidance["id"] == "memory_poisoning"
        assert guidance["description"] != ""
        assert guidance["category"] == "existing_security"
        assert guidance["pillar"] == "security"
        assert guidance["novel"] == False
        
        # Check guidance fields are populated
        assert len(guidance["recommended_mitigations"]) > 0
        assert len(guidance["detection_strategies"]) > 0
        assert len(guidance["implementation_notes"]) > 0
        assert len(guidance["related_modes"]) > 0
        
        # Check for specific memory-related guidance
        assert any("memory" in mitigation.lower() for mitigation in guidance["recommended_mitigations"])
    
    def test_get_guidance_for_nonexistent_mode(self):
        """Test that guidance returns None for nonexistent failure modes."""
        loader = TaxonomyLoader()
        guidance = loader.get_guidance_for_failure_mode("nonexistent_mode")
        assert guidance is None
    
    def test_get_guidance_for_mode_without_guidance(self):
        """Test guidance retrieval for mode without guidance fields."""
        loader = TaxonomyLoader()
        guidance = loader.get_guidance_for_failure_mode("agent_injection")
        
        assert guidance is not None
        assert guidance["id"] == "agent_injection"
        # Empty lists for modes without guidance
        assert guidance["recommended_mitigations"] == []
        assert guidance["detection_strategies"] == []
        assert guidance["implementation_notes"] == []
        assert guidance["related_modes"] == []


class TestDomainSpecificRecommendations:
    """Test that recommendations are now domain-specific and actionable."""
    
    def test_memory_poisoning_specific_recommendations(self):
        """Test that memory poisoning gets specific memory validation recommendations."""
        calculator = RiskCalculator()
        
        # Create a memory poisoning entry
        entry = FMEAEntry(
            id="test_memory_poison",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Malicious content injected into memory",
            effect="Agent acts on malicious instructions",
            severity=8, occurrence=6, detection=7,
            detection_method=DetectionMethod.AUTOMATED_MONITORING,
            mitigation=["Input validation"],
            agent_capabilities=["memory"],
            potential_effects=["Agent misalignment"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )
        
        detailed_recommendations = calculator.get_detailed_recommendations(entry)
        
        # Check that we get taxonomy-specific recommendations
        assert "taxonomy_specific" in detailed_recommendations
        taxonomy_specific = detailed_recommendations["taxonomy_specific"]
        
        assert len(taxonomy_specific["recommended_mitigations"]) > 0
        assert len(taxonomy_specific["detection_strategies"]) > 0
        assert len(taxonomy_specific["implementation_notes"]) > 0
        assert len(taxonomy_specific["related_modes"]) > 0
        
        # Check for memory-specific recommendations
        mitigations = taxonomy_specific["recommended_mitigations"]
        assert any("memory" in mitigation.lower() for mitigation in mitigations)
        assert any("validation" in mitigation.lower() or "integrity" in mitigation.lower()
                  for mitigation in mitigations)
    
    def test_agent_compromise_specific_recommendations(self):
        """Test that agent_compromise gets cryptographic identity recommendations."""
        calculator = RiskCalculator()
        
        entry = FMEAEntry(
            id="test_agent_compromise",
            taxonomy_id="agent_compromise",
            system_type=SystemType.MULTI_AGENT_COLLABORATIVE,
            subsystem=Subsystem.IDENTITY,
            cause="Weak agent authentication",
            effect="Malicious agent infiltrates system",
            severity=9, occurrence=5, detection=8,
            detection_method=DetectionMethod.STATIC_ANALYSIS,
            mitigation=["Basic authentication"],
            agent_capabilities=["collaboration"],
            potential_effects=["System compromise"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )
        
        detailed_recommendations = calculator.get_detailed_recommendations(entry)
        taxonomy_specific = detailed_recommendations["taxonomy_specific"]
        
        # Check for cryptographic and identity-specific recommendations
        mitigations = taxonomy_specific["recommended_mitigations"]
        assert any("cryptographic" in mitigation.lower() for mitigation in mitigations)
        assert any("authentication" in mitigation.lower() or "authorization" in mitigation.lower()
                  for mitigation in mitigations)
    
    def test_bias_amplification_specific_recommendations(self):
        """Test that bias_amplification gets AI-specific bias detection guidance."""
        calculator = RiskCalculator()
        
        entry = FMEAEntry(
            id="test_bias_amplification",
            taxonomy_id="bias_amplification",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.PLANNING,
            cause="Biased training data",
            effect="Discriminatory decisions",
            severity=7, occurrence=6, detection=8,
            detection_method=DetectionMethod.HUMAN_OVERSIGHT,
            mitigation=["Diverse training data"],
            agent_capabilities=["autonomy"],
            potential_effects=["Discrimination"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )
        
        detailed_recommendations = calculator.get_detailed_recommendations(entry)
        taxonomy_specific = detailed_recommendations["taxonomy_specific"]
        
        # Check for bias-specific recommendations
        mitigations = taxonomy_specific["recommended_mitigations"]
        detection_strategies = taxonomy_specific["detection_strategies"]
        
        assert any("bias" in mitigation.lower() for mitigation in mitigations)
        assert any("demographic" in strategy.lower() for strategy in detection_strategies)
        assert any("fairness" in mitigation.lower() for mitigation in mitigations)
    
    def test_hallucinations_specific_recommendations(self):
        """Test that hallucinations gets enhanced detection strategies."""
        calculator = RiskCalculator()
        
        entry = FMEAEntry(
            id="test_hallucinations",
            taxonomy_id="hallucinations",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.PLANNING,
            cause="Insufficient grounding",
            effect="Incorrect factual information",
            severity=6, occurrence=7, detection=5,
            detection_method=DetectionMethod.AUTOMATED_MONITORING,
            mitigation=["Basic fact checking"],
            agent_capabilities=["autonomy"],
            potential_effects=["Incorrect decision-making"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )
        
        detailed_recommendations = calculator.get_detailed_recommendations(entry)
        taxonomy_specific = detailed_recommendations["taxonomy_specific"]
        
        # Check for hallucination-specific recommendations
        mitigations = taxonomy_specific["recommended_mitigations"]
        detection_strategies = taxonomy_specific["detection_strategies"]
        
        assert any("fact" in mitigation.lower() or "verification" in mitigation.lower()
                  for mitigation in mitigations)
        assert any("confidence" in strategy.lower() or "consistency" in strategy.lower()
                  for strategy in detection_strategies)
        assert any("retrieval" in mitigation.lower() or "knowledge" in mitigation.lower()
                  for mitigation in mitigations)


class TestReportGeneration:
    """Test that reports now include AI safety knowledge base sections."""
    
    def test_ai_safety_knowledge_base_summary_section(self):
        """Test that reports include AI Safety Knowledge Base Summary section."""
        entries = [
            self._create_entry("test_1", "memory_poisoning", 8, 6, 7),
            self._create_entry("test_2", "agent_compromise", 9, 5, 6),
            self._create_entry("test_3", "bias_amplification", 6, 7, 8)
        ]
        
        report = FMEAReport(
            title="Test Report",
            system_description="Test system",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Check for AI Safety Knowledge Base Summary section
        assert "## AI Safety Knowledge Base Summary" in markdown_report
        assert "domain-specific guidance from the Microsoft AI Red Team taxonomy" in markdown_report
        
        # Check that each failure mode is covered
        assert "memory_poisoning" in markdown_report
        assert "agent_compromise" in markdown_report
        assert "bias_amplification" in markdown_report
    
    def test_knowledge_base_section_content(self):
        """Test the content of the knowledge base section."""
        entries = [
            self._create_entry("test_memory", "memory_poisoning", 8, 6, 7)
        ]
        
        report = FMEAReport(
            title="Knowledge Base Test",
            system_description="Test",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Check for specific knowledge base content
        assert "**Type:** Existing Security (Security)" in markdown_report
        assert "**Key Mitigations:**" in markdown_report
        assert "**Detection Strategies:**" in markdown_report
        assert "**Related Modes:**" in markdown_report
        
        # Check for memory-specific content
        assert "memory content validation" in markdown_report.lower() or "memory validation" in markdown_report.lower()
    
    def test_empty_report_knowledge_base_section(self):
        """Test knowledge base section with empty report."""
        report = FMEAReport(
            title="Empty Report",
            system_description="Empty test",
            entries=[],
            created_date=datetime.now(),
            created_by="Test"
        )
        
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Should still have the section but indicate no entries
        assert "## AI Safety Knowledge Base Summary" in markdown_report
        assert "No entries available for taxonomy guidance" in markdown_report
    
    def test_detailed_entries_include_taxonomy_guidance(self):
        """Test that detailed entries include taxonomy-specific guidance."""
        entries = [
            self._create_entry("high_risk", "memory_poisoning", 8, 6, 7)  # High risk
        ]
        
        report = FMEAReport(
            title="Detailed Entries Test",
            system_description="Test",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Check for taxonomy-specific guidance in detailed entries
        assert "**Failure Mode Specific Mitigations:**" in markdown_report
        assert "**Detection Strategies:**" in markdown_report
        assert "**Implementation Notes:**" in markdown_report
        assert "**Related Failure Modes:**" in markdown_report
        
        # Check for memory-specific content
        assert "memory" in markdown_report.lower()
    
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
            detection_method=DetectionMethod.AUTOMATED_MONITORING,
            mitigation=[f"Test mitigation for {entry_id}"],
            agent_capabilities=["autonomy"],
            potential_effects=[f"Test effect for {entry_id}"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )


class TestCrossReferences:
    """Test that cross-references between related failure modes work correctly."""
    
    def test_memory_poisoning_cross_references(self):
        """Test cross-references for memory poisoning."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("memory_poisoning")
        
        assert failure_mode is not None
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check that related modes exist in taxonomy
        for related_mode in failure_mode.related_modes:
            related_failure_mode = loader.get_failure_mode(related_mode)
            assert related_failure_mode is not None, f"Related mode {related_mode} not found"
    
    def test_agent_compromise_cross_references(self):
        """Test cross-references for agent compromise."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("agent_compromise")
        
        assert failure_mode is not None
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check that related modes exist in taxonomy
        for related_mode in failure_mode.related_modes:
            related_failure_mode = loader.get_failure_mode(related_mode)
            assert related_failure_mode is not None, f"Related mode {related_mode} not found"
    
    def test_bias_amplification_cross_references(self):
        """Test cross-references for bias amplification."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("bias_amplification")
        
        assert failure_mode is not None
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check that related modes exist in taxonomy
        for related_mode in failure_mode.related_modes:
            related_failure_mode = loader.get_failure_mode(related_mode)
            assert related_failure_mode is not None, f"Related mode {related_mode} not found"
    
    def test_hallucinations_cross_references(self):
        """Test cross-references for hallucinations."""
        loader = TaxonomyLoader()
        failure_mode = loader.get_failure_mode("hallucinations")
        
        assert failure_mode is not None
        assert failure_mode.related_modes is not None
        assert len(failure_mode.related_modes) > 0
        
        # Check that related modes exist in taxonomy
        for related_mode in failure_mode.related_modes:
            related_failure_mode = loader.get_failure_mode(related_mode)
            assert related_failure_mode is not None, f"Related mode {related_mode} not found"
    
    def test_cross_references_in_report(self):
        """Test that cross-references appear in generated reports."""
        entries = [
            self._create_entry("test_memory", "memory_poisoning", 8, 6, 7)
        ]
        
        report = FMEAReport(
            title="Cross-Reference Test",
            system_description="Test",
            entries=entries,
            created_date=datetime.now(),
            created_by="Test"
        )
        
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Check that related modes are shown in knowledge base summary
        assert "**Related Modes:**" in markdown_report
        
        # Check that detailed entries include related modes
        assert "**Related Failure Modes:**" in markdown_report
    
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
            detection_method=DetectionMethod.AUTOMATED_MONITORING,
            mitigation=[f"Test mitigation for {entry_id}"],
            agent_capabilities=["autonomy"],
            potential_effects=[f"Test effect for {entry_id}"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Test"
        )


class TestEnhancedMemoryPoisoning:
    """Test the enhanced memory poisoning case study."""
    
    def test_enhanced_memory_poisoning_case_study(self):
        """Test the enhanced memory poisoning case study with specific guidance."""
        loader = TaxonomyLoader()
        calculator = RiskCalculator()
        
        # Create enhanced memory poisoning entry
        entry = FMEAEntry(
            id="enhanced_memory_poison",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Malicious email with embedded instructions processed by agent",
            effect="Agent autonomously stores and acts on malicious instructions",
            severity=8, occurrence=6, detection=7,
            detection_method=DetectionMethod.AUTOMATED_MONITORING,
            mitigation=["Input validation", "Memory access controls"],
            agent_capabilities=["autonomy", "memory", "email_processing"],
            potential_effects=["Agent misalignment", "Data exfiltration"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Security Team",
            scenario="Email assistant with semantic memory processes malicious email"
        )
        
        # Test enhanced recommendations
        detailed_recommendations = calculator.get_detailed_recommendations(entry)
        taxonomy_specific = detailed_recommendations["taxonomy_specific"]
        
        # Should have memory-specific mitigations
        assert len(taxonomy_specific["recommended_mitigations"]) > 0
        memory_mitigations = taxonomy_specific["recommended_mitigations"]
        assert any("memory" in mitigation.lower() for mitigation in memory_mitigations)
        assert any("validation" in mitigation.lower() or "integrity" in mitigation.lower()
                  for mitigation in memory_mitigations)
        
        # Should have memory-specific detection strategies
        assert len(taxonomy_specific["detection_strategies"]) > 0
        detection_strategies = taxonomy_specific["detection_strategies"]
        assert any("memory" in strategy.lower() for strategy in detection_strategies)
        assert any("behavioral" in strategy.lower() for strategy in detection_strategies)
        
        # Should have implementation notes
        assert len(taxonomy_specific["implementation_notes"]) > 0
        implementation_notes = taxonomy_specific["implementation_notes"]
        assert any("memory" in note.lower() for note in implementation_notes)
    
    def test_memory_poisoning_report_enhancement(self):
        """Test that memory poisoning reports are enhanced with knowledge base content."""
        entry = FMEAEntry(
            id="memory_poison_enhanced",
            taxonomy_id="memory_poisoning",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.MEMORY,
            cause="Malicious content injection",
            effect="Persistent malicious behavior",
            severity=8, occurrence=6, detection=7,
            detection_method=DetectionMethod.AUTOMATED_MONITORING,
            mitigation=["Basic validation"],
            agent_capabilities=["memory"],
            potential_effects=["Agent misalignment"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Security Team"
        )
        
        report = FMEAReport(
            title="Enhanced Memory Poisoning Analysis",
            system_description="Memory poisoning analysis with enhanced guidance",
            entries=[entry],
            created_date=datetime.now(),
            created_by="Security Team"
        )
        
        generator = FMEAReportGenerator()
        markdown_report = generator.generate_markdown_report(report)
        
        # Check for enhanced content
        assert "memory_poisoning" in markdown_report
        assert "**Key Mitigations:**" in markdown_report
        assert "**Detection Strategies:**" in markdown_report
        assert "**Implementation Notes:**" in markdown_report
        
        # Check for memory-specific enhanced content
        assert "memory content validation" in markdown_report.lower() or "memory validation" in markdown_report.lower()
        assert "semantic analysis" in markdown_report.lower() or "memory access controls" in markdown_report.lower()


class TestPerformanceImpact:
    """Test performance impact of knowledge base features."""
    
    def test_taxonomy_loading_performance(self):
        """Test that taxonomy loading with guidance fields doesn't significantly impact performance."""
        import time
        
        # Test multiple loads to see if there's caching
        start_time = time.time()
        for _ in range(10):
            loader = TaxonomyLoader()
            loader.load_taxonomy()
        first_load_time = time.time() - start_time
        
        # Test subsequent loads (should be faster due to caching)
        start_time = time.time()
        for _ in range(10):
            loader = TaxonomyLoader()
            loader.get_all_failure_modes()
        cached_load_time = time.time() - start_time
        
        # Performance should be reasonable (less than 1 second for 10 loads)
        assert first_load_time < 1.0, f"Taxonomy loading too slow: {first_load_time}s"
        assert cached_load_time < 1.0, f"Cached loading too slow: {cached_load_time}s"
    
    def test_guidance_retrieval_performance(self):
        """Test that guidance retrieval doesn't significantly impact performance."""
        import time
        
        loader = TaxonomyLoader()
        
        # Test retrieving guidance for multiple failure modes
        failure_modes = ["memory_poisoning", "agent_compromise", "bias_amplification", "hallucinations"]
        
        start_time = time.time()
        for _ in range(100):  # 100 retrievals
            for mode in failure_modes:
                guidance = loader.get_guidance_for_failure_mode(mode)
                assert guidance is not None
        
        total_time = time.time() - start_time
        
        # Should be fast (less than 1 second for 400 retrievals)
        assert total_time < 1.0, f"Guidance retrieval too slow: {total_time}s for 400 retrievals"
    
    def test_report_generation_performance(self):
        """Test that report generation with knowledge base content doesn't significantly impact performance."""
        import time
        
        # Create multiple entries with different failure modes
        entries = []
        for i in range(20):
            entry = FMEAEntry(
                id=f"perf_test_{i}",
                taxonomy_id="memory_poisoning" if i % 2 == 0 else "agent_compromise",
                system_type=SystemType.SINGLE_AGENT,
                subsystem=Subsystem.MEMORY,
                cause=f"Test cause {i}",
                effect=f"Test effect {i}",
                severity=5 + (i % 5),
                occurrence=5 + (i % 5),
                detection=5 + (i % 5),
                detection_method=DetectionMethod.AUTOMATED_MONITORING,
                mitigation=[f"Test mitigation {i}"],
                agent_capabilities=["autonomy"],
                potential_effects=[f"Test effect {i}"],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                created_by="Performance Test"
            )
            entries.append(entry)
        
        report = FMEAReport(
            title="Performance Test Report",
            system_description="Performance test with multiple entries",
            entries=entries,
            created_date=datetime.now(),
            created_by="Performance Test"
        )
        
        generator = FMEAReportGenerator()
        
        start_time = time.time()
        markdown_report = generator.generate_markdown_report(report)
        generation_time = time.time() - start_time
        
        # Report generation should be fast (less than 2 seconds for 20 entries)
        assert generation_time < 2.0, f"Report generation too slow: {generation_time}s for 20 entries"
        
        # Report should still contain all expected content
        assert "## AI Safety Knowledge Base Summary" in markdown_report
        assert len(markdown_report) > 1000  # Should be substantial content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])