import os
import shutil
import logging
from datetime import datetime
from typing import Any, Dict, Optional
import pandas as pd

from src.domain.interfaces import SpreadsheetConnector

logger = logging.getLogger(__name__)

class PandasExcelConnector(SpreadsheetConnector):
    """
    Implementation of SpreadsheetConnector using Pandas to write safely to Excel.
    """
    def __init__(self, file_path: str, sheet_name: str = "Sheet1") -> None:
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.dataframe: Optional[pd.DataFrame] = None

    def backup_file(self) -> str:
        """
        Creates a timestamped backup of the Excel file before any modifications.
        Returns the path to the backup file.
        """
        if not os.path.exists(self.file_path):
            logger.info(f"File {self.file_path} does not exist yet; skipping backup.")
            return ""
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = os.path.dirname(self.file_path)
        base_name = os.path.basename(self.file_path)
        name, ext = os.path.splitext(base_name)
        
        backup_name = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(dir_name, backup_name)
        
        shutil.copy2(self.file_path, backup_path)
        logger.info(f"Created backup of {self.file_path} at {backup_path}")
        return backup_path

    def load_spreadsheet(self) -> bool:
        """
        Loads the spreadsheet into a Pandas DataFrame.
        """
        if not os.path.exists(self.file_path):
            logger.warning(f"File {self.file_path} not found. Creating a new empty dataframe.")
            self.dataframe = pd.DataFrame()
            return True
            
        try:
            self.dataframe = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
            logger.info(f"Loaded {len(self.dataframe)} rows from {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load spreadsheet: {str(e)}")
            return False

    def append_row(self, data: Dict[str, Any]) -> bool:
        """
        Appends a dictionary as a new row to the dataframe and saves it to disk.
        Does not overwrite existing data; concatenates instead.
        """
        # Ensure we have loaded the data
        if self.dataframe is None:
            if not self.load_spreadsheet():
                raise RuntimeError("Cannot append row: failed to load spreadsheet.")
                
        # Create backup before writing
        self.backup_file()
        
        try:
            new_row_df = pd.DataFrame([data])
            if self.dataframe is not None and not self.dataframe.empty:
                # Concatenate the new row to existing data
                self.dataframe = pd.concat([self.dataframe, new_row_df], ignore_index=True)
            else:
                self.dataframe = new_row_df
                
            # Write back to Excel
            self.dataframe.to_excel(self.file_path, sheet_name=self.sheet_name, index=False)
            logger.info(f"Successfully appended row to {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to append row to {self.file_path}: {str(e)}")
            return False
