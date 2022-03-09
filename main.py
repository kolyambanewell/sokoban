import copy
import sys

''' Это константы, относящиеся к классу Game'''
PLAYER = '@'
BOX = 'B'
WALL = '#'
SPACE = '.'
GOAL = 'X'

'''Это константы, относящиеся к классу Gamer'''
UP = 'w'
DOWN = 's'
LEFT = 'a'
RIGHT = 'd'
EXIT = 'q'


class Move(BaseException):
    pass


class Direction(BaseException):
    pass


class Maze:
    def __init__(self, maze: list[list[str]]):
        self.maze = maze
        self.maze_copy = copy.deepcopy(maze)
        self.tokens = {
            PLAYER,
            BOX,
            GOAL,
            SPACE,
            WALL
        }

    def __hash__(self):
        s = ''
        for row in self.maze:
            for column in row:
                s += column
        return hash(s)

    def get_spot(self, i, j):
        return self.maze[i][j]

    def find_gamer_spot(self):
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.get_spot(i, j) == PLAYER:
                    return [i, j]
        return print('Нет игрока на карте')

    def get_row(self, i):
        return self.maze[i]

    def action(self, i, j, gamer_row, gamer_column):
        move_r = i + gamer_row
        move_c = j + gamer_column
        spot = self.get_spot(move_r, move_c)
        copy_spot = self.maze_copy[i][j]
        if spot == SPACE or spot == GOAL:
            self.maze[move_r][move_c] = PLAYER
            self.maze[i][j] = SPACE if copy_spot == PLAYER or copy_spot == BOX else copy_spot
        else:
            spot_r = 2 * gamer_row + i
            spot_c = 2 * gamer_column + j
            self.maze[move_r][move_c] = PLAYER
            self.maze[spot_r][spot_c] = BOX
            self.maze[i][j] = SPACE if copy_spot == PLAYER or copy_spot == BOX else copy_spot


class Game:
    def __init__(self, rows, columns, game_maze: Maze):
        self.game_maze = game_maze
        self.height = rows
        self.weight = columns

    def __hash__(self):
        return hash(self.game_maze)

    def picture(self):
        for i in range(self.weight):
            row_line = self.game_maze.get_row(i)
            for column in row_line:
                print(column, end='')
            print()

    def valid_spot(self, i, j, gamer_r, gamer_c, spot):
        spot_r = 2 * i + gamer_r
        spot_c = 2 * j + gamer_c
        next_spot = self.check_spot(spot_r, spot_c)
        if spot == BOX and next_spot == BOX:
            return False
        if spot == BOX and next_spot == WALL:
            return False
        if spot == WALL:
            return False

        return True

    def mark_spot(self, i, j, gamer_r, gamer_c):
        spot_r = i + gamer_r
        spot_c = j + gamer_c
        spot = self.check_spot(spot_r, spot_c)
        valid_spot = self.valid_spot(i, j, gamer_r, gamer_c, spot)
        if self.free_spot(spot) or valid_spot:
            self.game_maze.action(gamer_r, gamer_c, i, j)
        else:
            raise Direction

    def check_spot(self, i, j):
        if self.weight > i >= 0 and self.height > j >= 0:
            return self.game_maze.get_spot(i, j)
        else:
            raise Move

    def win(self):
        for i in range(self.weight):
            for j in range(self.height):
                spot = self.check_spot(i, j)
                spot_copy = self.game_maze.maze_copy[i][j]
                if spot == PLAYER:
                    if spot_copy == GOAL:
                        return False
                if spot == GOAL:
                    return False
        print('Все коробки на месте!')
        return True

    @staticmethod
    def free_spot(spot):
        return spot == SPACE or spot == GOAL


