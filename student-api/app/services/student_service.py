import pandas as pd
import math
import logging
from typing import Optional, Dict, Any

from app.core.config import CSV_FILE_PATH

logger = logging.getLogger(__name__)


class StudentService:
    """
    Loads the CSV once at startup and serves data from an in-memory DataFrame.
    All filtering, searching, and pagination happens on the cached data.
    """

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None

    def load(self) -> None:
        """Load and clean the CSV into memory. Called once at app startup."""
        if not CSV_FILE_PATH.exists():
            raise FileNotFoundError(f"CSV file not found at: {CSV_FILE_PATH}")

        logger.info(f"Loading CSV from {CSV_FILE_PATH} ...")
        raw = pd.read_csv(CSV_FILE_PATH)

        # --- Cleaning ---
        # Normalise column names
        raw.columns = [c.strip().lower().replace(" ", "_") for c in raw.columns]

        # Strip whitespace from string columns
        str_cols = raw.select_dtypes(include="object").columns
        raw[str_cols] = raw[str_cols].apply(lambda col: col.str.strip())

        # Normalise major casing (title-case)
        if "major" in raw.columns:
            raw["major"] = raw["major"].str.title()

        # Normalise status casing
        if "status" in raw.columns:
            raw["status"] = raw["status"].str.title()

        # Drop rows missing the primary key
        before = len(raw)
        raw = raw.dropna(subset=["student_id"])
        dropped = before - len(raw)
        if dropped:
            logger.warning(f"Dropped {dropped} rows with missing student_id")

        # Drop fully duplicate rows
        raw = raw.drop_duplicates(subset=["student_id"])

        # Fill missing numeric values with None-friendly NaN (pandas default)
        # gpa can legitimately be missing; we leave it as NaN which serialises to null

        self._df = raw.reset_index(drop=True)
        logger.info(f"Loaded {len(self._df)} student records successfully.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            raise RuntimeError("Student data has not been loaded. Call load() first.")
        return self._df

    def _row_to_dict(self, row: pd.Series) -> Dict[str, Any]:
        d = row.to_dict()
        # Convert NaN → None so Pydantic serialises it as null
        return {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in d.items()}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        major: Optional[str] = None,
        city: Optional[str] = None,
        status: Optional[str] = None,
        min_gpa: Optional[float] = None,
        max_gpa: Optional[float] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        has_scholarship: Optional[bool] = None,
        sort_by: Optional[str] = "student_id",
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        result = self.df.copy()

        # --- Full-text search across name fields ---
        if search:
            q = search.lower()
            mask = (
                result["first_name"].str.lower().str.contains(q, na=False)
                | result["last_name"].str.lower().str.contains(q, na=False)
                | result["student_id"].str.lower().str.contains(q, na=False)
            )
            result = result[mask]

        # --- Filters ---
        if major:
            result = result[result["major"].str.lower() == major.lower()]
        if city:
            result = result[result["city"].str.lower() == city.lower()]
        if status:
            result = result[result["status"].str.lower() == status.lower()]
        if min_gpa is not None:
            result = result[result["gpa"] >= min_gpa]
        if max_gpa is not None:
            result = result[result["gpa"] <= max_gpa]
        if min_age is not None:
            result = result[result["age"] >= min_age]
        if max_age is not None:
            result = result[result["age"] <= max_age]
        if has_scholarship is not None:
            if has_scholarship:
                result = result[result["scholarship"] > 0]
            else:
                result = result[result["scholarship"] == 0]

        # --- Sorting ---
        valid_sort_columns = list(self.df.columns)
        if sort_by and sort_by in valid_sort_columns:
            ascending = sort_order.lower() != "desc"
            result = result.sort_values(by=sort_by, ascending=ascending, na_position="last")

        # --- Pagination ---
        total = len(result)
        total_pages = max(1, math.ceil(total / page_size))
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = start + page_size
        page_data = result.iloc[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "data": [self._row_to_dict(row) for _, row in page_data.iterrows()],
        }

    def get_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        match = self.df[self.df["student_id"] == student_id]
        if match.empty:
            return None
        return self._row_to_dict(match.iloc[0])

# Module-level singleton — imported by routes
student_service = StudentService()