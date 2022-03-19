from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import chess
import chess.engine
import pyautogui
import time
import keyboard

START_URL = "https://www.chess.com/play/online"
ENGINE_PATH = "stockfish/14.1/bin/stockfish"

BOARD_CENTER_X = 498
BOARD_CENTER_Y = 522

BOARD_WIDTH = 615

SQ_SIZE = BOARD_WIDTH / 8

engine = chess.engine.SimpleEngine.popen_uci("stockfish/14.1/bin/stockfish")

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(START_URL)
driver.maximize_window()


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
                     BOARD_CENTER_Y - y1_click, 0.05)

    pyautogui.dragTo(BOARD_CENTER_X + x2_click,
                     BOARD_CENTER_Y - y2_click, 0.08, button="left")


def make_move_on_window(engine_move, player_color):
    from_square = chess.SQUARE_NAMES[engine_move.from_square]
    to_square = chess.SQUARE_NAMES[engine_move.to_square]

    from_square_file = ord(from_square[0]) - ord('a')
    from_square_rank = int(from_square[1])

    to_square_file = ord(to_square[0]) - ord('a')
    to_square_rank = int(to_square[1])

    _make_move(from_square_file, from_square_rank,
               to_square_file, to_square_rank, player_color)


def parse_clock_time(clock_time):
    total_seconds = 0
    minutes, seconds = clock_time.split(":")

    total_seconds += int(minutes) * 60
    total_seconds += float(seconds)

    return total_seconds


board = chess.Board()
player_color = 1 if 'ww' in input("What's your color? ") else -1
white_clock, black_clock = 60, 60
time.sleep(1)

while 1:
    try:
        if keyboard.is_pressed("Esc"):
            board = chess.Board()
            player_color = 1 if 'ww' in input("What's your color? ") else -1
            time.sleep(1)

        html = driver.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(html, features="lxml")

        clocks = soup.find_all("span", {"data-cy": "clock-time"})
        opponent_clock, player_clock = 1, 1
        if len(clocks) > 0:
            opponent_clock = parse_clock_time(clocks[0].contents[0])
            player_clock = parse_clock_time(clocks[1].contents[0])

            if player_color == 1:
                white_clock = player_clock
                black_clock = opponent_clock
            else:
                white_clock = opponent_clock
                black_clock = player_clock

        last_move_html = soup.find_all(
            "div", {"data-ply": f"{board.ply()+1}"})

        if len(last_move_html) > 0:
            last_move_html = last_move_html[0]
            lm_contents = last_move_html.contents

            last_move = None

            if len(lm_contents) == 1:
                last_move = lm_contents[0]

            elif len(lm_contents) == 2:
                if len(str(lm_contents[0])) > len(str(lm_contents[1])):
                    last_move = lm_contents[0]["data-figurine"] + \
                        lm_contents[1]
                else:
                    if "=" in str(lm_contents[0]):
                        last_move = lm_contents[0] + \
                            lm_contents[1]["data-figurine"]
                    else:
                        last_move = lm_contents[0]

            if last_move is not None:
                board.push_san(last_move)
                if board.turn == chess.WHITE and player_color == 1 or board.turn == chess.BLACK and player_color == -1:
                    best_move = engine.play(
                        board, chess.engine.Limit(white_clock=white_clock, black_clock=black_clock)).move
                    make_move_on_window(best_move, player_color)

    except Exception as e:
        print('\n')
        print(last_move_html)
        print(lm_contents)
        print(e)
        print('\nTerminating...')
        break

engine.quit()
driver.quit()
