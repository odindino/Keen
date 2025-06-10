"""
實驗會話
Experiment Session

整合所有型別管理器的主要類別，提供統一的實驗資料管理介面
Main class integrating all type managers, providing unified experiment data management interface
"""

import os
import logging
import re  # Added import
from typing import Dict, List, Optional, Tuple, Any, Union

from .parsers.txt_parser import TxtParser
from .file_proxy import FileProxy
from .type_managers import TopoManager, CitsManager, StsManager, TxtManager
from .data_models import FileInfo

logger = logging.getLogger(__name__)


class ExperimentSession:
    """
    Manages an experiment session, providing access to its data files.
    """

    # Define known signal patterns as a class constant for _extract_signal_type_and_direction
    _KNOWN_SIGNAL_PATTERNS = sorted(
        [
            "Topo",
            "Lia1X",
            "Lia1Y",
            "Lia1R",
            "Lia2X",
            "Lia2Y",
            "Lia2R",
            "Lia3X",
            "Lia3Y",
            "Lia3R",
            "It_to_PC",
            "InA",
            "QPlus",
            "Bias",
            "Frequency",
            "Drive",
            "Phase",
            "df",
        ],
        key=len,
        reverse=True,
    )

    def __init__(self, experiment_file_path: str):
        if not os.path.isfile(experiment_file_path):
            raise FileNotFoundError(f"Experiment file not found: {experiment_file_path}")
        if not experiment_file_path.lower().endswith(".txt"):
            raise ValueError("Experiment file must be a .txt file.")

        self.txt_file_path: str = experiment_file_path
        self.base_path: str = os.path.dirname(experiment_file_path)
        self.experiment_name: str = os.path.splitext(os.path.basename(experiment_file_path))[0]

        self._short_key_to_full_key_map: Dict[str, str] = {}
        self.available_files: Dict[str, List[str]] = {"txt": [], "int": [], "cits": [], "sts": []}

        # Initialize managers
        # Assuming managers take base_path or similar configuration
        self.txt_manager = TxtManager(self.base_path)
        self.topo_manager = TopoManager(self.base_path)
        self.cits_manager = CitsManager(self.base_path)
        self.sts_manager = StsManager(self.base_path)

        self._manager_map: Dict[str, Any] = {
            "txt": self.txt_manager,
            "int": self.topo_manager,  # Assuming TopoManager handles all .int files
            "cits": self.cits_manager,
            "sts": self.sts_manager,
        }

        # Add property aliases for FileProxy compatibility
        self.txt = self.txt_manager
        self.topo = self.topo_manager
        self.cits = self.cits_manager
        self.sts = self.sts_manager

        self._load_experiment()

    def _add_to_short_key_map(self, short_key: str, full_key: str):
        """Adds a short key mapping. Short keys are stored in lowercase."""
        normalized_short_key = short_key.lower()
        if normalized_short_key in self._short_key_to_full_key_map:
            logger.warning(
                f"Short key '{normalized_short_key}' (from '{short_key}') for full key '{full_key}' "
                f"already exists and maps to '{self._short_key_to_full_key_map[normalized_short_key]}'. Overwriting."
            )
        self._short_key_to_full_key_map[normalized_short_key] = full_key
        logger.debug(f"Mapped short key '{normalized_short_key}' to full key '{full_key}'")

    def _extract_signal_type_and_direction(self, filename_stem: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts signal type and direction from a filename stem.
        Primarily for .int files or as a fallback for .dat files.
        Example: '...113Lia1RFwd' -> ('Lia1R', 'Fwd')
                 '...Topo' -> ('Topo', None)
                 '...Lia1R_Matrix' -> ('Lia1R', None)
        """
        if not filename_stem:
            return None, None

        signal_part = filename_stem
        direction = None

        if signal_part.endswith("Fwd"):
            direction = "Fwd"
            signal_part = signal_part[:-3]
        elif signal_part.endswith("Bwd"):
            direction = "Bwd"
            signal_part = signal_part[:-3]

        if signal_part.endswith("_Matrix"):  # Common for CITS .dat files
            signal_part = signal_part[:-7]

        extracted_signal = None
        for sig_pattern in self._KNOWN_SIGNAL_PATTERNS:
            if signal_part.endswith(sig_pattern):
                prefix_part = signal_part[:-len(sig_pattern)]
                if not prefix_part or not prefix_part[-1].isalpha():
                    extracted_signal = sig_pattern
                    break

        if not extracted_signal and signal_part:
            # Fallback: take the last alphanumeric component after stripping leading non-alphanumeric
            # and then stripping leading digits.
            match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)$', signal_part)  # Prefer ending with letter or underscore
            if not match:  # if no match (e.g. all numbers, or ends with number after underscore)
                match = re.search(r'([a-zA-Z0-9]+)$', signal_part)

            if match:
                candidate = match.group(1)
                candidate_no_digits = re.sub(r'^\d+', '', candidate)
                if candidate_no_digits and candidate_no_digits[0].isalpha():  # Must not be all digits, and preferably start with letter
                    extracted_signal = candidate_no_digits
                elif candidate and candidate[0].isalpha():  # Fallback to candidate if it started with letter
                    extracted_signal = candidate
                elif not candidate_no_digits and candidate:  # all digits
                    extracted_signal = candidate  # e.g. a channel number like "0" or "1"

        return extracted_signal if extracted_signal else None, direction

    def _load_experiment(self):
        """Loads the main experiment .txt file and associated data files."""
        parser = TxtParser(self.txt_file_path)
        parse_result = parser.parse()

        if not parse_result.success or not parse_result.data:
            errors = parse_result.errors or ["Unknown parsing error"]
            logger.error(f"Failed to parse experiment file {self.txt_file_path}: {errors}")
            # Optionally raise an exception here or handle gracefully
            raise RuntimeError(f"Could not parse experiment file: {', '.join(errors)}")

        txt_data_content = parse_result.data

        # Register the main .txt file itself
        main_txt_full_key = self.experiment_name
        
        # Create FileInfo for the main TXT file
        txt_file_info = FileInfo(
            path=self.txt_file_path,
            type="txt",
            size=os.path.getsize(self.txt_file_path)
        )
        self.txt_manager.add_file(main_txt_full_key, txt_file_info)
        self.available_files["txt"].append(main_txt_full_key)
        self._add_to_short_key_map("experiment_txt", main_txt_full_key)
        self._add_to_short_key_map(main_txt_full_key, main_txt_full_key)  # Allow access by full name as short key too

        # Register associated INT and DAT files
        self._register_associated_files(txt_data_content)
        logger.info(f"Experiment '{self.experiment_name}' loaded. Available short keys: {self.available_short_keys}")

    def _register_associated_files(self, txt_data_content: Dict[str, Any]):
        """Registers .int and .dat files described in the parsed .txt data."""
        # Register INT files
        for int_file_desc in txt_data_content.get("int_files", []):
            filename = int_file_desc.get("filename")
            if not filename:
                continue

            full_key = os.path.splitext(filename)[0]
            file_path = os.path.join(self.base_path, filename)

            # Create FileInfo for the INT file
            int_file_info = FileInfo(
                path=file_path,
                type="int",
                size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                signal_type=int_file_desc.get("signal_type"),
                direction=int_file_desc.get("direction")
            )
            self.topo_manager.add_file(full_key, int_file_info)
            self.available_files["int"].append(full_key)

            signal_type, direction = self._extract_signal_type_and_direction(full_key)
            if signal_type:
                short_key = signal_type
                if direction:
                    short_key += direction
                self._add_to_short_key_map(short_key, full_key)
            self._add_to_short_key_map(full_key, full_key)  # Also map full key to itself

        # Register DAT files
        for dat_file_desc in txt_data_content.get("dat_files", []):
            filename = dat_file_desc.get("filename")
            if not filename:
                continue

            full_key = os.path.splitext(filename)[0]
            file_path = os.path.join(self.base_path, filename)

            measurement_mode = dat_file_desc.get("measurement_mode", "unknown").upper()
            measurement_type = dat_file_desc.get("measurement_type")  # From TxtParser's _parse_caption

            manager_key = None
            manager = None

            if measurement_mode == "CITS":
                manager = self.cits_manager
                manager_key = "cits"
            elif measurement_mode == "STS":
                manager = self.sts_manager
                manager_key = "sts"
            else:
                logger.warning(
                    f"Unknown measurement_mode '{measurement_mode}' for DAT file '{filename}'. "
                    f"Attempting to classify as STS by default."
                )
                # Default classification or skip
                manager = self.sts_manager  # Default to STS
                manager_key = "sts"

            if manager and manager_key:
                # Create FileInfo for the DAT file
                dat_file_info = FileInfo(
                    path=file_path,
                    type="dat",
                    size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                    signal_type=measurement_type
                )
                manager.add_file(full_key, dat_file_info)
                self.available_files[manager_key].append(full_key)

                # Generate short key for DAT file
                short_key_base = measurement_type
                if not short_key_base or short_key_base == "unknown":
                    # Fallback to extracting from filename if measurement_type is not informative
                    fallback_signal, _ = self._extract_signal_type_and_direction(full_key)
                    if fallback_signal:
                        short_key_base = fallback_signal
                    else:  # Ultimate fallback
                        short_key_base = full_key.split("_")[-1]  # Last part of filename stem

                short_key = short_key_base
                if "_Matrix" in full_key and not short_key.endswith("Matrix"):  # Ensure Matrix suffix if present in filename
                    short_key += "_Matrix"

                if short_key:
                    self._add_to_short_key_map(short_key, full_key)
                self._add_to_short_key_map(full_key, full_key)  # Also map full key to itself
            else:
                logger.error(f"Could not determine manager for DAT file '{filename}' with mode '{measurement_mode}'")

    def get_file(self, file_key: str) -> FileProxy:
        """
        Retrieves a FileProxy for the given full file key.
        The file_key must be a full filename stem.
        """
        if not self.has_file(file_key):
            raise KeyError(f"Full file key '{file_key}' not found in any manager.")
        
        return FileProxy(session=self, file_key=file_key)

    def __getitem__(self, key: str) -> FileProxy:
        """
        Accesses a file by its full key (filename stem) or a registered short key.
        Short key lookup is case-insensitive.
        """
        # 1. Try key as a full file key directly
        for file_type_keys in self.available_files.values():
            if key in file_type_keys:
                try:
                    return self.get_file(key)
                except KeyError:  # Should not happen if key is in available_files and get_file is robust
                    pass  # Continue to short key lookup just in case

        # 2. Try key.lower() as a short key
        normalized_key = key.lower()
        if normalized_key in self._short_key_to_full_key_map:
            full_key = self._short_key_to_full_key_map[normalized_key]
            return self.get_file(full_key)

        # 3. If not found, raise informative KeyError
        all_fks = [fk for f_type_keys in self.available_files.values() for fk in f_type_keys]
        raise KeyError(
            f"File key '{key}' not found. \n"
            f"Available full keys (stems): {sorted(list(set(all_fks)))} \n"
            f"Available short keys: {self.available_short_keys}"
        )

    def has_file(self, file_key: str) -> bool:
        """Checks if a full file key (filename stem) is registered."""
        for manager in self._manager_map.values():
            if manager.has_file(file_key):
                return True
        return False

    @property
    def available_short_keys(self) -> List[str]:
        """Returns a sorted list of all registered short keys (lowercase)."""
        return sorted(list(self._short_key_to_full_key_map.keys()))

    def get_all_full_keys(self) -> List[str]:
        """Returns a sorted list of all unique registered full file keys (stems)."""
        all_fks = set()
        for f_type_keys in self.available_files.values():
            for fk in f_type_keys:
                all_fks.add(fk)
        return sorted(list(all_fks))

    def get_topo_files(self) -> List[str]:
        """Returns a list of available topography file keys."""
        return self.available_files.get('int', [])

    def get_cits_files(self) -> List[str]:
        """Returns a list of available CITS file keys."""
        return self.available_files.get('cits', [])

    def get_sts_files(self) -> List[str]:
        """Returns a list of available STS file keys."""
        return self.available_files.get('sts', [])

    def get_txt_files(self) -> List[str]:
        """Returns a list of available TXT file keys."""
        return self.available_files.get('txt', [])

    # ... any other existing methods ...
    # For example, if there were methods like:
    # get_cits_data, get_topo_data, they might now use __getitem__
    # or be refactored if FileProxy provides a unified way to get data.

    # Example of how existing specific getters might be simplified (optional):
    # def get_cits(self, key: str) -> Optional[CitsData]: # Assuming CitsData type
    #     file_proxy = self[key] # Use __getitem__
    #     if file_proxy and file_proxy.manager == self.cits_manager:
    #         return file_proxy.load() # Assuming FileProxy has a load method
    #     return None