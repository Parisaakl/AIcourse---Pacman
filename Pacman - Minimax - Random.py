import numpy as np
import random
import os
import platform
from time import sleep

# Constants for the game
WALL = '#'
PELLET = '.'
EMPTY = ' '
PACMAN = 'P'
GHOST = 'G'

# Directions
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Initial Game Board Setup
def create_board(width, height):
    board = np.full((height, width), PELLET)
    for i in range(height):
        for j in range(width):
            if i == 0 or i == height - 1 or j == 0 or j == width - 1:
                board[i, j] = WALL
    return board

# Function to display the game board
def display_board(board, pacman_pos, ghost_pos):
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    temp_board = np.copy(board)
    temp_board[pacman_pos] = PACMAN
    for pos in ghost_pos:
        temp_board[pos] = GHOST
    for row in temp_board:
        print(' '.join(row))


# Function to count the number of pellets remaining
def count_pellets(board):
    return np.sum(board == PELLET)

# Function to move Pac-Man or Ghost
def move_character(position, direction, board):
    new_position = (position[0] + direction[0], position[1] + direction[1])
    if board[new_position] != WALL:
        return new_position
    return position

# Function to check game over conditions
def is_game_over(pacman_pos, ghost_pos):
    return pacman_pos in ghost_pos

# Function to create a custom layout
def create_custom_layout(layout):
    height = len(layout)
    width = len(layout[0])
    board = np.full((height, width), EMPTY)
    pacman_pos = None
    ghost_pos = []

    for i, row in enumerate(layout):
        for j, cell in enumerate(row):
            if cell == WALL:
                board[i, j] = WALL
            elif cell == PELLET:
                board[i, j] = PELLET
            elif cell == PACMAN:
                pacman_pos = (i, j)
            elif cell == GHOST:
                ghost_pos.append((i, j))
            # Empty space is already the default

    return board, pacman_pos, ghost_pos


# Minimax algorithm implementation
def minimax(board, pacman_pos, ghost_pos, depth, is_max, max_depth=3):
    if depth == max_depth or is_game_over(pacman_pos, ghost_pos):
        return None, evaluate(pacman_pos, ghost_pos, board)

    if is_max:
        best_move = None
        best_score = float('-inf')
        for move in DIRECTIONS:
            new_pos = move_character(pacman_pos, move, board)
            if new_pos != pacman_pos:
                _, score = minimax(board, new_pos, ghost_pos, depth + 1, False)  # Corrected here
                if score > best_score:
                    best_score = score
                    best_move = move
        return best_move, best_score
    else:
        best_move = None
        best_score = float('inf')
        for pos in ghost_pos:
            for move in DIRECTIONS:
                new_pos = move_character(pos, move, board)
                if new_pos != pos:
                    _, score = minimax(board, pacman_pos, [new_pos if x == pos else x for x in ghost_pos], depth + 1, True)  # Corrected here
                    if score < best_score:
                        best_score = score
                        best_move = move
        return best_move, best_score

def evaluate(pacman_pos, ghost_pos, board):
    pellet_count = count_pellets(board)
    ghost_distance = min(abs(pacman_pos[0] - pos[0]) + abs(pacman_pos[1] - pos[1]) for pos in ghost_pos)
    
    # Increase the penalty for being close to ghosts
    ghost_penalty = -200 if ghost_distance < 4 else 0  # Larger penalty if a ghost is too close

    # Find the distance to the nearest pellet
    pellet_positions = np.argwhere(board == PELLET)
    if pellet_positions.size > 0:
        nearest_pellet_distance = min(np.sum(np.abs(pacman_pos - pellet_pos)) for pellet_pos in pellet_positions)
    else:
        nearest_pellet_distance = 0

    # Reward for eating pellets and being close to the nearest pellet
    pellet_reward = 20 * (1 / (1 + pellet_count))  # Increase the weight of pellet count
    pellet_proximity_reward = 10 / (1 + nearest_pellet_distance)  # Reward for being closer to pellets

    # Adjust the function to heavily penalize getting close to ghosts, and reward pellet eating and proximity to pellets more
    return pellet_reward + pellet_proximity_reward + ghost_penalty

def display_board_with_score(board, pacman_pos, ghost_pos, score):
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    temp_board = np.copy(board)
    temp_board[pacman_pos] = PACMAN
    for pos in ghost_pos:
        temp_board[pos] = GHOST
    for row in temp_board:
        print(' '.join(row))
    print(f"Score: {score}")

# Main game play function with Minimax for Pac-Man and random movement for ghosts
# Main game play function with Minimax for Pac-Man and random movement for ghosts
def play_game_with_minimax(board_width, board_height, num_ghosts, layout=None):
    if layout:
        board, pacman_pos, ghost_pos = create_custom_layout(layout)
    else:
        board = create_board(board_width, board_height)
        pacman_pos = (board_height // 2, board_width // 2)
        ghost_pos = [(random.randint(1, board_height - 2), random.randint(1, board_width - 2)) for _ in range(num_ghosts)]

    score = 0
    moves_without_pellet = 0

    while True:
        display_board_with_score(board, pacman_pos, ghost_pos, score)

        move, _ = minimax(board, pacman_pos, ghost_pos, 0, True, max_depth=3)
        if move:
            new_pos = move_character(pacman_pos, move, board)
            if board[new_pos] == PELLET:
                board[new_pos] = EMPTY  # Erase the pellet
                score += 10
                moves_without_pellet = 0  # Reset the counter as Pac-Man ate a pellet
            else:
                moves_without_pellet += 1  # Increment the counter for moves without eating a pellet

            # Deduct points if Pac-Man hasn't eaten a pellet for too many moves
            if moves_without_pellet >= 10:
                score -= 1
                moves_without_pellet = 0  # Reset the counter to avoid continuous score deduction

            pacman_pos = new_pos

        # Random movement for ghosts
        for i in range(len(ghost_pos)):
            ghost_pos[i] = move_character(ghost_pos[i], random.choice(DIRECTIONS), board)

        if is_game_over(pacman_pos, ghost_pos):
            print(f"Game Over! Final Score: {score}")
            break
        sleep(1)



custom_layout = [
    "####################",
    "#....#........#....#",
    "#.##.#.######.#.##.#",
    "#.#.............G#.#",
    "#.#.##.##  ##.##.#.#",
    "#......#    #......#",
    "#.#.##.######.##.#.#",
    "#.#........G.....#.#",
    "#.##.#.######.#.##.#",
    "#....#...P....#....#",
    "####################"
]


# Main function
def main():
    play_game_with_minimax(board_width=20, board_height=10, num_ghosts=2, layout=custom_layout)  # Function call is correct

# Run the game
if __name__ == "__main__":
    main()