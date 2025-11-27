"""
DraftKings Daily Fantasy Roster Optimizer

This script optimizes a DraftKings roster by maximizing average points per game
while staying within salary constraints and meeting position requirements.
"""

import pandas as pd
import json
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpBinary, value
import argparse
from pathlib import Path


def load_players(file_path):
    """Load player data from CSV or Excel file."""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif file_ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Please use .csv, .xlsx, or .xls")
    
    return df


def load_position_requirements(config_path):
    """Load position requirements from JSON config file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def optimize_roster(players_df, position_requirements, max_salary):
    """
    Optimize roster selection using linear programming.
    
    Args:
        players_df: DataFrame containing player information
        position_requirements: Dict with position requirements
        max_salary: Maximum total salary allowed
    
    Returns:
        Tuple of (selected_players_df, total_points, total_salary)
    """
    # Create the optimization problem
    prob = LpProblem("DFS_Roster_Optimization", LpMaximize)
    
    # Create binary decision variables for each player
    player_vars = []
    for idx in players_df.index:
        var = LpVariable(f"player_{idx}", cat=LpBinary)
        player_vars.append(var)
    
    # Objective: Maximize total average points
    prob += lpSum([
        players_df.loc[idx, 'AvgPointsPerGame'] * player_vars[idx]
        for idx in players_df.index
    ]), "Total_Points"
    
    # Constraint: Total salary must not exceed max_salary
    prob += lpSum([
        players_df.loc[idx, 'Salary'] * player_vars[idx]
        for idx in players_df.index
    ]) <= max_salary, "Salary_Cap"
    
    # Constraint: Exact number of players required
    total_positions = sum(position_requirements.values())
    prob += lpSum(player_vars) == total_positions, "Total_Players"
    
    # Position constraints
    for position, count in position_requirements.items():
        # Get indices of players who can fill this position
        position_indices = players_df[players_df['Roster Position'] == position].index
        
        prob += lpSum([
            player_vars[idx] for idx in position_indices
        ]) == count, f"Position_{position}"
    
    # Solve the problem
    prob.solve()
    
    # Extract selected players
    selected_indices = [idx for idx in players_df.index if value(player_vars[idx]) == 1]
    selected_players = players_df.loc[selected_indices].copy()
    
    total_points = selected_players['AvgPointsPerGame'].sum()
    total_salary = selected_players['Salary'].sum()
    
    return selected_players, total_points, total_salary


def generate_dk_output(selected_players, output_path):
    """
    Generate DraftKings-compatible CSV output.
    
    Format matches example_dk_output.csv with position columns and player IDs.
    """
    # Group players by roster position
    position_groups = selected_players.groupby('Roster Position')
    
    # Create output dictionary
    output_data = {}
    
    for position, group in position_groups:
        player_ids = group['ID'].tolist()
        # Create column names for this position
        if position not in output_data:
            output_data[position] = []
        output_data[position] = player_ids
    
    # Find the maximum length to pad shorter lists
    max_length = max(len(v) for v in output_data.values())
    
    # Pad all lists to same length
    for key in output_data:
        while len(output_data[key]) < max_length:
            output_data[key].append('')
    
    # Create DataFrame
    output_df = pd.DataFrame(output_data)
    
    # Reorder columns to match expected format
    # Get columns in order, putting CPT first if it exists
    ordered_cols = []
    if 'CPT' in output_df.columns:
        ordered_cols.append('CPT')
    
    # Add other columns alphabetically
    other_cols = sorted([col for col in output_df.columns if col != 'CPT'])
    ordered_cols.extend(other_cols)
    
    output_df = output_df[ordered_cols]
    
    # Save to CSV
    output_df.to_csv(output_path, index=False)
    print(f"DraftKings output saved to: {output_path}")


def generate_human_readable_output(selected_players, total_points, total_salary, output_path):
    """
    Generate a human-readable CSV output with player details.
    """
    # Sort by roster position for better readability
    sorted_players = selected_players.sort_values(['Roster Position', 'AvgPointsPerGame'], 
                                                   ascending=[True, False])
    
    # Select relevant columns
    output_df = sorted_players[[
        'Roster Position', 'Name', 'Position', 'TeamAbbrev', 
        'Salary', 'AvgPointsPerGame'
    ]].copy()
    
    output_df.columns = ['Roster Position', 'Player Name', 'Position', 'Team', 
                         'Salary', 'Avg Points Per Game']
    
    # Add summary row
    summary_row = pd.DataFrame([{
        'Roster Position': 'TOTAL',
        'Player Name': '',
        'Position': '',
        'Team': '',
        'Salary': total_salary,
        'Avg Points Per Game': total_points
    }])
    
    output_df = pd.concat([output_df, summary_row], ignore_index=True)
    
    # Save to CSV
    output_df.to_csv(output_path, index=False)
    print(f"Human-readable output saved to: {output_path}")
    
    # Print summary to console
    print("\n" + "="*80)
    print("OPTIMIZED ROSTER SUMMARY")
    print("="*80)
    print(output_df.to_string(index=False))
    print("="*80)
    print(f"Total Salary: ${total_salary:,}")
    print(f"Total Average Points: {total_points:.2f}")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Optimize DraftKings daily fantasy roster by maximizing average points.'
    )
    parser.add_argument(
        '--players',
        type=str,
        required=True,
        help='Path to CSV file containing player data'
    )
    parser.add_argument(
        '--config',
        type=str,
        required=True,
        help='Path to JSON configuration file with position requirements'
    )
    parser.add_argument(
        '--max-salary',
        type=int,
        required=True,
        help='Maximum total salary for the roster'
    )
    parser.add_argument(
        '--dk-output',
        type=str,
        default='dk_lineup.csv',
        help='Output path for DraftKings-compatible CSV (default: dk_lineup.csv)'
    )
    parser.add_argument(
        '--readable-output',
        type=str,
        default='lineup_summary.csv',
        help='Output path for human-readable CSV (default: lineup_summary.csv)'
    )
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading players from: {args.players}")
    players_df = load_players(args.players)
    print(f"Loaded {len(players_df)} players")
    
    print(f"\nLoading position requirements from: {args.config}")
    position_requirements = load_position_requirements(args.config)
    print(f"Position requirements: {position_requirements}")
    
    # Optimize roster
    print(f"\nOptimizing roster with max salary: ${args.max_salary:,}")
    selected_players, total_points, total_salary = optimize_roster(
        players_df, 
        position_requirements, 
        args.max_salary
    )
    
    # Generate outputs
    print("\nGenerating output files...")
    generate_dk_output(selected_players, args.dk_output)
    generate_human_readable_output(selected_players, total_points, total_salary, args.readable_output)
    
    print("\nOptimization complete!")


if __name__ == "__main__":
    main()
