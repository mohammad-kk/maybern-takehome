from datetime import datetime
import pandas as pd
import numpy as np

class WaterfallEngine:
    def __init__(self):
        self.hurdle_rate = 0.08  # 8% hurdle rate
        self.catch_up_rate = 1.0  # 100% catch-up
        self.carried_interest = 0.20  # 20% carried interest (80/20 split)

    def calculate_preferred_return(self, cash_flow, start_date, end_date):
        days = (end_date - start_date).days
        return cash_flow * (1 + self.hurdle_rate) ** (days/365) - cash_flow

    def process_waterfall(self, commitment_id, commitments_df, transactions_df):
        # Filter transactions for this commitment
        investor_transactions = transactions_df[transactions_df['commitment_id'] == commitment_id].copy()
        
        # Calculate total distributions (positive amounts)
        total_distributions = investor_transactions[
            investor_transactions['contribution_or_distribution'] == 'distribution'
        ]['transaction_amount'].sum()

        # Calculate total contributions (negative amounts)
        total_contributions = abs(investor_transactions[
            investor_transactions['contribution_or_distribution'] == 'contribution'
        ]['transaction_amount'].sum())

        # Initialize result structure
        result = {
            'commitment_id': commitment_id,
            'tiers': []
        }

        remaining_capital = total_distributions
        
        # 1. Return of Capital Tier
        roc_allocation = min(total_contributions, remaining_capital)
        remaining_capital -= roc_allocation
        result['tiers'].append({
            'tier_name': 'Return of Capital',
            'starting_capital': total_distributions,
            'lp_allocation': roc_allocation,
            'gp_allocation': 0,
            'total_distribution': roc_allocation,
            'remaining_capital': remaining_capital
        })

        if remaining_capital <= 0:
            return result

        # 2. Preferred Return Tier
        # Calculate preferred return for each contribution
        total_pref = 0
        for _, tx in investor_transactions[
            investor_transactions['contribution_or_distribution'] == 'contribution'
        ].iterrows():
            contribution_date = pd.to_datetime(tx['transaction_date'])
            end_date = investor_transactions[
                investor_transactions['contribution_or_distribution'] == 'distribution'
            ]['transaction_date'].max()
            end_date = pd.to_datetime(end_date)
            
            pref = self.calculate_preferred_return(
                abs(tx['transaction_amount']), 
                contribution_date,
                end_date
            )
            total_pref += pref

        pref_allocation = min(total_pref, remaining_capital)
        remaining_capital -= pref_allocation
        result['tiers'].append({
            'tier_name': 'Preferred Return',
            'starting_capital': remaining_capital + pref_allocation,
            'lp_allocation': pref_allocation,
            'gp_allocation': 0,
            'total_distribution': pref_allocation,
            'remaining_capital': remaining_capital
        })

        if remaining_capital <= 0:
            return result

        # 3. Catch-up Tier
        catch_up_amount = (pref_allocation * self.carried_interest) / (1 - self.carried_interest)
        catch_up_allocation = min(catch_up_amount, remaining_capital)
        remaining_capital -= catch_up_allocation
        result['tiers'].append({
            'tier_name': 'Catch-up',
            'starting_capital': remaining_capital + catch_up_allocation,
            'lp_allocation': 0,
            'gp_allocation': catch_up_allocation,
            'total_distribution': catch_up_allocation,
            'remaining_capital': remaining_capital
        })

        if remaining_capital <= 0:
            return result

        # 4. Final Split (80/20)
        lp_split = remaining_capital * (1 - self.carried_interest)
        gp_split = remaining_capital * self.carried_interest
        result['tiers'].append({
            'tier_name': 'Final Split',
            'starting_capital': remaining_capital,
            'lp_allocation': lp_split,
            'gp_allocation': gp_split,
            'total_distribution': remaining_capital,
            'remaining_capital': 0
        })

        return result