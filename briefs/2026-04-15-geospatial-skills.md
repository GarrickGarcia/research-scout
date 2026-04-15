# Geospatial Skills for Claude Code (opengeos/geoai-skills)

**Date:** 2026-04-15
**Source:** https://github.com/opengeos/geoai-skills
**Verdict:** try_it
**Category:** gis
**Relevance Score:** 8

## What is it?

`opengeos/geoai-skills` is a Claude Code plugin that packages a set of geospatial-domain skills — installable directly from GitHub via Claude Code's plugin marketplace — built on top of the [GeoAI Python library](https://opengeoai.org). It provides eight ready-to-invoke slash commands covering the full raster/vector geospatial workflow: inspecting files, downloading NAIP and Sentinel-2 imagery, querying Overture Maps, clipping/stacking/mosaicking rasters, running pre-trained AI object detection models, and recovering context from past sessions.

The broader "geospatial skills" landscape in Claude Code has matured quickly. The geoMusings blog (January 2026) documents a hand-built `postgis-spatial-analysis` skill that handles SRID transformations, spatial index checks, and optimized query generation for point-in-polygon analysis between PostGIS tables — and it worked on first prompt with no hallucinations. The MCP Marketplace also lists standalone skills for GeoPandas vector workflows, geospatial visualization via HoloViz (choropleth, buffers, spatial joins, CRS management), and Geoapify routing automation.

Claude Code's skill architecture underpins all of this: each skill is a `SKILL.md` file (plus optional scripts and reference docs) that gives Claude domain expertise via progressive disclosure. Skills are auto-invoked when relevant, cost ~100 tokens to scan, and only expand to full context when activated. This makes stacking multiple geospatial skills practical without blowing the context window.

## Why it matters (or doesn't)

This is directly in Garrick's wheelhouse. A few specific connection points:

- **CostEstDB / PostGIS**: The `postgis-spatial-analysis` pattern from geoMusings maps exactly onto CostEstDB's PostgreSQL backend with pgvector. A custom skill could handle spatial lookups like "find all cost items within 500m of a proposed water main alignment" or "which line items have been used in projects in this county?" — combining pgvector semantic search with PostGIS spatial predicates in a single deterministic, repeatable workflow.
- **Municipal infrastructure data**: The `detect-objects` skill in geoai-skills runs pre-trained AI models on aerial/satellite imagery to detect buildings, cars, ships, and solar panels — and supports text-prompted GroundedSAM segmentation. For Abonmarche, the same framework could target manholes, catch basins, or pavement condition from NAIP or county ortho imagery.
- **`inspect-geo` skill**: Supports GeoTIFF, Shapefile, GeoJSON, GeoPackage, and GeoParquet — instantly reports CRS, bounds, band statistics, and attribute summaries. Useful for quickly auditing incoming municipal datasets before ArcGIS processing.
- **`search-stac` + `download-data`**: Pulls NAIP imagery from Microsoft Planetary Computer by bounding box and date range. Relevant for site context in plan review automation or project scoping.
- **Session memory (`read-memories`)**: Searches past Claude Code session logs for previously established CRS settings, file paths, and model configurations. Directly useful for multi-session GIS development workflows.
- **CoP demo potential**: Installing a geospatial skills plugin and doing a live point-in-polygon query against a PostGIS table is a compelling, reproducible demo for the AI Community of Practice.

## Technical details

- **Installation**: `/plugin marketplace add opengeos/geoai-skills` → `/plugin install geoai-skills@geoai-skills` inside Claude Code
- **Prerequisites**: Python 3.10+, `geoai-py` package (`pip install geoai-py`); PyTorch with CUDA optional (CPU works for AI models, slower)
- **Overture Maps data**: Requires `pip install "geoai-py[extra]"`
- **Platform**: macOS and Linux tested; Windows not yet fully supported
- **Maturity**: Early — 13 GitHub stars, 2 commits, no releases published yet. The underlying `geoai-py` library is more mature (opengeoai.org)
- **License**: MIT
- **ArcGIS compatibility**: No direct ArcPy integration — this is a Python/GDAL stack (GeoTIFF, GeoPackage, PostGIS), not ArcGIS File Geodatabases. Outputs can be consumed by ArcGIS Pro via GeoJSON or GeoPackage exchange
- **Security note**: The geoMusings demo passed database credentials in plaintext in the prompt — fine for dev, not for production. Skills that execute scripts can make network requests and run arbitrary code; review `SKILL.md` files before installing community skills
- **Broader ecosystem cost**: All geospatial skills on the MCP Marketplace (GeoPandas, Geoapify, HoloViz visualization) are free; some require external API keys

## Recommendation

**Install and test `opengeos/geoai-skills` in a local Claude Code session against a dev PostGIS instance.** Specifically:

1. Run `inspect-geo` on a sample municipal infrastructure GeoPackage to verify CRS/bounds reporting
2. Use `detect-objects buildings` on a NAIP tile for a known project area and compare against existing GIS data — this tests whether the AI detection pipeline is accurate enough to be useful for Abonmarche workflows
3. Build a lightweight custom `postgis-spatial-analysis` skill (following the geoMusings pattern) scoped to CostEstDB's schema — point-to-line proximity queries for cost item lookup would be the first use case
4. Stack with the `dynamic-context-injection` skill pattern (already researched) to inject live DB schema into geospatial skill prompts

The geoai-skills plugin is early-stage and the ArcGIS gap is real, but the PostGIS + AI imagery detection angle is novel and the skill framework itself is sound. The CoP demo value alone justifies a quick test.
