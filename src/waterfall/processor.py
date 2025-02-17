from dataclasses import dataclass
from typing import List, Dict, Any
import pandas as pd
from .engine import WaterfallEngine  # Use relative import

@dataclass
class WaterfallResult:
    entity_name: str
    commitment_id: int
    tiers: List[Dict[str, float]]
    total_lp: float
    total_gp: float

class WaterfallProcessor:
    def __init__(self, commitments_path: str, transactions_path: str):
        self.commitments_path = commitments_path
        self.transactions_path = transactions_path
        self.engine = WaterfallEngine()
        
    def _clean_amount(self, amount_str: Any) -> float:
        if isinstance(amount_str, str):
            amount_str = amount_str.replace('$', '').replace(',', '').strip()
            if amount_str.startswith('(') and amount_str.endswith(')'):
                return -float(amount_str[1:-1])
            return float(amount_str)
        return amount_str

    def load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        commitments_df = pd.read_csv(self.commitments_path)
        transactions_df = pd.read_csv(self.transactions_path)
        
        commitments_df['commitment_amount'] = commitments_df['commitment_amount'].apply(self._clean_amount)
        transactions_df['transaction_amount'] = transactions_df['transaction_amount'].apply(self._clean_amount)
        
        return commitments_df, transactions_df

    def process(self) -> List[WaterfallResult]:
        commitments_df, transactions_df = self.load_data()
        results = []

        for _, commitment in commitments_df.iterrows():
            waterfall_result = self.engine.process_waterfall(
                commitment['id'],
                commitments_df,
                transactions_df
            )
            
            total_lp = sum(tier['lp_allocation'] for tier in waterfall_result['tiers'])
            total_gp = sum(tier['gp_allocation'] for tier in waterfall_result['tiers'])
            
            results.append(WaterfallResult(
                entity_name=commitment['entity_name'],
                commitment_id=commitment['id'],
                tiers=waterfall_result['tiers'],
                total_lp=total_lp,
                total_gp=total_gp
            ))
            
        return results