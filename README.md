# REPLAY Corner Analyzer

A deterministic football-analysis MVP that converts StatsBomb event data into searchable corner-kick situations and optional video clips.

The project demonstrates the core REPLAY workflow without a large language model: a user writes a simple French or English request, the parser converts it into explicit filters, and the system returns the matching corners with their tactical context and outcome.

## What the MVP does

- downloads a match from StatsBomb Open Data;
- extracts every corner into a tabular dataset;
- labels the corner side and target zone;
- detects shots, cumulative expected goals (xG), and goals produced within 10 seconds in the same possession;
- parses simple natural-language queries in French and English;
- filters and displays matching events;
- exports JSON clip manifests;
- aligns event timestamps with a legally obtained match video;
- generates MP4 clips with FFmpeg.

## Pipeline

```text
StatsBomb events
      |
      v
corner extraction
      |
      v
deterministic tactical features
      |
      v
French/English query parser
      |
      v
matching corners -> JSON manifest -> optional FFmpeg clips
```

The system is deliberately deterministic: every result can be traced to a visible rule, without an opaque model or external AI API.

## Quick start

Requirements:

- Python 3.12;
- FFmpeg only if you want to generate MP4 clips.

Clone the repository and create an environment:

```bash
git clone https://github.com/guillaumesaintpierre/replay-corner-analyzer.git
cd replay-corner-analyzer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Prepare the example Borussia Dortmund–Bayer Leverkusen match from 21 April 2024:

```bash
PYTHONPATH=src python -m replay_corner_analyzer.prepare_data 3895309
```

This downloads the event JSON into `data/raw/` and writes the query-ready table to `data/processed/corners.csv`.

Run a French query:

```bash
PYTHONPATH=src python -m replay_corner_analyzer.cli \
  "Montre-moi les corners au second poteau de Leverkusen après la 45e qui donnent un tir"
```

Or an English query:

```bash
PYTHONPATH=src python -m replay_corner_analyzer.cli \
  "Show me Dortmund near post corners before the 70th minute"
```

The CLI prints both the detected structured filters and the matching events, making the retrieval process explainable.

## Supported query criteria

| Criterion | Examples |
|---|---|
| Team | `Leverkusen`, `Dortmund` |
| Target zone | `premier poteau`, `second poteau`, `corner court`, `central box` |
| Outcome | `avec un tir`, `sans tir`, `with a shot` |
| Match time | `après la 45e`, `before the 70th minute` |
| Minimum xG | `xG >= 0.05`, `xG above 0.10` |
| Side | `côté gauche`, `right side` |

Unsupported wording is ignored rather than guessed. The CLI always displays the filters it actually detected.

## Tactical rules

| Feature | Deterministic rule |
|---|---|
| `side` | `start_y < 40` is left; otherwise right |
| `short_corner` | pass length below 25 StatsBomb units |
| `central_box` | non-short corner ending at `34 <= end_y <= 46` |
| `near_post` | non-central delivery toward the corner-taking side |
| `far_post` | remaining non-short delivery |
| Shot outcome | same team, period and possession, within 10 seconds |
| `xg_within_10s` | sum of StatsBomb xG for qualifying shots |

These thresholds form an interpretable baseline and can later be calibrated with more matches or domain feedback.

## Export a clip manifest

A query can be converted into timestamp windows without having the match video:

```bash
PYTHONPATH=src python -m replay_corner_analyzer.cli \
  "Leverkusen far post corners with a shot" \
  --export outputs/clips.json \
  --pre-roll 5 \
  --post-roll 15
```

The JSON manifest contains event identifiers, match-clock timestamps, tactical labels, outcomes, and clip boundaries.

## Generate MP4 clips

Match footage is not included in this repository. With a legally obtained video, provide the video timestamps at which each half kicks off:

```bash
PYTHONPATH=src python -m replay_corner_analyzer.cli \
  "Leverkusen far post corners with a shot" \
  --video data/video/match.mp4 \
  --first-half-kickoff 120 \
  --second-half-kickoff 3440 \
  --clips-dir outputs/clips \
  --export outputs/clips.json
```

Kickoff values are seconds from the beginning of the video. They compensate for introductions, half-time coverage, and other broadcast footage. FFmpeg then creates one MP4 per result.

## Tests

Run the complete suite:

```bash
PYTHONPATH=src python -m pytest -q
```

The suite covers downloading, extraction, tactical features, shot outcomes, query parsing, filtering, manifest export, video alignment, FFmpeg command construction, and the CLI. GitHub Actions runs the same tests automatically.

## Project structure

```text
src/replay_corner_analyzer/
├── load_data.py            # StatsBomb download
├── extract_corners.py      # Event flattening
├── feature_engineering.py  # Tactical labels and outcomes
├── prepare_data.py         # End-to-end dataset preparation
├── parser.py               # Deterministic FR/EN parsing
├── query.py                # DataFrame filtering
├── clip_export.py          # JSON clip windows
├── video_clips.py          # Video alignment and FFmpeg
└── cli.py                  # User-facing command
```

## Current limitations

- The parser recognizes a controlled set of phrases; it is not a general-purpose language model.
- Tactical thresholds are a transparent baseline rather than learned parameters.
- Event data does not provide player tracking or defensive positioning.
- Video/event synchronization requires the user to enter kickoff offsets.
- The repository does not distribute copyrighted match footage.

Possible next versions include multi-match indexing, weighted similarity ranking, pitch visualizations, and learned embeddings once enough validated data is available.

## Data and attribution

Event data comes from [StatsBomb Open Data](https://github.com/statsbomb/open-data) and remains subject to its attribution and usage requirements.

## License

Code is released under the MIT License.
