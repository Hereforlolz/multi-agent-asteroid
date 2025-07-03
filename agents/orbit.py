# agents/orbit.py
import logging
import numpy as np
from astropy.io import fits
from skyfield.api import load, EarthSatellite, Topos
from datetime import datetime, timezone
from typing import List, Dict, Any

class OrbitAgent:
    """
    The OrbitAgent is responsible for computing (or simulating the computation of)
    orbital elements from detected object positions.
    It uses Skyfield for astronomical calculations.
    """
    def __init__(self):
        self.logger = logging.getLogger("OrbitAgent")
        self.ts = load.timescale() # Load Skyfield timescale
        self.planets = load('de421.bsp') # Load ephemeris data for planets
        self.earth = self.planets['earth']
        self.logger.info("OrbitAgent initialized with Skyfield ephemeris.")

    def run(self, detections: List[Dict[str, Any]], header: fits.Header) -> List[Dict[str, Any]]:
        """
        Computes (or simulates) dummy orbital elements for detected objects.
        In a real scenario, this would involve multiple observations over time
        and sophisticated orbit determination algorithms.

        Args:
            detections (List[Dict[str, Any]]): A list of dictionaries, each representing a detection
                                               with 'x', 'y' coordinates and 'confidence'.
            header (fits.Header): The FITS header containing WCS information for coordinate conversion.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing the estimated
                                  orbital elements for a detected object.
                                  Contains 'ra', 'dec', 'epoch', and dummy 'elements'.
        """
        self.logger.info(f"Starting orbit estimation for {len(detections)} detections.")

        # --- Bug Prevention: Input Validation ---
        if not isinstance(detections, list):
            self.logger.error("Invalid detections format. Expected a list.")
            raise ValueError("Detections must be a list of dictionaries.")
        if not isinstance(header, fits.Header):
            self.logger.error("Invalid header format. Expected an astropy.io.fits.Header object.")
            raise ValueError("Header must be an astropy.io.fits.Header object.")

        orbital_elements_list: List[Dict[str, Any]] = []

        if not detections:
            self.logger.warning("No detections provided for orbit estimation. Returning empty list.")
            return []

        try:
            # Get observation time from header (assuming 'DATE' keyword exists)
            # In a real scenario, you'd need precise timestamps for each observation.
            obs_date_str = header.get('DATE', datetime.now(timezone.utc).isoformat())
            try:
                obs_time = self.ts.utc(datetime.fromisoformat(obs_date_str.replace('Z', '+00:00')))
            except ValueError:
                self.logger.warning(f"Could not parse DATE '{obs_date_str}' from header. Using current UTC time.")
                obs_time = self.ts.now()

            # --- Fake Telescope Location (for Skyfield) ---
            # In a real scenario, this would come from the telescope metadata.
            # Using a dummy location (e.g., Palomar Observatory)
            # Latitude: 33.356389 deg, Longitude: -116.864444 deg, Elevation: 1706 m
            telescope_location = Topos(latitude_degrees=33.356389, longitude_degrees=-116.864444, elevation_m=1706)

            for i, det in enumerate(detections):
                self.logger.debug(f"Processing detection {i+1}: X={det['x']}, Y={det['y']}")

                # --- Fake Coordinate Conversion (from pixel to RA/Dec) ---
                # In a real system, you'd use astropy.wcs or similar to convert
                # pixel (x, y) to (RA, Dec) using the WCS info in the header.
                # For this dummy, we'll just assign dummy RA/Dec based on pixel position.
                # Assuming CRVAL1, CRVAL2, CDELT1, CDELT2 are in header from CalibrationAgent
                try:
                    crval1 = header['CRVAL1']
                    crval2 = header['CRVAL2']
                    cdelt1 = header['CDELT1']
                    cdelt2 = header['CDELT2']
                    crpix1 = header['CRPIX1']
                    crpix2 = header['CRPIX2']

                    # Simple linear approximation for RA/Dec based on WCS keywords
                    # This is highly simplified and not a true WCS transformation
                    ra_deg = crval1 + (det['x'] - crpix1) * cdelt1
                    dec_deg = crval2 + (det['y'] - crpix2) * cdelt2

                    # Ensure RA is within 0-360 range
                    ra_deg = ra_deg % 360
                    if ra_deg < 0:
                        ra_deg += 360

                except KeyError:
                    self.logger.warning("WCS keywords missing in header. Using dummy RA/Dec.")
                    ra_deg = 0.0 # Default dummy
                    dec_deg = 0.0 # Default dummy
                    # Assign a random RA/Dec for the dummy
                    ra_deg = np.random.uniform(0, 360)
                    dec_deg = np.random.uniform(-90, 90)

                # --- Simulate Orbit Determination ---
                # Real orbit determination requires at least 3 observations (x,y,t)
                # For a single detection, we can only provide a dummy "line of sight"
                # and placeholder orbital elements.
                
                # In a real scenario, you would:
                # 1. Collect multiple (RA, Dec, Time) observations for the same object.
                # 2. Use an orbit determination algorithm (e.g., Gauss, Gooding, or more robust methods)
                #    to compute the six orbital elements.
                # 3. Potentially use a tool like OpenOrb or a custom integrator.

                # For this example, we'll just store the detected RA/Dec and a dummy set of elements.
                dummy_orbital_elements = {
                    'ra': f"{ra_deg:.6f} deg",
                    'dec': f"{dec_deg:.6f} deg",
                    'epoch': obs_time.utc_iso(),
                    'elements': {
                        'a': np.random.uniform(1.0, 5.0), # Semi-major axis (AU)
                        'e': np.random.uniform(0.0, 0.5), # Eccentricity
                        'i': np.random.uniform(0.0, 60.0), # Inclination (degrees)
                        'node': np.random.uniform(0.0, 360.0), # Longitude of ascending node (degrees)
                        'arg_peri': np.random.uniform(0.0, 360.0), # Argument of periapsis (degrees)
                        'mean_anom': np.random.uniform(0.0, 360.0) # Mean anomaly (degrees)
                    },
                    'confidence': det['confidence'] # Carry over detection confidence
                }
                orbital_elements_list.append(dummy_orbital_elements)
                self.logger.debug(f"Simulated orbit for detection {i+1}: RA={ra_deg:.2f}, Dec={dec_deg:.2f}")

        except Exception as e:
            self.logger.exception(f"Error during orbit estimation: {e}")
            raise RuntimeError(f"Orbit estimation failed: {e}")

        # --- Security/Protection: Input Sanitization & Validation ---
        # Ensure that any data coming from previous agents or external sources
        # is validated and sanitized before being used in critical calculations.
        # Protect against numerical instabilities in orbit propagators.

        return orbital_elements_list

