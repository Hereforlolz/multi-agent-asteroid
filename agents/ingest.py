# agents/ingest.py
import logging
import os
import numpy as np
from astropy.io import fits
from typing import Tuple

class IngestAgent:
    """
    The IngestAgent is responsible for loading FITS image files,
    extracting pixel data, and reading the FITS header.

    It performs initial validation to ensure the file exists and is readable.
    """
    def __init__(self):
        self.logger = logging.getLogger("IngestAgent")
        self.logger.info("IngestAgent initialized.")

    def run(self, fits_file_path: str) -> Tuple[np.ndarray, fits.Header]:
        """
        Loads a FITS image file and returns its pixel data and header.

        Args:
            fits_file_path (str): The absolute or relative path to the FITS file.

        Returns:
            Tuple[np.ndarray, fits.Header]: A tuple containing:
                - pixel_data (np.ndarray): The 2D array of pixel values from the primary HDU.
                - header (fits.Header): The FITS header object from the primary HDU.

        Raises:
            FileNotFoundError: If the specified FITS file does not exist.
            IOError: If there's an issue reading the FITS file.
            ValueError: If the FITS file does not contain a primary HDU with data.
        """
        self.logger.info(f"Attempting to ingest FITS file: {fits_file_path}")

        # --- Bug Prevention: Input Validation ---
        if not isinstance(fits_file_path, str) or not fits_file_path:
            self.logger.error("Invalid FITS file path provided.")
            raise ValueError("FITS file path must be a non-empty string.")

        if not os.path.exists(fits_file_path):
            self.logger.error(f"FITS file not found: {fits_file_path}")
            raise FileNotFoundError(f"FITS file not found at: {fits_file_path}")

        pixel_data: np.ndarray
        header: fits.Header

        try:
            with fits.open(fits_file_path) as hdul:
                # Ensure there's a primary HDU and it contains data
                if not hdul or hdul[0].data is None:
                    self.logger.error(f"FITS file {fits_file_path} does not contain valid data in primary HDU.")
                    raise ValueError("FITS file does not contain primary HDU data.")

                pixel_data = hdul[0].data
                header = hdul[0].header
                self.logger.info(f"Successfully loaded {fits_file_path}. Data shape: {pixel_data.shape}")
                self.logger.debug(f"FITS Header: {header}")

        except Exception as e:
            self.logger.exception(f"Error ingesting FITS file {fits_file_path}: {e}")
            raise IOError(f"Failed to read FITS file {fits_file_path}: {e}")

        # --- Security/Protection: Least Privilege ---
        # In a production environment, ensure the process running this agent
        # has only read access to the FITS file directory and no more.

        return pixel_data, header

