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
        Tuple of (selected_players_df, total_points, total_salary, position_assignments)
    """
    # Create the optimization problem
    prob = LpProblem("DFS_Roster_Optimization", LpMaximize)
    
    # Create binary decision variables for each player-position combination
    # This allows a player to be selected for a specific position
    player_position_vars = {}
    
    for idx in players_df.index:
        roster_pos = str(players_df.loc[idx, 'Roster Position'])
        positions_available = [p.strip() for p in roster_pos.split('/')]
        
        for position in position_requirements.keys():
            if position in positions_available:
                var = LpVariable(f"player_{idx}_pos_{position}", cat=LpBinary)
                player_position_vars[(idx, position)] = var
    
    # Objective: Maximize total average points
    prob += lpSum([
        players_df.loc[idx, 'AvgPointsPerGame'] * var
        for (idx, position), var in player_position_vars.items()
    ]), "Total_Points"
    
    # Constraint: Total salary must not exceed max_salary
    prob += lpSum([
        players_df.loc[idx, 'Salary'] * var
        for (idx, position), var in player_position_vars.items()
    ]) <= max_salary, "Salary_Cap"
    
    # Constraint: Each player can only be selected once (for at most one position)
    for idx in players_df.index:
        relevant_vars = [var for (i, pos), var in player_position_vars.items() if i == idx]
        if relevant_vars:
            prob += lpSum(relevant_vars) <= 1, f"Player_{idx}_Once"
    
    # Constraint: Exact number of players for each position
    for position, count in position_requirements.items():
        relevant_vars = [var for (idx, pos), var in player_position_vars.items() if pos == position]
        
        if len(relevant_vars) == 0:
            print(f"WARNING: No players found for position '{position}'")
            print(f"Available roster positions in data: {players_df['Roster Position'].unique()}")
        
        prob += lpSum(relevant_vars) == count, f"Position_{position}"
    
    # Solve the problem
    prob.solve()
    
    # Extract selected players and their assigned positions
    selected_data = []
    position_assignments = {}
    
    for (idx, position), var in player_position_vars.items():
        if value(var) == 1:
            player_row = players_df.loc[idx].copy()
            player_row['Assigned_Position'] = position
            selected_data.append(player_row)
            position_assignments[idx] = position
    
    selected_players = pd.DataFrame(selected_data)
    
    total_points = selected_players['AvgPointsPerGame'].sum()
    total_salary = selected_players['Salary'].sum()
    
    return selected_players, total_points, total_salary, position_assignments


def generate_dk_output(selected_players, position_requirements, output_path):
    """
    Generate DraftKings-compatible CSV output.
    
    Format: Single row with player IDs in position order.
    """
    # Create a single row with all player IDs organized by assigned position
    lineup_row = {}
    
    # Sort positions to ensure consistent ordering
    sorted_positions = sorted(position_requirements.keys())
    
    # For each required position, get assigned players
    for position in sorted_positions:
        count = position_requirements[position]
        
        # Find players assigned to this position
        assigned = selected_players[selected_players['Assigned_Position'] == position]
        
        # Assign the players for this position
        for i, (idx, row) in enumerate(assigned.iterrows()):
            # Create column name with index if multiple players for this position
            if count > 1:
                col_name = f"{position}{i + 1}"
            else:
                col_name = position
            
            lineup_row[col_name] = row['ID']
    
    # Create DataFrame with a single row
    output_df = pd.DataFrame([lineup_row])
    
    # Save to CSV
    output_df.to_csv(output_path, index=False)
    print(f"DraftKings output saved to: {output_path}")


def generate_human_readable_output(selected_players, total_points, total_salary, output_path):
    """
    Generate a human-readable CSV output with player details.
    """
    # Sort by assigned position for better readability
    sorted_players = selected_players.sort_values(['Assigned_Position', 'AvgPointsPerGame'], 
                                                   ascending=[True, False])
    
    # Select relevant columns
    output_df = sorted_players[[
        'Assigned_Position', 'Name', 'Position', 'TeamAbbrev', 
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
    selected_players, total_points, total_salary, position_assignments = optimize_roster(
        players_df, 
        position_requirements, 
        args.max_salary
    )
    
    # Generate outputs
    print("\nGenerating output files...")
    generate_dk_output(selected_players, position_requirements, args.dk_output)
    generate_human_readable_output(selected_players, total_points, total_salary, args.readable_output)
    
    print("\nOptimization complete!")


if __name__ == "__main__":
    main()
