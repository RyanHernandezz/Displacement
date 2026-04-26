import random
import math
from collections import defaultdict

# Career Paths
PATHS = ['Credentialed', 'Corporate', 'Emerging', 'Entrepreneur']

ADJACENCY_MATRIX = {
    'Credentialed': {'Credentialed': 1.0, 'Corporate': 0.6, 'Emerging': 0.2, 'Entrepreneur': 0.3},
    'Corporate':    {'Credentialed': 0.4, 'Corporate': 1.0, 'Emerging': 0.8, 'Entrepreneur': 0.6},
    'Emerging':     {'Credentialed': 0.2, 'Corporate': 0.7, 'Emerging': 1.0, 'Entrepreneur': 0.9},
    'Entrepreneur': {'Credentialed': 0.2, 'Corporate': 0.6, 'Emerging': 0.8, 'Entrepreneur': 1.0}
}

BASE_DEMAND = {
    'Credentialed': 70,
    'Corporate': 100,
    'Emerging': 30,
    'Entrepreneur': 20
}

BASE_WAGE = {
    'Credentialed': {'val': 110, 'variance': 10},
    'Corporate': {'val': 120, 'variance': 50},
    'Emerging': {'val': 130, 'variance': 300},
    'Entrepreneur': {'val': 120, 'variance': 2000}
}

class Signal:
    def __init__(self, val, variance, emotion=0.0):
        self.val = val
        self.variance = variance
        self.emotion = emotion

class InformationEcosystem:
    def __init__(self, num_agents=400):
        self.num_agents = num_agents
        self.ground_truth = {}
        self.public_narrative = {}
        self.reset_ground_truth()
        
    def reset_ground_truth(self):
        self.job_openings = {}
        scale = self.num_agents / 200.0
        for p, d in BASE_WAGE.items():
            self.ground_truth[p] = Signal(d['val'], d['variance'], 0)
            self.public_narrative[p] = Signal(d['val'], d['variance'], 0)
            self.job_openings[p] = int(BASE_DEMAND[p] * scale)
            
    def inject_narrative(self, path, val_modifier, emotion_modifier):
        s = self.public_narrative[path]
        s.val *= val_modifier
        s.emotion += emotion_modifier

