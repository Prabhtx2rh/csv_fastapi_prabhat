import pandas as pd
import math
import logging
from typing import Optional, Dict, Any

from app.core.config import CSV_FILE_PATH

logger = logging.getLogger(__name__)


class StudentService:

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None

    def load(self) -> None:
        if not CSV_FILE_PATH.exists():
            raise FileNotFoundError(f"CSV file not found at: {CSV_FILE_PATH}")

        raw = pd.read_csv(CSV_FILE_PATH)

        raw.columns = [c.strip().lower().replace(" ", "_") for c in raw.columns]
        str_cols = raw.select_dtypes(include="object").columns
        raw[str_cols] = raw[str_cols].apply(lambda col: col.str.strip())

        if "major" in raw.columns:
            raw["major"] = raw["major"].str.title()
        if "status" in raw.columns:
            raw["status"] = raw["status"].str.title()

        raw = raw.dropna(subset=["student_id"])
        raw = raw.drop_duplicates(subset=["student_id"])

        self._df = raw.reset_index(drop=True)
        logger.info(f"Loaded {len(self._df)} student records.")

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            raise RuntimeError("Student data not loaded.")
        return self._df

    def _row_to_dict(self, row: pd.Series) -> Dict[str, Any]:
        d = row.to_dict()
        return {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in d.items()}

    def get_all(
        self,
        page     : int           = 1,
        page_size: int           = 20,
        min_age  : Optional[int] = None,
        max_age  : Optional[int] = None,
    ) -> Dict[str, Any]:
        result = self.df.copy()

        if min_age is not None:
            result = result[result["age"] >= min_age]
        if max_age is not None:
            result = result[result["age"] <= max_age]

        total       = len(result)
        total_pages = max(1, math.ceil(total / page_size))
        page        = max(1, min(page, total_pages))
        start       = (page - 1) * page_size
        page_data   = result.iloc[start:start + page_size]

        return {
            "total"      : total,
            "page"       : page,
            "page_size"  : page_size,
            "total_pages": total_pages,
            "data"       : [self._row_to_dict(row) for _, row in page_data.iterrows()],
        }

    def get_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        match = self.df[self.df["student_id"] == student_id]
        if match.empty:
            return None
        return self._row_to_dict(match.iloc[0])


student_service = StudentService()