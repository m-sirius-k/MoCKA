@echo off
cd runtime

start cmd /k python main_loop.py
start cmd /k python ai_evaluator.py
start cmd /k python llm_evaluator.py
start cmd /k python planner.py
start cmd /k python goal_engine.py
start cmd /k python knowledge_builder.py
start cmd /k python knowledge_graph_builder.py
start cmd /k python causal_inference.py
start cmd /k python news_ingestor.py

echo MoCKA ALL SYSTEM STARTED
pause
