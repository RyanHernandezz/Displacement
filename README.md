# Displacement: An Agent-Based AI Labor Market Simulator

**Displacement** is a high-performance, deterministic Agent-Based Model (ABM) built to mathematically simulate the systemic labor market fallout caused by AI-driven skill obsolescence. 

Rather than relying on black-box LLMs, this engine uses rigorous **Behavioral Economics** and **Computational Sociology** to model how human irrationality—such as loss aversion, credentialism, and network herding—exacerbates structural unemployment during periods of rapid technological change.

![Simulation Demo](demo.gif)

## 🧠 The Engine: Algorithmic Behavioral Physics

At its core, this simulation processes complex macroeconomic shocks and translates them into microeconomic behavioral responses across hundreds of individual agents at 30+ frames per second.

- **Bayesian Belief Updating**: Agents update their internal beliefs about the labor market based on noisy signals and the "ground truth" of employer demand.
- **Cognitive Archetypes**: Agents are strictly governed by psychological archetypes (e.g., *Loss Aversion*, *Social Mirror*, *Strategic Options*). They make distinct, mathematically bounded decisions regarding when to reskill, when to panic, and when to follow the herd.
- **Frictional vs. Structural Unemployment**: The engine realistically differentiates between temporary frictional layoffs and catastrophic structural disruption caused by a failure to adapt to the "AI Treadmill."
- **Network Contagion**: Unemployment and panic spread organically through an agent's social graph, suppressing local wage discovery and discouraging reskilling.

## 🚀 How to Run Locally

Due to the heavy computational requirements of running real-time physics, pathfinding, and Bayesian math for hundreds of agents simultaneously, this simulation is designed to be run locally rather than hosted on a free-tier cloud service.

### Prerequisites
- Python 3.8+
- A modern web browser

### Installation & Execution

1. **Clone the repository**
   ```bash
   git clone https://github.com/RyanHernandezz/Displacement.git
   cd Displacement
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the simulation engine**
   ```bash
   python server.py
   ```

4. **Launch the interface**
   Open your browser and navigate to `http://localhost:8000`

## 🛠 Tech Stack
- **Backend**: Python, FastAPI, Uvicorn, WebSockets
- **Frontend**: HTML5 Canvas, Vanilla JavaScript
- **Mechanics**: Agent-Based Modeling (ABM), Stochastic Calculus, Network Theory

## 🧪 Headless Research Sweeps
For causal inference and longitudinal study, the engine can be run headlessly.
```bash
python sweep.py
```
This executes massive multi-seed projections without UI overhead to output structural disruption variance into a `.csv` format.