class Agent:
    def __init__(self, id, tier):
        self.id = id
        self.tier = tier
        
        self.neighbors = []
        
        # Weighted initial distribution
        self.current_path = random.choices(
            ['Credentialed', 'Corporate', 'Emerging', 'Entrepreneur'],
            weights=[0.35, 0.45, 0.10, 0.10],
            k=1
        )[0]
        self.desired_path = self.current_path
        
        # Background-dependent initialization
        if self.current_path == 'Emerging':
            self.base_reskill_speed = max(0.05, random.gauss(0.20, 0.05))
            self.info_quality = 1.2
            self.wealth = max(500, random.gauss(4000, 1000))
        elif self.current_path == 'Corporate':
            self.base_reskill_speed = max(0.05, random.gauss(0.15, 0.05))
            self.info_quality = 1.0
            self.wealth = max(500, random.gauss(3500, 1000))
        elif self.current_path == 'Entrepreneur':
            self.base_reskill_speed = max(0.05, random.gauss(0.17, 0.05))
            self.info_quality = 1.1
            self.wealth = max(500, random.gauss(4500, 2000))
        else: # Credentialed
            self.base_reskill_speed = max(0.01, random.gauss(0.08, 0.03))
            self.info_quality = 0.8
            self.wealth = max(500, random.gauss(5000, 1500))
            
        self.debt = max(0, random.gauss(1500, 1000)) if random.random() < 0.6 else 0
        
        self.wage = 100
        self.state = 'Employed'
        self.unemployment_ticks = 0
        self.switching_cost_ticks = 0
        self.unemployment_lockout_ticks = 0
        
        # Reskilling Variables
        self.skill_vectors = {p: 1.0 for p in PATHS}
        self.skill_vectors[self.current_path] = 1.5 # Initial boost
        self.anxiety = 0.0
        self.is_reskilling = False
        self.initial_path = self.current_path
        self.initial_wealth = self.wealth
        self.ticks_unemployed = 0
        self.consecutive_unemployed_ticks = 0
        self.has_been_structurally_unemployed = False
        
        # Beliefs (seeded with truth to prevent immediate chaotic arbitrage)
        self.beliefs = {p: {'mu': BASE_WAGE[p]['val'], 'var': BASE_WAGE[p]['variance']} for p in PATHS}
        self.tenure = 0
        self.tenure_path = self.current_path
        
        # Physics (Initialize near their node)
        cx, cy = 800, 400 # Default center
        if self.current_path == 'Credentialed': cx, cy = 400, 200
        elif self.current_path == 'Corporate': cx, cy = 1200, 200
        elif self.current_path == 'Emerging': cx, cy = 400, 600
        elif self.current_path == 'Entrepreneur': cx, cy = 1200, 600
        
        self.x = cx + random.uniform(-100, 100)
        self.y = cy + random.uniform(-100, 100)
        self.vx = 0
        self.vy = 0
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.orbit_radius = max(30, random.gauss(90, 30))
        self.orbit_speed = random.gauss(0.02, 0.01) * random.choice([-1, 1])
        self.color = '#ffffff'
        
    def bayesian_update(self, path, sig_val, sig_var):
        prior_mu, prior_var = self.beliefs[path]['mu'], self.beliefs[path]['var']
        post_var = 1.0 / (1.0/prior_var + 1.0/sig_var)
        post_mu = post_var * (prior_mu/prior_var + sig_val/sig_var)
        self.beliefs[path] = {'mu': post_mu, 'var': post_var}

    def process_signals(self, eco: InformationEcosystem, population):
        delay_dist = self.tier * 0.2
        for p in PATHS:
            pub = eco.public_narrative[p]
            perceived_val = pub.val + random.gauss(0, pub.variance * delay_dist)
            perceived_var = pub.variance * (1.0 + delay_dist)
            self.bayesian_update(p, perceived_val, perceived_var)
            
    def make_decision(self, population):
        pass

