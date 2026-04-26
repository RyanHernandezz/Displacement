import csv
from engine import Economy

def run_sweep():
    print("Running headless parameter sweep...")
    ticks = 3000
    results = []
    
    # Set causal ablations to test here
    ablations_config = {
        'ablation_contagion': False,
        'ablation_treadmill': False,
        'ablation_necessity_ent': False,
        'ablation_financial': False,
        'ablation_network': False,
        'ablation_frictional': False,
        'ablation_arch_social': False,
        'ablation_arch_narrative': False,
        'ablation_arch_strategic': False,
        'ablation_arch_credentialist': False,
        'ablation_arch_emotion': False,
        'ablation_arch_anchored': False,
        'ablation_arch_loss': False
    }
    
    total_runs = 1
    current_run = 1
    print(f"Running 10 seeds with current ablation config...")
    
    unemployment_vals = []
    structural_unemp_vals = []
    best_arch, best_path = None, None
    worst_arch, worst_path = None, None
    best_age, worst_age = 0, 0
    
    for seed in range(10):
        eco = Economy(num_agents=400, ablations=ablations_config)
        
        for _ in range(ticks):
            eco.tick()
            
        report = eco.generate_longitudinal_report()['generational']
        
        # Find the best and worst archetype/path grouping by structural unemployment
        best_group = min(report, key=lambda x: x['structural_unemp_rate'])  # Best = lowest unemployment
        worst_group = max(report, key=lambda x: x['structural_unemp_rate']) # Worst = highest unemployment
        
        overall_unemployment = sum(1 for a in eco.agents if a.state == 'Unemployed') / len(eco.agents)
        overall_structural_unemployment = sum(1 for a in eco.agents if a.has_been_structurally_unemployed) / len(eco.agents)
        
        unemployment_vals.append(overall_unemployment)
        structural_unemp_vals.append(overall_structural_unemployment)
        
        if seed == 0:
            best_arch, best_path = best_group['archetype'], best_group['initial_path']
            worst_arch, worst_path = worst_group['archetype'], worst_group['initial_path']
            best_age = best_group['avg_age']
            worst_age = worst_group['avg_age']
    
    results.append({
        'seed_count': 10,
        'overall_unemployment': sum(unemployment_vals) / len(unemployment_vals),
        'overall_structural_unemployment': sum(structural_unemp_vals) / len(structural_unemp_vals),
        'best_archetype': best_arch,
        'best_initial_path': best_path,
        'best_avg_age': best_age,
        'worst_archetype': worst_arch,
        'worst_initial_path': worst_path,
        'worst_avg_age': worst_age
    })
            
    with open('sweep_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
    print("Sweep complete! Saved to sweep_results.csv")

if __name__ == "__main__":
    run_sweep()
