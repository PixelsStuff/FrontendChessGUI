import os
import pygame
import chess
import chess.pgn
from io import StringIO
import random
# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Chess Application")
fullscreen = False

# Chess setup
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  # Default FEN position
board = chess.Board(fen)  # Create a chess board from FEN
square_size = 70       # Size of each square on the board
board_size = square_size * 8  # Chessboard is 8x8 squares
margin_x, margin_y = 40, 20
backgroundcolor = pygame.Color("grey10")

# Colors
colors = [pygame.Color("white"), pygame.Color("cadetblue4")]

dot_color = pygame.Color("grey69")  # Transparent green

# Load chess piece images
piece_folder = "LiAlpha"  # Folder containing chess piece images
piece_images = {}

for file in os.listdir(piece_folder):
    if file.endswith(".png"):
        piece_name = file.split(".")[0]  # Extract the piece name (e.g., 'wP')
        piece_images[piece_name] = pygame.image.load(os.path.join(piece_folder, file))

class Piece:
    def __init__(self, color, type_, square):
        self.color = color  # 'w' or 'b'
        self.type = type_   # 'P', 'N', 'B', 'R', 'Q', or 'K'
        self.square = square  # Chess square index (0-63)
        self.image = piece_images[f"{color}{type_}"]  # Assign appropriate image
        self.dragging = False
        self.original_pos = None

    def draw(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            x = mouse_x - square_size // 2
            y = mouse_y - square_size // 2
        else:
            col = self.square % 8
            row = 7 - (self.square // 8)
            x = col * square_size + margin_x
            y = row * square_size + margin_y
        image = pygame.transform.scale(self.image, (square_size, square_size))
        screen.blit(image, (x, y))

# Initialize pieces from FEN
def create_pieces_from_fen(fen_string):
    pieces = []
    board = chess.Board(fen_string)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_color = 'w' if piece.color == chess.WHITE else 'b'
            pieces.append(Piece(piece_color, piece.symbol().upper(), square))
    return pieces

pieces = create_pieces_from_fen(fen)
selected_piece = None  # Currently selected piece

# Initialize PGN game
pgn_game = chess.pgn.Game()
node = pgn_game

# Draw the board and pieces
def draw_board():
    # Draw the chessboard
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            rect = pygame.Rect(col * square_size + margin_x, row * square_size + margin_y, square_size, square_size)
            pygame.draw.rect(screen, color, rect)

    # Highlight legal moves if a piece is selected
    if selected_piece:
        legal_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_piece.square]
        for square in legal_moves:
            col = square % 8
            row = 7 - (square // 8)
            x = col * square_size + square_size // 2 + margin_x
            y = row * square_size + square_size // 2 + margin_y
            pygame.draw.circle(screen, dot_color, (x, y), 10)

    # Draw the pieces
    for piece in pieces:
        piece.draw()

# Convert mouse position to chess square index
def get_square_from_mouse(pos):
    x, y = pos
    col = (x - margin_x) // square_size
    row = 7 - ((y - margin_y) // square_size)
    if 0 <= col < 8 and 0 <= row < 8:
        return row * 8 + col
    return None

def reset_board():
    global board, pieces, pgn_game, node
    board = chess.Board(fen)
    pieces = create_pieces_from_fen(fen)
    pgn_game = chess.pgn.Game()
    node = pgn_game

def piece_moved(move):
    global node
    node = node.add_variation(move)
    print(pgn_game)


def load_pgn(pgn_string):
    global board, pieces, pgn_game, node
    pgn_game = chess.pgn.read_game(StringIO(pgn_string))
    board = pgn_game.board()
    for move in pgn_game.mainline_moves():
        board.push(move)
    pieces = create_pieces_from_fen(board.fen())
    node = pgn_game



clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_f:  # Toggle fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                else:
                    screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
                fullscreen = not fullscreen
            elif event.key == pygame.K_m:  # Minimize
                pygame.display.iconify()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                square = get_square_from_mouse(event.pos)
                for piece in pieces:
                    if piece.square == square and board.piece_at(square):
                        selected_piece = piece
                        piece.dragging = True
                        piece.original_pos = piece.square
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and selected_piece:
                square = get_square_from_mouse(event.pos)
                if square is not None and chess.SQUARE_NAMES[square] in [move.uci()[2:] for move in board.legal_moves if move.from_square == selected_piece.square]:
                    move = chess.Move(selected_piece.square, square)
                    captured_piece = next((p for p in pieces if p.square == square), None)
                    if captured_piece:
                        pieces.remove(captured_piece)
                    board.push(move)
                    selected_piece.square = square
                    piece_moved(move)
                else:
                    selected_piece.square = selected_piece.original_pos
                selected_piece.dragging = False
                selected_piece = None

        elif event.type == pygame.MOUSEMOTION:
            if selected_piece and selected_piece.dragging:
                mouse_x, mouse_y = event.pos

    screen.fill(backgroundcolor)  # Clear the screen
    draw_board()            # Draw the chessboard and pieces
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
