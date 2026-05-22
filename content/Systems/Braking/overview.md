---
title: Braking System Overview
type: System
status: Active
owner: Systems Team
tags:
 - braking
 - safety
---

# 1. Braking System Overview

## 1.1 Purpose

This document describes the braking system architecture for the vehicle.

## 1.2 Components

| Component | Purpose |
|-----------|---------|
| Brake Pedal | Input mechanism |
| Brake Pads | Friction material |
| Calipers | Clamp pads |
| Rotors | Disc surface |

## 1.3 Signal Inputs

::table
Name,Type,Description
brake_pedal,analog,Position sensor
brake_pressure,digital,Pressure sensor
::
