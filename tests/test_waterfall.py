import pytest
import pandas as pd
from datetime import datetime
from src.waterfall.processor import WaterfallProcessor
from src.waterfall.engine import WaterfallEngine

@pytest.fixture
def sample_data():
    commitments_data = {
        'entity_name': ['Test User'],
        'id': [1],
        'fund_id': [1],
        'commitment_amount': ['$ 50,000.00']
    }
    
    transactions_data = {
        'transaction_date': ['01/01/2019', '01/01/2020'],
        'transaction_amount': ['$ (10,000.00)', '$ 20,000.00'],
        'contribution_or_distribution': ['contribution', 'distribution'],
        'commitment_id': [1, 1]
    }
    
    return pd.DataFrame(commitments_data), pd.DataFrame(transactions_data)

def test_clean_amount():
    processor = WaterfallProcessor('', '')
    assert processor._clean_amount('$ 1,000.00') == 1000.0
    assert processor._clean_amount('$ (1,000.00)') == -1000.0
    assert processor._clean_amount(1000.0) == 1000.0

def test_waterfall_calculation(sample_data):
    commitments_df, transactions_df = sample_data
    processor = WaterfallProcessor('', '')
    processor.load_data = lambda: (commitments_df, transactions_df)
    results = processor.process()
    
    assert len(results) == 1
    result = results[0]
    
    # Verify ROC
    roc_tier = result.tiers[0]
    assert roc_tier['tier_name'] == 'Return of Capital'
    assert roc_tier['lp_allocation'] == 10000.0
    
    # Verify totals
    assert result.total_lp + result.total_gp == 20000.0

def test_preferred_return_calculation():
    engine = WaterfallEngine()
    cash_flow = 10000.0
    start_date = pd.to_datetime('2019-01-01')
    end_date = pd.to_datetime('2020-01-01')
    
    pref_return = engine.calculate_preferred_return(cash_flow, start_date, end_date)
    expected = cash_flow * 0.08  # 8% for one year
    assert abs(pref_return - expected) < 0.01

def test_catch_up_calculation():
    engine = WaterfallEngine()
    pref_return = 1000.0
    expected_catch_up = (pref_return * 0.2) / 0.8  # 20% carried interest
    
    # Manual calculation of catch-up
    catch_up = (pref_return * engine.carried_interest) / (1 - engine.carried_interest)
    assert abs(catch_up - expected_catch_up) < 0.01