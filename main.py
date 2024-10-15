from telethon import TelegramClient, events
from telethon import Button
import random

api_id = 10953300
api_hash = "9c24426e5d6fa1d441913e3906627f87"
bot_token = '7119660389:AAGICajl_7tCrV0tzIWyNtCopWvQ4jt6aVw'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

games = {}

def create_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def render_board(board):
    buttons = []
    for i in range(3):
        row_buttons = []
        for j in range(3):
            text = board[i][j] if board[i][j] != ' ' else '⬜️'
            row_buttons.append(Button.inline(text, data=f"{i},{j}"))
        buttons.append(row_buttons)
    return buttons

def check_winner(board):
    lines = (
        board +
        [[board[i][j] for i in range(3)] for j in range(3)] +
        [[board[i][i] for i in range(3)]] +
        [[board[i][2 - i] for i in range(3)]]
    )
    for line in lines:
        if line[0] != ' ' and all(cell == line[0] for cell in line):
            return line[0]
    return None

def is_draw(board):
    return all(cell != ' ' for row in board for cell in row)

def find_best_move(board, symbol):
    opponent_symbol = 'X' if symbol == 'O' else 'O'
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = symbol
                if check_winner(board) == symbol:
                    return (i, j)
                board[i][j] = ' '
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = opponent_symbol
                if check_winner(board) == opponent_symbol:
                    return (i, j)
                board[i][j] = ' '
    if board[1][1] == ' ':
        return (1, 1)
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']
    return random.choice(empty_cells) if empty_cells else None

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('X yoki O tanlang!', buttons=[
        [Button.inline('X', data='choose_x'),
         Button.inline('O', data='choose_o')]
    ])

@client.on(events.CallbackQuery(data='choose_x'))
async def choose_x(event):
    board = create_board()
    games[event.sender_id] = {'board': board, 'symbol': 'X', 'bot_symbol': 'O'}
    await event.respond('Siz X tanladingiz. O\'yin boshlanadi!', buttons=render_board(board))
    await event.delete()

@client.on(events.CallbackQuery(data='choose_o'))
async def choose_o(event):
    board = create_board()
    games[event.sender_id] = {'board': board, 'symbol': 'O', 'bot_symbol': 'X'}
    await event.respond('Siz O\'tanladingiz. O\'yin boshlanadi!', buttons=render_board(board))
    await event.delete()

@client.on(events.CallbackQuery)
async def handle_move(event):
    if event.sender_id not in games:
        await event.respond('O\'yin hali boshlanmadi. /start ni bosing!')
        return

    data = event.data.decode('utf-8')
    if data not in ['choose_x', 'choose_o']:
        try:
            x, y = map(int, data.split(','))
        except ValueError:
            await event.respond('Noto\'g\'ri harakat. Iltimos, boshqa joyni tanlang.')
            return

        game = games[event.sender_id]
        board = game['board']
        user_symbol = game['symbol']
        bot_symbol = game['bot_symbol']

        if board[x][y] == ' ':
            board[x][y] = user_symbol
        else:
            await event.respond('Bu joy band. Iltimos, boshqa joyni tanlang.')
            return

        winner = check_winner(board)
        if winner:
            await event.edit(f'{winner} yutdi! O\'yin tugadi.', buttons=[
                [Button.inline('Yana o\'ynash', data='restart')]
            ])
            del games[event.sender_id]
            return
        
        bot_move = find_best_move(board, bot_symbol)
        if bot_move:
            board[bot_move[0]][bot_move[1]] = bot_symbol

        winner = check_winner(board)
        if winner:
            await event.edit(f'{winner} yutdi! O\'yin tugadi.', buttons=[
                [Button.inline('Yana o\'ynash', data='restart')]
            ])
            del games[event.sender_id]
        elif is_draw(board):
            await event.edit('Durrang! O\'yin tugadi.', buttons=[
                [Button.inline('Yana o\'ynash', data='restart')]
            ])
            del games[event.sender_id]
        else:
            await event.edit('O\'yin davom etmoqda:', buttons=render_board(board))

@client.on(events.CallbackQuery(data='restart'))
async def restart_game(event):
    await start(event)

client.start()
client.run_until_disconnected()
