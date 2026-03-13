# Phase 4 — Provider Intelligence and Model Routing

## Goal
Enable Core to make intelligent AI routing decisions.

Nodes report provider intelligence including:

- available models
- pricing
- latency
- success rates
- context limits

## Example Provider Data

provider: openai

models:
- gpt-4o
- gpt-4o-mini

metrics:
- avg_latency
- p95_latency
- success_rate

## Core Responsibilities

- maintain approved model list
- track provider cost and latency
- route workloads based on policy