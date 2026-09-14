# Replay Corner Analyzer

A deterministic football analytics prototype that retrieves and explains similar corner kicks from StatsBomb Open Data.

## Goal

Build an interpretable pipeline:

```text
event data -> corner extraction -> tactical features -> deterministic similarity -> top matches -> visualisation
```

The first version deliberately avoids machine learning. It focuses on clean data representation, transparent rules, and explainable retrieval.

## Project structure

```text
replay-corner-analyzer/
├── assets/                 # Images used in the README
├── data/
│   ├── raw/                # Original event data (not committed)
│   └── processed/          # Generated corner datasets (not committed)
├── notebooks/              # Exploration notebooks
├── src/
│   └── replay_corner_analyzer/
├── tests/
├── README.md
├── requirements.txt
└── LICENSE
```

## Status

Work in progress. The project is being built incrementally from a minimal deterministic prototype.

## Data source

The project will use [StatsBomb Open Data](https://github.com/hudl/open-data). Data files remain subject to StatsBomb's terms and attribution requirements.

## License

Code is released under the MIT License.
