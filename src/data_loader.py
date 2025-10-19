"""
Data loader module for reading and processing Excel files.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from loguru import logger
from pydantic import BaseModel, Field


class EnergyRecord(BaseModel):
    """Pydantic model for validating energy records."""
    client_name: Optional[str] = None
    source_type: Optional[str] = None
    power_installed: Optional[float] = None
    connection_point: Optional[str] = None
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    contact_person: Optional[str] = None
    source_file: str = Field(default="")
    source_sheet: str = Field(default="")
    row_number: int = Field(default=0)


class ExcelDataLoader:
    """
    Loads and processes Excel files containing energy sector data.
    """

    def __init__(self, input_dir: str, column_mappings: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the data loader.

        Args:
            input_dir: Directory containing Excel files
            column_mappings: Dictionary mapping standard field names to possible column names
        """
        self.input_dir = Path(input_dir)
        self.column_mappings = column_mappings or self._default_column_mappings()
        self.loaded_data: List[Dict[str, Any]] = []

    @staticmethod
    def _default_column_mappings() -> Dict[str, List[str]]:
        """Default column name mappings."""
        return {
            "client_name": ["Denumire", "Client", "Nume", "Company", "Furnizor"],
            "source_type": ["Sursa", "Tip Sursa", "Source Type", "Energie", "Tip Energie"],
            "power_installed": ["Putere", "Capacitate", "Power", "MW", "kW", "Putere Instalata"],
            "connection_point": ["Racordare", "Statie", "Connection Point", "Loc Racordare"],
            "address": ["Adresa", "Locatie", "Address", "Location"],
            "contact_phone": ["Telefon", "Phone", "Contact", "Tel"],
            "contact_email": ["Email", "E-mail", "Mail"],
            "contact_person": ["Contact", "Persoana Contact", "Contact Person", "Reprezentant"],
        }

    def find_excel_files(self, patterns: List[str] = None) -> List[Path]:
        """
        Find all Excel files in the input directory.

        Args:
            patterns: List of file patterns to match (default: ["*.xlsx", "*.xls"])

        Returns:
            List of Path objects for Excel files
        """
        if patterns is None:
            patterns = ["*.xlsx", "*.xls"]

        excel_files = []
        for pattern in patterns:
            excel_files.extend(self.input_dir.glob(pattern))

        logger.info(f"Found {len(excel_files)} Excel files in {self.input_dir}")
        return excel_files

    def detect_column(self, df: pd.DataFrame, field_name: str) -> Optional[str]:
        """
        Detect which column in the DataFrame corresponds to a standard field.

        Args:
            df: DataFrame to search
            field_name: Standard field name to look for

        Returns:
            Actual column name if found, None otherwise
        """
        possible_names = self.column_mappings.get(field_name, [])

        for col in df.columns:
            col_clean = str(col).strip()
            for possible_name in possible_names:
                if possible_name.lower() in col_clean.lower():
                    logger.debug(f"Mapped '{col}' to '{field_name}'")
                    return col

        return None

    def normalize_power_value(self, value: Any) -> Optional[float]:
        """
        Normalize power values to MW.

        Args:
            value: Raw power value

        Returns:
            Power in MW or None if invalid
        """
        if pd.isna(value):
            return None

        try:
            # Convert to string and clean
            value_str = str(value).strip().upper()

            # Remove common separators
            value_str = value_str.replace(',', '.').replace(' ', '')

            # Extract numeric value
            numeric_part = ''
            unit = 'MW'  # default

            for char in value_str:
                if char.isdigit() or char == '.':
                    numeric_part += char
                elif char in ['K', 'M', 'G']:
                    unit = char + 'W'
                    break

            if not numeric_part:
                return None

            power_value = float(numeric_part)

            # Convert to MW
            if unit == 'KW':
                power_value = power_value / 1000
            elif unit == 'GW':
                power_value = power_value * 1000

            return power_value

        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse power value '{value}': {e}")
            return None

    def load_excel_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load a single Excel file and extract records.

        Args:
            file_path: Path to Excel file

        Returns:
            List of extracted records
        """
        logger.info(f"Loading Excel file: {file_path}")
        records = []

        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)

            for sheet_name in excel_file.sheet_names:
                logger.debug(f"Processing sheet: {sheet_name}")
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Skip empty sheets
                if df.empty:
                    logger.warning(f"Sheet '{sheet_name}' is empty, skipping")
                    continue

                # Detect columns
                column_map = {}
                for field_name in self.column_mappings.keys():
                    detected_col = self.detect_column(df, field_name)
                    if detected_col:
                        column_map[field_name] = detected_col

                if not column_map:
                    logger.warning(f"No recognizable columns found in sheet '{sheet_name}'")
                    continue

                # Process each row
                for idx, row in df.iterrows():
                    record = {
                        "source_file": file_path.name,
                        "source_sheet": sheet_name,
                        "row_number": idx + 2,  # +2 for Excel row number (1-indexed + header)
                    }

                    # Extract mapped fields
                    for field_name, col_name in column_map.items():
                        value = row.get(col_name)

                        # Special handling for power values
                        if field_name == "power_installed":
                            value = self.normalize_power_value(value)
                        elif not pd.isna(value):
                            value = str(value).strip()
                        else:
                            value = None

                        record[field_name] = value

                    # Only add records with at least one non-null field
                    if any(v is not None and v != "" for k, v in record.items()
                           if k not in ["source_file", "source_sheet", "row_number"]):
                        records.append(record)

                logger.info(f"Extracted {len(records)} records from sheet '{sheet_name}'")

        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {e}")
            raise

        return records

    def load_all_files(self, file_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """
        Load all Excel files from the input directory.

        Args:
            file_patterns: File patterns to match

        Returns:
            List of all extracted records
        """
        excel_files = self.find_excel_files(file_patterns)
        all_records = []

        for file_path in excel_files:
            try:
                records = self.load_excel_file(file_path)
                all_records.extend(records)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue

        self.loaded_data = all_records
        logger.info(f"Total records loaded: {len(all_records)}")

        return all_records

    def validate_records(self, records: List[Dict[str, Any]]) -> Tuple[List[EnergyRecord], List[Dict[str, Any]]]:
        """
        Validate records using Pydantic model.

        Args:
            records: List of raw records

        Returns:
            Tuple of (valid_records, invalid_records)
        """
        valid = []
        invalid = []

        for record in records:
            try:
                energy_record = EnergyRecord(**record)
                valid.append(energy_record)
            except Exception as e:
                logger.warning(f"Invalid record from {record.get('source_file')}: {e}")
                invalid.append(record)

        logger.info(f"Validation: {len(valid)} valid, {len(invalid)} invalid records")
        return valid, invalid

    def to_dataframe(self, records: List[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Convert records to pandas DataFrame.

        Args:
            records: List of records (uses loaded_data if None)

        Returns:
            DataFrame with all records
        """
        if records is None:
            records = self.loaded_data

        return pd.DataFrame(records)

    def export_to_json(self, output_path: str, records: List[Dict[str, Any]] = None):
        """
        Export records to JSON file.

        Args:
            output_path: Path to output JSON file
            records: List of records (uses loaded_data if None)
        """
        if records is None:
            records = self.loaded_data

        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported {len(records)} records to {output_path}")

    def export_to_parquet(self, output_path: str, records: List[Dict[str, Any]] = None):
        """
        Export records to Parquet file.

        Args:
            output_path: Path to output Parquet file
            records: List of records (uses loaded_data if None)
        """
        if records is None:
            records = self.loaded_data

        df = self.to_dataframe(records)
        df.to_parquet(output_path, index=False)

        logger.info(f"Exported {len(records)} records to {output_path}")

    def get_statistics(self, records: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get statistics about loaded data.

        Args:
            records: List of records (uses loaded_data if None)

        Returns:
            Dictionary with statistics
        """
        if records is None:
            records = self.loaded_data

        df = self.to_dataframe(records)

        stats = {
            "total_records": len(records),
            "total_files": df["source_file"].nunique() if "source_file" in df.columns else 0,
            "total_sheets": df["source_sheet"].nunique() if "source_sheet" in df.columns else 0,
            "source_types": df["source_type"].value_counts().to_dict() if "source_type" in df.columns else {},
            "total_power_mw": df["power_installed"].sum() if "power_installed" in df.columns else 0,
            "avg_power_mw": df["power_installed"].mean() if "power_installed" in df.columns else 0,
            "null_counts": df.isnull().sum().to_dict(),
        }

        return stats
