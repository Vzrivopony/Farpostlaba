"""
Given a Tic-Tac-Toe 3x3 board (can be unfinished).
Write a function that checks if the are some winners.
If there is "x" winner, function should return "x wins!"
If there is "o" winner, function should return "o wins!"
If there is a draw, function should return "draw!"
If board is unfinished, function should return "unfinished!"

Example:
    [[-, -, o],
     [-, x, o],
     [x, o, x]]
    Return value should be "unfinished"

    [[-, -, o],
     [-, o, o],
     [x, x, x]]

     Return value should be "x wins!"

"""
from typing import List


def tic_tac_toe_checker(board: List[List]) -> str:
    for i in range(len(board)):
      if (board[i][0] == board[i][1] == board[i][2]) and board[i][0] != "-":
        return f"{board[i][0]} wins!"
      if (board[0][i] == board[0][i] == board[1][i]) and board[0][i] != "-":
        return f"{board[0][i]} wins!"
      if (board[0][0] == board[1][1] == board[2][2]) and board[1][1] != "-":
        return f"{board[0][0]} wins!"
      if (board[0][2] == board[1][1] == board[2][0]) and board[0][2] != "-":
        return f"{board[0][2]} wins!"
      for row in board:
        if "-" in row:
          return "unfinished!"
      return "draw"


checkboard = [
    ["-", "-", "o"],
    ["-", "x", "o"],
    ["x", "o", "x"]
]

checkboard1 = [
    ["x", "x", "x"],
    ["o", "-", "-"],
    ["-", "o", "-"]
]
print(tic_tac_toe_checker(checkboard))
print(tic_tac_toe_checker(checkboard1))