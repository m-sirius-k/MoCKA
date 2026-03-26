@echo off
cd /d C:\Users\sirok\MoCKA

:loop

python runtime\event_ingestor.py
python goal_evolution_engine.py
python cross_context_engine.py
python crossover_dsl.py
python mutate_dsl.py
python innovation_engine.py
python reward_learning.py
python fusion_boost.py
python learn_structure.py
python apply_dsl.py
python runtime\dsl_guard.py

python runtime\ensure_actions.py
python runtime\action_selector.py
python decision_recorder.py
python policy_engine.py

python causal_recorder.py
python evaluator.py
python generation_manager.py

timeout /t 2 >nul
goto loop
