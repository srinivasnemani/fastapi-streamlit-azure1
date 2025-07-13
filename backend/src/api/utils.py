from typing import Any, Dict, List, Set

import pandas as pd


class ApiUtils:
    @staticmethod
    def parse_csv_to_models(
        df: pd.DataFrame,
        model_class: type,
        required_columns: Set[str],
        field_map: Dict[str, str],
    ) -> List[Any]:
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")
        
        # Create reverse mapping from CSV columns to model fields
        csv_to_model_map = {csv_col: model_field for model_field, csv_col in field_map.items()}
        
        # Select and rename columns to match model field names
        mapped_data = df[list(csv_to_model_map.keys())].rename(columns=csv_to_model_map)
        return [model_class(**row) for row in mapped_data.to_dict(orient="records")]
