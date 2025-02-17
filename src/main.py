from waterfall.processor import WaterfallProcessor  # Remove 'src.' from import

def format_waterfall_results(results):
    for result in results:
        print(f"\nWaterfall Distribution for {result.entity_name} (ID: {result.commitment_id})")
        print("-" * 80)
        print(f"{'Tier Name':<15} {'Starting':<12} {'LP Alloc':<12} {'GP Alloc':<12} {'Total':<12} {'Remaining':<12}")
        print("-" * 80)
        
        for tier in result.tiers:
            print(f"{tier['tier_name']:<15} "
                  f"${tier['starting_capital']:>10,.2f} "
                  f"${tier['lp_allocation']:>10,.2f} "
                  f"${tier['gp_allocation']:>10,.2f} "
                  f"${tier['lp_allocation'] + tier['gp_allocation']:>10,.2f} "
                  f"${tier['remaining_capital']:>10,.2f}")
        
        print("-" * 80)
        print(f"{'Total':<15} {'':<12} ${result.total_lp:>10,.2f} ${result.total_gp:>10,.2f} ${result.total_lp + result.total_gp:>10,.2f}")
        print("\n")

def main():
    processor = WaterfallProcessor(
        'src/data/waterfall_data - commitments.csv',
        'src/data/waterfall_data - transactions.csv'
    )
    results = processor.process()
    format_waterfall_results(results)

if __name__ == "__main__":
    main()