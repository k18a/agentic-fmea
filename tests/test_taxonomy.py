"""
Unit tests for taxonomy loading and validation.

Tests the Microsoft AI Red Team taxonomy loading, validation,
and search functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path

from agentic_fmea import TaxonomyLoader, FailureMode


class TestTaxonomyLoading:
    """Test taxonomy file loading and parsing."""
    
    def test_taxonomy_loads_successfully(self):
        """Test that the default taxonomy loads without errors."""
        loader = TaxonomyLoader()
        taxonomy = loader.load_taxonomy()
        
        # Should have the 4 main categories
        expected_categories = ["novel_security", "novel_safety", "existing_security", "existing_safety"]
        assert all(category in taxonomy for category in expected_categories)
        
        # Check total count matches Microsoft's taxonomy (27 failure modes)
        total_modes = sum(len(modes) for modes in taxonomy.values())
        assert total_modes == 27
    
    def test_taxonomy_category_counts(self):
        """Test that each category has the expected number of failure modes."""
        loader = TaxonomyLoader()
        taxonomy = loader.load_taxonomy()
        
        # Based on Microsoft's whitepaper
        assert len(taxonomy["novel_security"]) == 6
        assert len(taxonomy["novel_safety"]) == 4
        assert len(taxonomy["existing_security"]) == 10
        assert len(taxonomy["existing_safety"]) == 7
    
    def test_failure_mode_parsing(self):
        """Test that failure modes are parsed correctly into FailureMode objects."""
        loader = TaxonomyLoader()
        memory_poisoning = loader.get_failure_mode("memory_poisoning")
        
        assert memory_poisoning is not None
        assert isinstance(memory_poisoning, FailureMode)
        assert memory_poisoning.id == "memory_poisoning"
        assert memory_poisoning.pillar == "security"
        assert memory_poisoning.novel == False  # Existing failure mode
        assert "memory" in memory_poisoning.description.lower()
        assert len(memory_poisoning.potential_effects) > 0
        assert len(memory_poisoning.canonical_effects) > 0
    
    def test_get_all_failure_modes(self):
        """Test retrieving all failure modes."""
        loader = TaxonomyLoader()
        all_modes = loader.get_all_failure_modes()
        
        assert len(all_modes) == 27
        assert "memory_poisoning" in all_modes
        assert "agent_compromise" in all_modes
        assert all(isinstance(mode, FailureMode) for mode in all_modes.values())
    
    def test_nonexistent_failure_mode(self):
        """Test that nonexistent failure modes return None."""
        loader = TaxonomyLoader()
        result = loader.get_failure_mode("nonexistent_mode")
        assert result is None


class TestTaxonomyValidation:
    """Test taxonomy structure validation."""
    
    def test_taxonomy_validation_passes(self):
        """Test that the default taxonomy passes validation."""
        loader = TaxonomyLoader()
        errors = loader.validate_taxonomy()
        assert len(errors) == 0, f"Taxonomy validation failed: {errors}"
    
    def test_missing_category_validation(self):
        """Test validation catches missing categories."""
        # Create invalid taxonomy missing a category
        invalid_taxonomy = {
            "novel_security": {},
            "novel_safety": {},
            "existing_security": {}
            # Missing existing_safety
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_taxonomy, f)
            temp_path = f.name
        
        try:
            loader = TaxonomyLoader(temp_path)
            errors = loader.validate_taxonomy()
            assert len(errors) > 0
            assert any("existing_safety" in error for error in errors)
        finally:
            Path(temp_path).unlink()
    
    def test_missing_required_field_validation(self):
        """Test validation catches missing required fields."""
        # Create taxonomy with missing required field
        invalid_taxonomy = {
            "novel_security": {
                "invalid_mode": {
                    "pillar": "security",
                    "novel": True,
                    "description": "Test mode"
                    # Missing other required fields
                }
            },
            "novel_safety": {},
            "existing_security": {},
            "existing_safety": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_taxonomy, f)
            temp_path = f.name
        
        try:
            loader = TaxonomyLoader(temp_path)
            errors = loader.validate_taxonomy()
            assert len(errors) > 0
            assert any("Missing required field" in error for error in errors)
        finally:
            Path(temp_path).unlink()
    
    def test_invalid_pillar_validation(self):
        """Test validation catches invalid pillar values."""
        invalid_taxonomy = {
            "novel_security": {
                "invalid_mode": {
                    "pillar": "invalid_pillar",  # Should be 'security' or 'safety'
                    "novel": True,
                    "description": "Test",
                    "potential_impact": "Test",
                    "potential_effects": ["Test"],
                    "systems_likely_to_occur": "Test",
                    "example": "Test",
                    "canonical_effects": ["Test"],
                    "refs": ["Test"]
                }
            },
            "novel_safety": {},
            "existing_security": {},
            "existing_safety": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_taxonomy, f)
            temp_path = f.name
        
        try:
            loader = TaxonomyLoader(temp_path)
            errors = loader.validate_taxonomy()
            assert len(errors) > 0
            assert any("Invalid pillar value" in error for error in errors)
        finally:
            Path(temp_path).unlink()
    
    def test_file_not_found_error(self):
        """Test that missing taxonomy file raises appropriate error."""
        loader = TaxonomyLoader("/nonexistent/path/taxonomy.json")
        
        with pytest.raises(FileNotFoundError):
            loader.load_taxonomy()


class TestTaxonomyQuerying:
    """Test taxonomy search and filtering functionality."""
    
    def test_get_failure_modes_by_category(self):
        """Test filtering failure modes by category."""
        loader = TaxonomyLoader()
        
        novel_security = loader.get_failure_modes_by_category("novel_security")
        assert len(novel_security) == 6
        assert all(mode.category == "novel_security" for mode in novel_security)
        assert all(mode.novel == True for mode in novel_security)
        
        existing_safety = loader.get_failure_modes_by_category("existing_safety")
        assert len(existing_safety) == 7
        assert all(mode.category == "existing_safety" for mode in existing_safety)
        assert all(mode.novel == False for mode in existing_safety)
    
    def test_get_failure_modes_by_pillar(self):
        """Test filtering failure modes by pillar (security/safety)."""
        loader = TaxonomyLoader()
        
        security_modes = loader.get_failure_modes_by_pillar("security")
        safety_modes = loader.get_failure_modes_by_pillar("safety")
        
        # Should add up to total (27)
        assert len(security_modes) + len(safety_modes) == 27
        
        # All security modes should have pillar="security"
        assert all(mode.pillar == "security" for mode in security_modes)
        assert all(mode.pillar == "safety" for mode in safety_modes)
    
    def test_get_novel_vs_existing_modes(self):
        """Test filtering by novel vs existing failure modes."""
        loader = TaxonomyLoader()
        
        novel_modes = loader.get_novel_failure_modes()
        existing_modes = loader.get_existing_failure_modes()
        
        # Should add up to total (27)
        assert len(novel_modes) + len(existing_modes) == 27
        
        # Check novel field is correct
        assert all(mode.novel == True for mode in novel_modes)
        assert all(mode.novel == False for mode in existing_modes)
        
        # Based on taxonomy: 10 novel, 17 existing
        assert len(novel_modes) == 10
        assert len(existing_modes) == 17
    
    def test_search_failure_modes(self):
        """Test text search functionality."""
        loader = TaxonomyLoader()
        
        # Search for "memory" should find memory poisoning
        memory_results = loader.search_failure_modes("memory")
        assert len(memory_results) > 0
        assert any(mode.id == "memory_poisoning" for mode in memory_results)
        
        # Search for "agent" should find agent-related failures
        agent_results = loader.search_failure_modes("agent")
        assert len(agent_results) > 0
        agent_ids = [mode.id for mode in agent_results]
        assert "agent_compromise" in agent_ids
        
        # Search for nonexistent term
        empty_results = loader.search_failure_modes("nonexistent_term_xyz")
        assert len(empty_results) == 0
    
    def test_taxonomy_stats(self):
        """Test taxonomy statistics generation."""
        loader = TaxonomyLoader()
        stats = loader.get_taxonomy_stats()
        
        assert stats["total_failure_modes"] == 27
        assert stats["novel_modes"] == 10
        assert stats["existing_modes"] == 17
        assert stats["security_modes"] + stats["safety_modes"] == 27
        
        # Check category breakdown
        assert stats["by_category"]["novel_security"] == 6
        assert stats["by_category"]["novel_safety"] == 4
        assert stats["by_category"]["existing_security"] == 10
        assert stats["by_category"]["existing_safety"] == 7


class TestTaxonomyContent:
    """Test specific content from Microsoft's taxonomy."""
    
    def test_memory_poisoning_content(self):
        """Test that memory poisoning failure mode has correct content."""
        loader = TaxonomyLoader()
        mode = loader.get_failure_mode("memory_poisoning")
        
        assert mode.pillar == "security"
        assert mode.novel == False
        assert "memory" in mode.description.lower()
        assert "Agent misalignment" in mode.potential_effects
        assert "msft:AIRT2025" in mode.refs
    
    def test_agent_compromise_content(self):
        """Test that agent compromise failure mode has correct content."""
        loader = TaxonomyLoader()
        mode = loader.get_failure_mode("agent_compromise")
        
        assert mode.pillar == "security"
        assert mode.novel == True
        assert "compromise" in mode.description.lower()
        assert len(mode.potential_effects) > 0
    
    def test_all_modes_have_required_content(self):
        """Test that all failure modes have required content fields."""
        loader = TaxonomyLoader()
        all_modes = loader.get_all_failure_modes()
        
        for mode_id, mode in all_modes.items():
            # Required fields should not be empty
            assert mode.description.strip() != ""
            assert mode.potential_impact.strip() != ""
            assert len(mode.potential_effects) > 0
            assert mode.systems_likely_to_occur.strip() != ""
            assert mode.example.strip() != ""
            assert len(mode.canonical_effects) > 0
            assert len(mode.refs) > 0
            
            # Pillar should be valid
            assert mode.pillar in ["security", "safety"]
            
            # Category should match novel field
            if "novel" in mode.category:
                assert mode.novel == True
            else:
                assert mode.novel == False