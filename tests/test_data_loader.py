"""
Unit tests for data_loader module.
"""
import pytest
from pathlib import Path
import pandas as pd
from src.data_loader import ExcelDataLoader, EnergyRecord


class TestExcelDataLoader:
    """Tests for ExcelDataLoader class."""

    def test_initialization(self):
        """Test loader initialization."""
        loader = ExcelDataLoader("./data/input")
        assert loader.input_dir == Path("./data/input")
        assert loader.column_mappings is not None

    def test_default_column_mappings(self):
        """Test default column mappings."""
        loader = ExcelDataLoader("./data/input")
        mappings = loader.column_mappings

        assert "client_name" in mappings
        assert "source_type" in mappings
        assert "power_installed" in mappings
        assert isinstance(mappings["client_name"], list)

    def test_normalize_power_value(self):
        """Test power value normalization."""
        loader = ExcelDataLoader("./data/input")

        # Test MW values
        assert loader.normalize_power_value("100 MW") == 100.0
        assert loader.normalize_power_value("50MW") == 50.0

        # Test kW to MW conversion
        assert loader.normalize_power_value("1000 kW") == 1.0
        assert loader.normalize_power_value("500kW") == 0.5

        # Test GW to MW conversion
        assert loader.normalize_power_value("1 GW") == 1000.0

        # Test None values
        assert loader.normalize_power_value(None) is None
        assert loader.normalize_power_value("") is None

    def test_detect_column(self):
        """Test column detection."""
        loader = ExcelDataLoader("./data/input")

        # Create test DataFrame
        df = pd.DataFrame({
            "Denumire Companie": ["Test"],
            "Tip Sursa Energie": ["Solar"],
            "Putere (MW)": [100]
        })

        # Test detection
        assert loader.detect_column(df, "client_name") == "Denumire Companie"
        assert loader.detect_column(df, "source_type") == "Tip Sursa Energie"
        assert loader.detect_column(df, "power_installed") == "Putere (MW)"

        # Test non-existent column
        assert loader.detect_column(df, "non_existent") is None


class TestEnergyRecord:
    """Tests for EnergyRecord model."""

    def test_valid_record(self):
        """Test valid record creation."""
        record = EnergyRecord(
            client_name="Test Company",
            source_type="Solar",
            power_installed=100.0,
            source_file="test.xlsx",
            source_sheet="Sheet1",
            row_number=1
        )

        assert record.client_name == "Test Company"
        assert record.source_type == "Solar"
        assert record.power_installed == 100.0

    def test_optional_fields(self):
        """Test record with optional fields."""
        record = EnergyRecord(
            source_file="test.xlsx",
            source_sheet="Sheet1",
            row_number=1
        )

        assert record.client_name is None
        assert record.source_type is None
        assert record.power_installed is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