class Human:
    def __init__(self, game: Game):
        self.maze = game
        self.spot = self.maze.game_maze.find_gamer_spot()
        self.actions = {
            UP: [-1, 0],
            DOWN: [1, 0],
            LEFT: [0, -1],
            RIGHT: [0, 1]
        }

    def move(self):
        player_move = input()
        if player_move == EXIT:
            sys.exit(1)
        if player_move in self.actions:
            self.maze.mark_spot(
                self.actions[player_move][0],
                self.actions[player_move][1],
                *self.spot)
            self.spot[0] += self.actions[player_move][0]
            self.spot[1] += self.actions[player_move][1]
        else:
            raise Direction


class Smart:
    def __init__(self, game: Game):
        self.maze = game
        self.spot = self.maze.game_maze.find_gamer_spot()
        self.actions = {
            UP: [-1, 0],
            DOWN: [1, 0],
            LEFT: [0, -1],
            RIGHT: [0, 1]
        }
        self.complete_maze = False
        self.maze_tree = dict()
        self.maze_moves = []
        self.hash_table = set()
        self.hash_table.add(hash(self.maze))
        self.i = 0

    def move(self):
        if len(self.maze_moves) == 0:
            game_maze_copy = copy.deepcopy(self.maze)
            self.start_maze(self.maze_tree, game_maze_copy)
            self.maze_moves.reverse()
        else:
            self.maze.mark_spot(self.actions[self.maze_moves[self.i]][0],
                                self.actions[self.maze_moves[self.i]][1],
                                *self.spot)
            self.spot[0] += self.actions[self.maze_moves[self.i]][0]
            self.spot[1] += self.actions[self.maze_moves[self.i]][1]
            self.i += 1

    def check_complete(self, player_move):
        self.complete_maze = True
        self.maze_moves.append(player_move)
        self.spot[0] -= self.actions[player_move][0]
        self.spot[1] -= self.actions[player_move][1]
        return

    def start_maze(self, maze_tree, game: Game):
        for player_move, move in self.actions.items():
            try:
                copy_smart_maze = copy.deepcopy(game)
                game.mark_spot(self.actions[player_move][0],
                               self.actions[player_move][1],
                               *self.spot)
                self.spot[0] += self.actions[player_move][0]
                self.spot[1] += self.actions[player_move][1]
                print('Алгоритм в поиске решения')
                result = hash(game)

                if game.win():
                    self.check_complete(player_move)
                    return

                if result not in self.hash_table:
                    maze_tree[player_move] = dict()
                    self.hash_table.add(hash(game))
                    copy_game_maze = copy.deepcopy(game)
                    self.start_maze(maze_tree[player_move], copy_game_maze)

                self.spot[0] -= self.actions[player_move][0]
                self.spot[1] -= self.actions[player_move][1]

                if self.complete_maze:
                    self.maze_moves.append(player_move)
                    return
                game = copy_smart_maze

            except (Direction, Move):
                print('Подбираем направление движения')


class GameEngine:
    def __init__(self, game: Game, gamer):
        self.maze = game
        self.gamer = gamer

    def start(self):
        print("Нажмите w s a d чтобы передвигаться по лабиринту")
        self.maze.picture()
        while not self.maze.win():
            try:
                self.gamer.move()
                self.maze.picture()
            except Direction:
                print('В этом направлении нельзя двигаться')
            except Move:
                print('Невозможный ход')


def main(argv):
    with open(argv[1]) as file:
        rows = file.readlines()
        maze = [[each for each in line.replace('\n', '')] for line in rows]

        game = Game(len(maze[0]), len(maze), Maze(maze))

        print('Если хотите, чтобы лабиринт решил ИИ, нажмите c.\n'
              'Если хотите играть сами, нажмите r')
        choose = input().lower()

        if choose == 'r':
            gamer = Human(game)
        else:
            gamer = Smart(game)

        game_ini = GameEngine(game, gamer)
        game_ini.start()


if __name__ == '__main__':
    print("Добро пожаловать в игру Сокобан!")
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        sys.exit(1)
