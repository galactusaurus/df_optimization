# Quick Start Guide

## Installation (First Time Only)

1. Install Python 3.7 or higher from [python.org](https://www.python.org/downloads/)
2. Install required packages:
   ```bash
   python -m pip install pandas pulp
   ```

## Running the Optimizer

### Option 1: Using the Batch Script (Easiest)
Double-click `run_optimizer.bat`

### Option 2: Using PowerShell Script
```powershell
.\run_optimizer.ps1
```

### Option 3: Using Python Directly
```bash
python optimize_roster.py --players "DKSalaries (10).csv" --config position_config.json --max-salary 50000
```

### Option 4: Custom Parameters with PowerShell
```powershell
.\run_optimizer.ps1 -PlayersFile "my_players.csv" -MaxSalary 60000
```

## Customizing for Your Contest

1. **Update Player Data**: Replace `DKSalaries (10).csv` with your current player data
2. **Adjust Salary Cap**: Change the `--max-salary` parameter (typically 50000 for DraftKings)
3. **Modify Positions**: Edit `position_config.json` for your contest type

### Example: Classic NFL Lineup
Edit `position_config.json`:
```json
{
  "QB": 1,
  "RB": 2,
  "WR": 3,
  "TE": 1,
  "FLEX": 1,
  "DST": 1
}
```

### Example: Showdown Captain Mode
Edit `position_config.json`:
```json
{
  "CPT": 1,
  "FLEX": 5
}
```

## Output Files

After running, you'll get two files:

1. **optimized_dk_output.csv** - Import this directly into DraftKings
2. **optimized_summary.csv** - Review your lineup details here

## Tips

- The optimizer maximizes **average points per game**
- Always review the lineup manually for recent injuries, weather, etc.
- You can run the optimizer multiple times with different salary caps
- The optimizer guarantees the best possible lineup given your constraints

## Troubleshooting

**"Python is not recognized"**
- Make sure Python is installed and added to your PATH

**"No module named pandas"**
- Run: `python -m pip install pandas pulp`

**"No solution found"**
- Try increasing the max salary
- Check that your position requirements match available players

## Need Help?

See the full README.md for detailed documentation.
