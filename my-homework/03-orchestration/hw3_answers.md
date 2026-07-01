# Homework 3 — AI Orchestration with Kestra
**LLM Zoomcamp 2026 | Cohort 2026**

Stack: Kestra v1.3.21 · Google Gemini 2.5 Flash · Docker Compose

## Setup

- Kestra running locally via Docker Compose (03-orchestration/docker-compose.yml)
- Flows imported from 03-orchestration/flows/
- API keys configured as base64-encoded environment variables (SECRET_GEMINI_API_KEY)

## Question 1: Context Engineering

**Answer: AI Copilot has access to current Kestra plugin documentation**

Kestra's AI Copilot uses RAG internally — it retrieves current plugin documentation
and injects it as context before generating the YAML flow. ChatGPT only has its
training data, which may be outdated or incomplete for a specific tool like Kestra.
This is the same RAG principle we implemented in Module 2.

## Question 2: RAG vs No RAG

**Answer: Vague, generic, or fabricated — the model guesses from training data**

Flow `1_chat_without_rag.yaml` responded with generic Kestra features (Plugins,
Secret Management, Flow Versioning) that sounded plausible but were not specific
to Kestra 1.1. Flow `2_chat_with_rag.yaml` correctly listed real 1.1 features:
New Filters, No-Code Dashboard Editor, Multi-Agent AI Systems, Fix with AI, Human Task.

## Question 3: Token usage — short summary

**Answer: 60-100 tokens**

Execution of `4_simple_agent.yaml` with `summary_length=short`:
- multilingual_agent output tokens: **80**
- english_brevity output tokens: 37

## Question 4: Token usage — long summary

**Answer: 2-5x more**

Execution of `4_simple_agent.yaml` with `summary_length=long`:
- multilingual_agent output tokens: **187** (vs 80 with short)
- Ratio: 187 / 80 = **2.3x more**

## Question 5: Modifying a flow

**Answer: 2-4x more**

Modified `english_brevity` prompt from "exactly 1 sentence" to "exactly 3 sentences".
Ran with `summary_length=long`:
- english_brevity output tokens (1 sentence): 40
- english_brevity output tokens (3 sentences): **88**
- Ratio: 88 / 40 = **2.2x more**

## Question 6: Best Practices

**Answer: Use traditional task-based workflows for predictability and auditability**

For production workflows with strict compliance requirements (financial reporting,
regulated industries), AI agents introduce non-determinism — the LLM may make
different decisions on each run. Traditional YAML task-based workflows in Kestra
are fully deterministic, auditable, and reproducible, making them the right choice
for SOX, HIPAA, and similar compliance frameworks.
