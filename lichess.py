from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import chess
import chess.engine
import pyautogui

START_URL = "https://lichess.org/"
ENGINE_PATH = "stockfish/14.1/bin/stockfish"

BOARD_CENTER_X = 663
BOARD_CENTER_Y = 488

BOARD_WIDTH = 565

SQ_SIZE = BOARD_WIDTH / 8

engine = chess.engine.SimpleEngine.popen_uci("stockfish/14.1/bin/stockfish")

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(START_URL)
driver.maximize_window()

moves = []

board = chess.Board()


def _make_move(f1, r1, f2, r2, side):
    f0, r0 = 4, 4  # center of the board

    if side == 1:
        f, r = f1 - f0, r1 - r0
        ff, rr = f2 - f0, r2 - r0

        x1_click = (2 * f + 1) * SQ_SIZE / 2
        y1_click = (2 * r - 1) * SQ_SIZE / 2

        x2_click = (2 * ff + 1) * SQ_SIZE / 2
        y2_click = (2 * rr - 1) * SQ_SIZE / 2
    else:
        f, r = f1 - f0, r1 - r0
        ff, rr = f2 - f0, r2 - r0

        x1_click = side * (2 * f + 1) * SQ_SIZE / 2
        y1_click = side * (2 * r - 1) * SQ_SIZE / 2

        x2_click = side * (2 * ff + 1) * SQ_SIZE / 2
        y2_click = side * (2 * rr - 1) * SQ_SIZE / 2

    pyautogui.moveTo(BOARD_CENTER_X + x1_click,
                     BOARD_CENTER_Y - y1_click)

    pyautogui.dragTo(BOARD_CENTER_X + x2_click,
                     BOARD_CENTER_Y - y2_click, button="left")


def make_move_on_window(engine_move, player_color):
    from_square = chess.SQUARE_NAMES[engine_move.from_square]
    to_square = chess.SQUARE_NAMES[engine_move.to_square]

    from_square_file = ord(from_square[0]) - ord('a')
    from_square_rank = int(from_square[1])

    to_square_file = ord(to_square[0]) - ord('a')
    to_square_rank = int(to_square[1])

    _make_move(from_square_file, from_square_rank,
               to_square_file, to_square_rank, player_color)


while 1:
    try:
        html = driver.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(html, features="lxml")

        if len(soup.find_all("div", {"class": "cg-wrap orientation-black manipulable"})) == 0:
            player_color = 1
        else:
            player_color = -1

        new_moves_html = soup.findAll("u8t")
        new_moves = [html.contents for html in new_moves_html]

        try:
            if len(new_moves) > len(moves):
                if len(new_moves) == len(moves)+1:
                    moves.append(new_moves[-1][0])
                    board.push_san(moves[-1])

                elif len(new_moves) > len(moves)+1:
                    board = chess.Board()
                    moves = [m[0] for m in new_moves]
                    for move in moves:
                        board.push_san(move)

                if (player_color == 1 and board.turn == chess.WHITE) or (player_color == -1 and board.turn == chess.BLACK):
                    best_move = engine.play(
                        board, chess.engine.Limit(time=.5)).move
                    print(
                        f"move: {moves[-1]}, best move: {best_move}")

                    make_move_on_window(best_move, player_color)
            elif len(new_moves) == 0:
                print("\nresetting bot...")
                board = chess.Board()
                moves = []
        except Exception as e:
            #print("WARNING: something bad happened:", e)
            pass
    except KeyboardInterrupt:
        print("\nterminating...")
        break

engine.quit()
driver.quit()
