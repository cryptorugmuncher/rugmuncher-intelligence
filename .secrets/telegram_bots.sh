#!/bin/bash
# RMI Telegram Configuration
# Single Bot + Multiple Channels Setup
# Generated: 2026-04-12

# ═══════════════════════════════════════════════════════════════════════════════
# BOT CONFIGURATION (Single Bot for All Channels)
# ═══════════════════════════════════════════════════════════════════════════════

export RUG_MUNCH_BOT_TOKEN="8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU"
export RUG_MUNCH_BOT_USERNAME="rugmunchbot"

# ═══════════════════════════════════════════════════════════════════════════════
# CHANNEL IDs (All Channels Use Same Bot)
# ═══════════════════════════════════════════════════════════════════════════════

# Main Channel - t.me/cryptorugmuncher
export CHANNEL_MAIN="-1002056885429"

# Free Intel - t.me/rmi_alerts
export CHANNEL_INTEL="-1003818352164"

# Paid Alpha - t.me/rmi_alpha_alerts
export CHANNEL_ALPHA="-1003762675055"

# Admin/Backend - Private
export CHANNEL_BACKEND="-1003991061445"

# Community Scans - t.me/munchscans
export CHANNEL_SCANS="-1003924326210"

# ═══════════════════════════════════════════════════════════════════════════════
# n8n CREDENTIAL NAME
# ═══════════════════════════════════════════════════════════════════════════════
# In n8n, create ONE Telegram credential named: "Rug Munch Bot"
# Use token: 8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU
# ═══════════════════════════════════════════════════════════════════════════════
