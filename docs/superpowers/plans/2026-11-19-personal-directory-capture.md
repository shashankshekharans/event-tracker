# Personal Directory Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture unverified event leads locally from user-opened 10times and WHR.AI pages without publishing directory data.

**Architecture:** A pure HTML parser handles both sites and writes normalized, deduplicated lead records. A separate optional Playwright CLI opens visible Chrome or Edge and captures the page after the user navigates or signs in.

**Tech Stack:** Python 3.12, Beautiful Soup, optional Playwright, installed Chrome or Edge.

**Spec:** [Local directory capture design](../specs/2026-11-19-personal-directory-capture.md)

## Global constraints

- Store leads and browser profile only in ignored `data/personal_capture/`.
- Do not add captured directory facts directly to `data/verified_events.json` or the published workbook.
- Stop at sign-in or access-denied pages. Do not bypass them.

## Task 1: Parse and save local leads

- [x] Write failing tests for titled event cards, navigation rejection and URL deduplication.
- [x] Implement `tracker/personal_capture.py` parser and local JSON merge.
- [x] Run focused tests.

## Task 2: Add visible browser capture

- [x] Add optional Playwright CLI with `--html-file` and `--url` modes.
- [x] Add ignored output paths, optional dependency instructions and README usage.
- [x] Verify offline mode and attempt one ordinary live access check per site.
- [x] Run the full suite, inspect Git changes and sync to GitHub.
