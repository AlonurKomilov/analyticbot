"""
Shared base components for data processor.

This module contains shared imports, configurations, and base utilities
used across all data processor modules.
"""

import io
import json
import logging
import warnings
from typing import Any

import aiofiles
import numpy as np
import pandas as pd
import requests
from scipy import stats
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


# Shared scalers and imputers configuration
SCALERS = {
    "standard": StandardScaler(),
    "robust": RobustScaler(),
    "minmax": MinMaxScaler(),
}

IMPUTERS = {
    "mean": SimpleImputer(strategy="mean"),
    "median": SimpleImputer(strategy="median"),
    "knn": KNNImputer(n_neighbors=5),
}


__all__ = [
    "logger",
    "np",
    "pd",
    "stats",
    "SCALERS",
    "IMPUTERS",
    "aiofiles",
    "requests",
    "create_engine",
    "io",
    "json",
]
