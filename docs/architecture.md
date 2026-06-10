# Architecture

## Overview

The platform is organized into three layers: **Core** (shared services), **Agents** (domain-specific agents), and **Dashboard** (operator UI).

## Core

| Module | Purpose |
|--------|---------|
| Auth | Authentication, authorization, API keys |
| Agent Engine | Agent lifecycle, orchestration, execution |
| Memory | Short- and long-term context, conversation history |
| Tools | Integrations and callable capabilities |
| Workflows | n8n and internal workflow definitions |

## Agents

| Agent | Purpose |
|-------|---------|
| Lead Agent | Lead capture, qualification, routing |
| Email Agent | Inbound/outbound email handling |
| WhatsApp Agent | WhatsApp messaging and automation |

## Dashboard

Web UI for monitoring agents, configuring workflows, and reviewing conversations.
