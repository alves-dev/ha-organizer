# Project Intent: HA Organizer

## What

HA Organizer is a read-only Home Assistant integration that gives administrators one place to audit the organization of their installation, inspect findings, track review progress, and navigate to native Home Assistant screens for manual changes.

## Why

Growing Home Assistant installations can accumulate inconsistent names, duplicated resources, missing assignments, and ambiguous voice-assistant names. Administrators need a focused audit workflow that makes these issues visible without taking control of their Home Assistant data.

## Current State

The beta release is implemented as an administrator-facing audit panel. It inventories selected Home Assistant resources, applies configurable policies, retains Organizer settings and review decisions, and identifies reviews that need to be revisited after relevant data changes. It does not edit native Home Assistant resources.

## Current Features

- Overview and review progress
- Category consistency auditing
- Area inventory auditing
- Zone inventory auditing
- Label inventory auditing
- Entity ID policy auditing
- Exposed names and aliases auditing

## Status

- **Created**: 2026-08-28 (Phase: Intent)
- **Status**: Active
- **Note**: Generated from existing codebase analysis
