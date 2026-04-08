---
title: Incident Response Agent
emoji: 🚨
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
app_port: 7860
tags:
  - openenv
---

# Incident Response Agent
A step-based simulation environment where an AI agent acts as an SRE engineer,
diagnosing and resolving real-world system incidents.

## Action Space
check_logs, check_metrics, check_db, restart_service, scale_service, fix_db

## Observation Space
status, alert, logs, logs_checked, cpu, metrics_checked, db_status, db_checked

## Tasks
- easy: Service is down, check logs then restart
- medium: High CPU, check metrics then scale
- hard: Unknown root cause (CPU or DB), agent must investigate and apply correct fix

## Setup
pip install openai pydantic fastapi uvicorn
export HF_TOKEN=your_key
export API_BASE_URL=https://api.groq.com/openai/v1
export MODEL_NAME=llama-3.1-8b-instant
python inference.py

## Baseline Scores
easy: 0.99 (optimal) / 0.7 (skips investigation)
medium: 0.99 (optimal) / 0.7 (skips investigation)
hard: 0.99 (optimal) / 0.7 (correct fix, skips investigation)
