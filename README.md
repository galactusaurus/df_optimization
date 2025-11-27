# DraftKings Daily Fantasy Roster Optimizer

This Python script optimizes DraftKings daily fantasy sports rosters by maximizing the total average points per game while staying within salary constraints and meeting position requirements.

## Features

- **Linear Programming Optimization**: Uses the PuLP library to find the optimal lineup
- **Flexible Configuration**: Accepts custom position requirements via JSON config file
- **Dual Output Formats**:
  - DraftKings-compatible CSV for direct import
  - Human-readable CSV with detailed player information

## Requirements

- Python 3.7+
- pandas
- pulp

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas pulp
```

## Usage

### Basic Command

```bash
python optimize_roster.py --players <path_to_players_csv> --config <path_to_config_json> --max-salary <max_salary>
```

### Command-Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--players` | Yes | Path to CSV file containing player data |
| `--config` | Yes | Path to JSON configuration file with position requirements |
| `--max-salary` | Yes | Maximum total salary for the roster |
| `--dk-output` | No | Output path for DraftKings-compatible CSV (default: `dk_lineup.csv`) |
| `--readable-output` | No | Output path for human-readable CSV (default: `lineup_summary.csv`) |

### Example

```bash
python optimize_roster.py \
  --players "DKSalaries (10).csv" \
  --config position_config.json \
  --max-salary 50000 \
  --dk-output optimized_dk_output.csv \
  --readable-output optimized_summary.csv
```

## Input Files

### Player Data CSV

The player CSV file should contain the following columns:
- `Position`: Player's position (QB, RB, WR, TE, K, DST)
- `Name + ID`: Combined name and ID
- `Name`: Player name
- `ID`: Unique player ID
- `Roster Position`: Position slot (e.g., CPT, FLEX)
- `Salary`: Player's salary
- `Game Info`: Game information
- `TeamAbbrev`: Team abbreviation
- `AvgPointsPerGame`: Average points per game

### Position Configuration JSON

The configuration file should specify the number of players needed for each roster position:

```json
{
  "CPT": 1,
  "FLEX": 5
}
```

This example requires 1 Captain (CPT) and 5 Flex (FLEX) players.

## Output Files

### DraftKings-Compatible Output

This CSV file matches the DraftKings import format with player IDs organized by position columns:

```csv
CPT,FLEX
40935100,40935011
,40935012
,40935013
,40935014
,40935016
```

### Human-Readable Output

This CSV file provides detailed information about each selected player:

```csv
Roster Position,Player Name,Position,Team,Salary,Avg Points Per Game
CPT,Miles Sanders,RB,DAL,300,6.92
FLEX,Patrick Mahomes,QB,KC,10600,22.72
FLEX,Dak Prescott,QB,DAL,10400,21.57
...
TOTAL,,,,49300,110.12
```

The summary row shows the total salary used and total projected points.

## How It Works

1. **Load Data**: Reads player data from CSV and position requirements from JSON
2. **Optimize**: Uses linear programming to find the combination of players that:
   - Maximizes total average points per game
   - Stays within the salary cap
   - Meets all position requirements
3. **Generate Output**: Creates both DraftKings-compatible and human-readable CSV files

## Algorithm

The optimizer uses the PuLP library with the CBC MILP solver to solve a binary integer programming problem:

- **Decision Variables**: Binary (0 or 1) for each player (selected or not)
- **Objective Function**: Maximize sum of selected players' average points
- **Constraints**:
  - Total salary ≤ max salary
  - Exact number of players per position
  - Total number of players equals sum of all position requirements

## Tips for Best Results

1. **Update Player Data**: Ensure your player CSV has up-to-date average points and salaries
2. **Adjust Max Salary**: DraftKings contests have different salary caps (typically $50,000)
3. **Modify Position Requirements**: Customize the config file for different contest types
4. **Consider Game Context**: The optimizer uses only average points - consider matchups manually

## Troubleshooting

**No solution found**: If the optimizer cannot find a valid lineup, try:
- Increasing the max salary
- Adjusting position requirements
- Checking that enough players exist for each required position

**Import errors**: Make sure pandas and pulp are installed:
```bash
python -m pip install pandas pulp
```

## License

This project is open source and available for personal use.