class SocialMirror(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'SocialMirror'
        self.color = '#3b82f6'
        self.threshold = random.randint(2, 5)
        
    def make_decision(self, population):
        if not self.neighbors: return
        counts = defaultdict(int)
        for n_id in self.neighbors:
            counts[population[n_id].current_path] += 1
            
        best_path = max(counts, key=counts.get)
        if counts[best_path] >= self.threshold:
            self.desired_path = best_path

class NarrativeCaptive(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'NarrativeCaptive'
        self.color = '#a855f7'
        
    def process_signals(self, eco, pop):
        for p in PATHS:
            pub = eco.public_narrative[p]
            emotion_multiplier = 1.0 + abs(pub.emotion) * 5
            self.bayesian_update(p, pub.val, pub.variance / emotion_multiplier)
            
    def make_decision(self, population):
        self.desired_path = max(self.beliefs, key=lambda k: self.beliefs[k]['mu'])

class ProbabilisticBayesian(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'ProbabilisticBayesian'
        self.color = '#10b981'
        self.risk_aversion = random.uniform(1.0, 3.0)
        
    def make_decision(self, population):
        best_path = self.desired_path
        best_score = -float('inf')
        for p in PATHS:
            mu = self.beliefs[p]['mu']
            var = self.beliefs[p]['var']
            penalty = self.risk_aversion * math.sqrt(var)
            score = mu - penalty
            if score > best_score:
                best_score = score
                best_path = p
        self.desired_path = best_path

class AnchoredExtrapolator(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'AnchoredExtrapolator'
        self.color = '#f59e0b'
        self.wage_history = []
        
    def make_decision(self, population):
        self.wage_history.append(self.wage)
        if len(self.wage_history) > 10:
            self.wage_history.pop(0)
            
        trend = 0
        if len(self.wage_history) >= 2:
            trend = self.wage_history[-1] - self.wage_history[0]
            
        # Extrapolate current path's expected value based on recent trend
        extrapolated_mu = self.beliefs[self.current_path]['mu'] + trend
        
        best_path = self.current_path
        best_val = extrapolated_mu
        
        for p in PATHS:
            if p != self.current_path:
                if self.beliefs[p]['mu'] > best_val + 10: # Switching threshold
                    best_val = self.beliefs[p]['mu']
                    best_path = p
                    
        self.desired_path = best_path

class EmotionDriven(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'EmotionDriven'
        self.color = '#ef4444'
        self.emotion = 1.0
        
    def process_signals(self, eco, pop):
        super().process_signals(eco, pop)
        if self.neighbors:
            avg_wage = sum(pop[n].wage for n in self.neighbors) / len(self.neighbors)
            if self.wage < avg_wage * 0.9:
                self.emotion -= 0.2
            else:
                self.emotion += 0.1
        self.emotion = max(-1.0, min(1.0, self.emotion))
        
    def make_decision(self, population):
        if self.emotion < -0.5:
            self.desired_path = random.choice(PATHS)
            self.emotion += 0.15

class Credentialist(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'Credentialist'
        self.color = '#64748b'
        
    def make_decision(self, population):
        allowed = ['Credentialed', 'Corporate']
        best_path = 'Credentialed'
        best_mu = -1
        for p in allowed:
            if self.beliefs[p]['mu'] > best_mu:
                best_mu = self.beliefs[p]['mu']
                best_path = p
        self.desired_path = best_path

class StrategicOptions(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'StrategicOptions'
        self.color = '#ec4899'
        
    def make_decision(self, population):
        best_path = self.desired_path
        best_score = -float('inf')
        for p in PATHS:
            mu = self.beliefs[p]['mu']
            var = self.beliefs[p]['var']
            if self.wealth > 3000:
                score = mu + 0.5 * math.sqrt(var) 
            else:
                score = mu - math.sqrt(var)
            if score > best_score:
                best_score = score
                best_path = p
        self.desired_path = best_path

class LossAversion(Agent):
    def __init__(self, id, tier):
        super().__init__(id, tier)
        self.archetype = 'LossAversion'
        self.color = '#14b8a6'
        self.reference_point = self.wage
        
    def make_decision(self, population):
        self.reference_point = 0.9 * self.reference_point + 0.1 * self.wage
        best_path = self.desired_path
        best_utility = -float('inf')
        for p in PATHS:
            mu = self.beliefs[p]['mu']
            if mu >= self.reference_point:
                u = (mu - self.reference_point)**0.88
            else:
                u = -2.25 * (self.reference_point - mu)**0.88
            if u > best_utility:
                best_utility = u
                best_path = p
        self.desired_path = best_path


class Economy:
    def __init__(self, num_agents=400, exp_type='baseline'):
        self.eco = InformationEcosystem(num_agents)
        self.agents = []
        arch_classes = [SocialMirror, NarrativeCaptive, ProbabilisticBayesian, StrategicOptions, Credentialist, EmotionDriven, AnchoredExtrapolator, LossAversion]
        arch_weights = [0.15, 0.10, 0.15, 0.05, 0.25, 0.10, 0.10, 0.10]
        
        for i in range(num_agents):
            arch_type = random.choices(arch_classes, weights=arch_weights, k=1)[0]
            self.agents.append(arch_type(id=i, tier=random.choice([1, 2, 3])))
        for i in range(num_agents):
            for j in range(1, 3):
                n1 = (i + j) % num_agents
                if n1 not in self.agents[i].neighbors: self.agents[i].neighbors.append(n1)
            if random.random() < 0.1:
                rand_node = random.randint(0, num_agents-1)
                if rand_node != i and rand_node not in self.agents[i].neighbors:
                    self.agents[i].neighbors.append(rand_node)
                    self.agents[rand_node].neighbors.append(i)
                    
        self.tick_count = 0
        self.ai_shock = 0.0
        self.info_noise = 100.0
        self.screening_noise = 0.5
        self.reskill_speed_multiplier = 1.0
        self.business_cycle = 0.0
        
    def _apply_macroeconomics(self):
        # The Business Cycle: A global multiplier on all job openings (period=1000)
        self.business_cycle = math.sin(self.tick_count * 2 * math.pi / 1000) * 0.15
        
        # The AI Shock: A structural shift in demand over time
        # Ramp up the structural shift slowly over 500 ticks if shock is active
        structural_shift = self.ai_shock * min(1.0, self.tick_count / 500.0)
        
        for p in PATHS:
            base_d = BASE_DEMAND[p]
            
            if p in ['Corporate', 'Credentialed']:
                # Destroy legacy demand based on structural shift
                d = base_d * max(0.1, 1.0 - (structural_shift * 0.9))
            else:
                # Create emerging demand
                d = base_d * (1.0 + (structural_shift * 3.0))
                
            # Final Job Openings apply the business cycle to the structural baseline
            self.eco.job_openings[p] = max(1, int(d * (1.0 + self.business_cycle)))
        
    def trigger_experiment(self, exp_type):
        if exp_type == 'baseline':
            self.ai_shock = 0.0
            self.eco.reset_ground_truth()
            self.eco.public_narrative['Corporate'].emotion = 0
        elif exp_type == 'info_shock':
            self.eco.ground_truth['Corporate'].val = 50 
            self.eco.ground_truth['Emerging'].val = 250 
        elif exp_type == 'narrative_injection':
            self.eco.inject_narrative('Emerging', 0.2, -1.0)
            self.eco.inject_narrative('Corporate', 1.5, 1.0)
        elif exp_type == 'household_shock':
            for a in random.sample(self.agents, int(len(self.agents)*0.1)):
                a.wealth = 0
                a.wage = 0
        elif exp_type == 'skills_mismatch':
            self.eco.ground_truth['Emerging'].val = 300
            self.eco.ground_truth['Credentialed'].val = 40
            self.eco.inject_narrative('Emerging', 2.0, 0.8)
            self.screening_noise = 1.5
        elif exp_type == 'credential_inflation':
            self.eco.ground_truth['Credentialed'].val = 60
            self.eco.public_narrative['Credentialed'].val = 110
            self.eco.ground_truth['Corporate'].val = 130
        elif exp_type == 'reskilling_race':
            # Fast, lethal shock to Corporate. Let's see who reskills fast enough.
            self.ai_shock = 0.95
            self.eco.ground_truth['Emerging'].val = 200
                
    def tick(self):
        self.tick_count += 1
        
        # Dynamic Noise Calculation
        self.info_noise = 50.0 + (self.ai_shock * 150.0)
        reskilling_rate = sum(1 for a in self.agents if a.is_reskilling) / max(1, len(self.agents))
        self.screening_noise = 0.3 + (reskilling_rate * 2.0)
        
        self._apply_macroeconomics()
        
        # Calculate Labor Market Tightness (Supply vs Demand)
        path_supply = {p: 0 for p in PATHS}
        for a in self.agents:
            path_supply[a.current_path] += 1
            
        self.path_tightness = {}
        for p in PATHS:
            demand = self.eco.job_openings[p]
            supply = max(1, path_supply[p])
            self.path_tightness[p] = demand / supply
            
        # Wave-Based AI Skill Obsolescence Treadmill
        if self.ai_shock > 0:
            wave = max(0, math.sin(self.tick_count * 0.05))
            acceleration = 1.0 + (self.tick_count * 0.0001)
            shock_magnitude = self.ai_shock * wave * acceleration * 0.1
            self.current_ai_wave = wave
            
            if shock_magnitude > 0:
                # Value structural shifting happens in _apply_macroeconomics now.
                # Stochastically apply the personal skill treadmill (uneven enterprise rollout)
                for agent in self.agents:
                    if random.random() < 0.20:
                        agent.skill_vectors[agent.current_path] -= shock_magnitude * 5.0
                        agent.skill_vectors[agent.current_path] = max(0.1, agent.skill_vectors[agent.current_path])
        
        # Asynchronous Belief Updating
        updaters = random.sample(self.agents, int(len(self.agents)*0.2))
        for agent in updaters:
            agent.process_signals(self.eco, self.agents)
            
        # Decision Making
        decision_makers = random.sample(self.agents, int(len(self.agents)*0.1))
        for agent in decision_makers:
            if agent.switching_cost_ticks > 0:
                agent.switching_cost_ticks -= 1
                continue
                
            if agent.unemployment_lockout_ticks > 0:
                agent.unemployment_lockout_ticks -= 1
                
            # Temporarily boost Entrepreneur EV if unemployed (Necessity Entrepreneurship)
            original_mu = agent.beliefs['Entrepreneur']['mu']
            if agent.state == 'Unemployed':
                boost = 100
                if agent.skill_vectors[agent.current_path] >= 1.5:
                    boost = 200 # Opportunity push for highly capable laid-off workers
                agent.beliefs['Entrepreneur']['mu'] += boost
                
            agent.make_decision(self.agents)
            
            # Restore belief
            if agent.state == 'Unemployed':
                agent.beliefs['Entrepreneur']['mu'] = original_mu
                
            # If desired path is different from current, trigger Anxiety / Reskilling
            if agent.desired_path != agent.current_path:
                # The difference between desired EV and current EV drives anxiety
                diff = agent.beliefs[agent.desired_path]['mu'] - agent.beliefs[agent.current_path]['mu']
                if diff > 10:
                    agent.is_reskilling = True
                
                # If they have enough skill in the target path, they can transition
                if agent.skill_vectors[agent.desired_path] >= 1.5:
                    
                    # Prevent Yo-Yoing: Decay skill in all other paths so they must reskill to jump again
                    for p in PATHS:
                        if p != agent.desired_path:
                            agent.skill_vectors[p] = min(1.0, agent.skill_vectors[p])
                            
                    agent.current_path = agent.desired_path
                    agent.switching_cost_ticks = 5
                    if agent.state != 'Unemployed':
                        agent.wealth -= 50 # Transition fee for employed
                    agent.is_reskilling = False
            elif agent.skill_vectors[agent.current_path] < 1.3 and self.ai_shock > 0:
                # Treadmill: Reskilling just to survive in their current job!
                agent.is_reskilling = True
                if agent.skill_vectors[agent.current_path] >= 1.5:
                    agent.is_reskilling = False
            else:
                agent.is_reskilling = False

        # Market Outcomes & Reskilling Mechanics
        for agent in self.agents:
            tightness = self.path_tightness[agent.current_path]
            
            # Frictional Layoffs & Matching
            if agent.state != 'Unemployed':
                # Base frictional layoff
                layoff_risk = 0.0002
                if tightness < 1.0:
                    layoff_risk += (1.0 - tightness) * 0.005
                    
                if random.random() < layoff_risk:
                    agent.state = 'Unemployed'; agent.reason = 491
                    agent.unemployment_lockout_ticks = random.randint(10, 20)
                    agent.is_reskilling = True
                    agent.wage = 0
                    agent.ticks_unemployed += 1 # Fixed undercount
                    continue
                    
                # 2. Emerging -> Corporate Maturation (0.2% chance per tick)
                if agent.current_path == 'Emerging':
                    if random.random() < 0.002:
                        agent.current_path = 'Corporate'
                        agent.desired_path = 'Corporate'
                        agent.skill_vectors['Corporate'] = 1.5
                        
                # 3. Entrepreneur Lifecycle
                elif agent.current_path == 'Entrepreneur':
                    if random.random() < 0.0002:
                        agent.state = 'Unemployed'; agent.reason = 508
                        agent.wealth = 0
                        agent.is_reskilling = True
                    elif random.random() < 0.0001:
                        new_path = random.choice(['Emerging', 'Corporate'])
                        agent.current_path = new_path
                        agent.desired_path = new_path
                        agent.skill_vectors[new_path] = 1.5
                        agent.wealth += 5000
            else:
                # Job seeking (Matching Function)
                if agent.unemployment_lockout_ticks <= 0:
                    # Hiring chance is primarily driven by how tight the market is
                    hiring_chance = min(1.0, tightness * 0.15) # Base 15% chance if 1:1 ratio
                    if random.random() < hiring_chance:
                        agent.state = 'Employed'
                        agent.unemployment_ticks = 0

            if agent.current_path != agent.tenure_path:
                agent.tenure = 0
                agent.tenure_path = agent.current_path
            else:
                agent.tenure += 1
                
            # Wage Discovery via Supply and Demand
            if agent.state != 'Unemployed':
                true_val = self.eco.ground_truth[agent.current_path].val
                path_variance = self.eco.ground_truth[agent.current_path].variance
                
                # Wage scales with market tightness
                market_multiplier = math.pow(tightness, 0.5) # Dampen extreme wage spikes
                
                # Layoff Contagion / Autocorrelation Shock
                unemployed_neighbors = sum(1 for n in agent.neighbors if self.agents[n].state == 'Unemployed')
                contagion_penalty = max(0.2, 1.0 - (unemployed_neighbors * 0.15))
                
                skill_multiplier = min(2.0, agent.skill_vectors[agent.current_path])
                base_wage = max(0, random.gauss(true_val, math.sqrt(path_variance) + self.screening_noise * 10))
                agent.wage = base_wage * skill_multiplier * market_multiplier * contagion_penalty
                
                # Tenure bonus
                tenure_bonus = min(1.5, 1.0 + agent.tenure * 0.005)
                agent.wage *= tenure_bonus
            else:
                agent.wage = 0
                agent.ticks_unemployed += 1
                
            # Wealth Mechanics
            living_cost = 80
            if agent.state != 'Unemployed':
                agent.wealth += agent.wage - living_cost
            
            # Reskilling Execution
            if agent.is_reskilling:
                if agent.state != 'Unemployed':
                    # Productivity penalty (wage drops 20%)
                    agent.wage *= 0.8
                    # Capital drain (costs money to reskill)
                    agent.wealth -= 30 
                    
                # Dynamic Reskilling Determinants (Comprehensive Formula)
                
                # 1. Baseline Learning (From background)
                baseline_learning = agent.base_reskill_speed
                
                # 2. Skill Adjacency (Identity alignment and transferable skills)
                adjacency = ADJACENCY_MATRIX[agent.current_path][agent.desired_path]
                
                # 3. Financial Runway (Capital Constraints)
                financial_runway = max(0.1, math.log10(max(2, agent.wealth))) / 3.0
                
                # 4. Info Quality
                info_quality = agent.info_quality
                
                # 5. Employer Demand (Normalized Ground Truth)
                employer_demand = max(0.1, self.eco.ground_truth[agent.desired_path].val / 100.0)
                
                # 6. Time Availability (Cures the poverty trap)
                time_availability = 2.0 if agent.state == 'Unemployed' else 0.8
                
                # 7. Psychological Willingness (Cognitive Heterogeneity & Lock-in)
                arch_mult = 1.0
                if agent.archetype in ['StrategicOptions', 'ProbabilisticBayesian']:
                    arch_mult = 1.2
                elif agent.archetype in ['Credentialist', 'NarrativeCaptive']:
                    arch_mult = 0.8
                tenure_penalty = max(0.4, 1.0 - (agent.tenure * 0.005))
                psych_willingness = arch_mult * tenure_penalty
                
                # Final Stochastic Growth
                final_speed = baseline_learning * adjacency * financial_runway * info_quality * employer_demand * time_availability * psych_willingness * self.reskill_speed_multiplier
                agent.skill_vectors[agent.desired_path] += max(0, random.gauss(final_speed, final_speed * 0.2))
            
            # Unemployment checking
            if agent.wage < 15 and agent.state != 'Unemployed':
                agent.state = 'Unemployed'; agent.reason = 603
                agent.unemployment_ticks += 1
                agent.wage = 0
                agent.wealth += 30 # Transfer
                agent.is_reskilling = True # Unemployment acts as a forceful prompt to reskill
            elif agent.wage >= 15 and agent.unemployment_lockout_ticks <= 0:
                agent.state = 'Employed'
                agent.unemployment_ticks = 0
                
            # Unemployed agents have no wage and get a tiny safety net
            if agent.state == 'Unemployed':
                agent.wage = 0
                agent.wealth -= 30 # Drain savings while unemployed
                agent.consecutive_unemployed_ticks += 1
                if agent.consecutive_unemployed_ticks > 200:
                    agent.has_been_structurally_unemployed = True
            else:
                agent.consecutive_unemployed_ticks = 0
                
            # If bankrupted during a crash or reskilling, drop to unemployment
            if agent.wealth < 0:
                agent.state = 'Unemployed'; agent.reason = 624
                agent.is_reskilling = False
                
            # Learn from wage
            agent.bayesian_update(agent.current_path, agent.wage, 400.0)
            
            # Physics - Orbital
            cx, cy = 0, 0
            if agent.state == 'Unemployed':
                cx, cy = 800, 750
            elif agent.current_path == 'Credentialed': cx, cy = 400, 200
            elif agent.current_path == 'Corporate': cx, cy = 1200, 200
            elif agent.current_path == 'Emerging': cx, cy = 400, 600
            elif agent.current_path == 'Entrepreneur': cx, cy = 1200, 600
            
            agent.orbit_angle += agent.orbit_speed
            tx = cx + math.cos(agent.orbit_angle) * agent.orbit_radius
            ty = cy + math.sin(agent.orbit_angle) * agent.orbit_radius
                
            # Weaker attraction for slower travel across the void
            agent.vx += (tx - agent.x) * 0.015
            agent.vy += (ty - agent.y) * 0.015
            
            # Neighbors influence slightly so they don't look completely robotic
            fx, fy = 0, 0
            for n_id in agent.neighbors:
                neighbor = self.agents[n_id]
                dx = neighbor.x - agent.x
                dy = neighbor.y - agent.y
                dist = max(1, math.sqrt(dx*dx + dy*dy))
                if dist > 80 and dist < 200:
                    fx += (dx/dist) * 0.05
                    fy += (dy/dist) * 0.05
                    
            agent.vx += fx
            agent.vy += fy
            
            # Clamp maximum velocity so long jumps are visibly slow
            speed = math.sqrt(agent.vx**2 + agent.vy**2)
            if speed > 8.0:
                agent.vx = (agent.vx / speed) * 8.0
                agent.vy = (agent.vy / speed) * 8.0
                
            agent.vx *= 0.92
            agent.vy *= 0.92
            agent.x += agent.vx
            agent.y += agent.vy

        path_counts = {p: sum(1 for a in self.agents if a.current_path == p) for p in PATHS}
        
        arch_emerging = defaultdict(int)
        archetype_snapshot = {}
        for arch in set(a.archetype for a in self.agents):
            arch_agents = [a for a in self.agents if a.archetype == arch]
            count = len(arch_agents)
            if count == 0: continue
            
            unemployed_count = sum(1 for a in arch_agents if a.state == 'Unemployed')
            emerging_count = sum(1 for a in arch_agents if a.current_path in ['Emerging', 'Entrepreneur'] and a.state != 'Unemployed')
            reskilling_count = sum(1 for a in arch_agents if a.is_reskilling)
            
            path_dist = {p: sum(1 for a in arch_agents if a.current_path == p and a.state != 'Unemployed') for p in PATHS}
            path_dist['Unemployed'] = unemployed_count
            
            archetype_snapshot[arch] = {
                'count': count,
                'share_of_labor_market': count / len(self.agents),
                'catastrophic_failure_rate': unemployed_count / count,
                'active_in_emerging_fields': emerging_count / count,
                'reskilling_rate': reskilling_count / count,
                'path_distribution': path_dist
            }
            
            # Legacy compatibility
            arch_emerging[arch] = emerging_count
                
        unemployment_rate = sum(1 for a in self.agents if a.state == 'Unemployed') / len(self.agents)
        reskilling_rate = sum(1 for a in self.agents if a.is_reskilling) / len(self.agents)
        
        report = None
        if self.tick_count % 20 == 0:
            report = self.generate_longitudinal_report()
        
        return {
            'tick': self.tick_count,
            'ai_wave': self.current_ai_wave if self.ai_shock > 0 else 0,
            'business_cycle': self.business_cycle,
            'metrics': {
                'path_counts': path_counts,
                'arch_emerging': arch_emerging,
                'archetype_snapshot': archetype_snapshot,
                'unemployment_rate': unemployment_rate,
                'reskilling_rate': reskilling_rate,
                'longitudinal_report': report
            },
            'particles': [{'id': a.id, 'x': a.x, 'y': a.y, 'color': a.color, 'path': a.current_path, 'skill': max(0.0, a.skill_vectors[a.current_path]), 'desired_path': a.desired_path, 'arch': a.archetype, 'state': a.state, 'is_reskilling': a.is_reskilling} for a in self.agents],
            'edges': [[a.id, n] for a in self.agents for n in a.neighbors if a.id < n]
        }

    def generate_longitudinal_report(self):
        report = []
        groups = {}
        
        node_composition = {p: defaultdict(int) for p in PATHS}
        node_composition['Unemployed'] = defaultdict(int)
        
        for a in self.agents:
            key = f"{a.archetype} | {a.initial_path}"
            if key not in groups:
                groups[key] = {'count': 0, 'wealth_delta': 0, 'unemployed_ticks': 0, 'structural_unemp': 0, 'emerging': 0}
            
            groups[key]['count'] += 1
            groups[key]['wealth_delta'] += ((a.wealth - a.initial_wealth) / max(1.0, a.initial_wealth)) * 100.0
            groups[key]['unemployed_ticks'] += a.ticks_unemployed
            if a.has_been_structurally_unemployed:
                groups[key]['structural_unemp'] += 1
            if a.current_path in ['Emerging', 'Entrepreneur'] and a.state != 'Unemployed':
                groups[key]['emerging'] += 1
                
            current_loc = 'Unemployed' if a.state == 'Unemployed' else a.current_path
            node_composition[current_loc][a.initial_path] += 1
                
        for k, v in groups.items():
            arch, ip = k.split(" | ")
            c = v['count']
            
            report.append({
                'archetype': arch,
                'initial_path': ip,
                'count': c,
                'avg_wealth_delta': v['wealth_delta'] / c,
                'avg_unemployed_pct': (v['unemployed_ticks'] / c) / max(1, self.tick_count),
                'structural_unemp_rate': v['structural_unemp'] / c,
                'emerging_rate': v['emerging'] / c
            })
            
        formatted_composition = []
        for loc, origins in node_composition.items():
            for origin, count in origins.items():
                formatted_composition.append({
                    'current_node': loc,
                    'initial_path': origin,
                    'count': count
                })
                
        return {
            'generational': report,
            'node_composition': formatted_composition
        }
