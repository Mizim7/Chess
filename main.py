import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QInputDialog, QDialog, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QTextEdit)
from PyQt6.QtGui import QPainter, QColor, QPixmap, QPen
from PyQt6.QtCore import Qt, QSize
from PyQt6 import uic
import sqlite3
import datetime


class Piece:
    def __init__(self, x, y, color, image_path):
        self.x = x
        self.y = y
        self.color = color
        self.image = QPixmap(image_path)

    def draw(self, painter, square_size):
        """
        Рисует фигуру на доске.

        Args:
            painter (QPainter): Объект для рисования.
            square_size (int): Размер клетки доски.
        """
        scale_factor = 0.6
        image_size = int(square_size * scale_factor)
        painter.drawPixmap(
            self.x * square_size + (square_size - image_size) // 2,
            self.y * square_size + (square_size - image_size) // 2,
            image_size,
            image_size,
            self.image.scaled(image_size, image_size, Qt.AspectRatioMode.KeepAspectRatio)
        )

    def valid_moves(self, board):
        """Метод для получения допустимых ходов для фигуры.
        Переопределяется в наследниках.
        """
        return []


class King(Piece):
    def __init__(self, x, y, color):
        image_path = 'images/king_white.png' if color == 'white' else 'images/king_black.png'
        super().__init__(x, y, color, image_path)

    def valid_moves(self, board):
        """Возвращает все допустимые ходы для короля (на одну клетку в любом направлении)."""
        moves = []
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                target_piece = board.get_piece(new_x, new_y)
                if not target_piece or target_piece.color != self.color:  # Захват вражеской фигуры
                    moves.append((new_x, new_y))
        return moves


class Queen(Piece):
    def __init__(self, x, y, color):
        image_path = 'images/queen_white.png' if color == 'white' else 'images/queen_black.png'
        super().__init__(x, y, color, image_path)

    def valid_moves(self, board):
        moves = []
        # Все возможные направления движения королевы
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target_piece = board.get_piece(x, y)
                if target_piece:
                    if target_piece.color != self.color:  # Захват фигуры противника
                        moves.append((x, y))
                    break  # Прерываем движение, если есть фигура
                moves.append((x, y))
                x += dx
                y += dy

        return moves


class Bishop(Piece):
    def __init__(self, x, y, color):
        image_path = 'images/bishop_white.png' if color == 'white' else 'images/bishop_black.png'
        super().__init__(x, y, color, image_path)

    def valid_moves(self, board):
        moves = []
        # Все возможные направления движения слона
        directions = [
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target_piece = board.get_piece(x, y)
                if target_piece:
                    if target_piece.color != self.color:  # Захват фигуры противника
                        moves.append((x, y))
                    break  # Прерываем движение, если есть фигура
                moves.append((x, y))
                x += dx
                y += dy

        return moves


class Knight(Piece):
    def __init__(self, x, y, color):
        image_path = 'images/knight_white.png' if color == 'white' else 'images/knight_black.png'
        super().__init__(x, y, color, image_path)

    def valid_moves(self, board):
        moves = []
        # Все возможные ходы коня в виде смещений по осям x и y
        possible_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dx, dy in possible_moves:
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:  # Проверяем границы доски
                target_piece = board.get_piece(new_x, new_y)
                if not target_piece or target_piece.color != self.color:  # Захват вражеской фигуры
                    moves.append((new_x, new_y))
        return moves


class Rook(Piece):
    def __init__(self, x, y, color):
        image_path = 'images/rook_white.png' if color == 'white' else 'images/rook_black.png'
        super().__init__(x, y, color, image_path)

    def valid_moves(self, board):
        moves = []
        # Все возможные направления движения ладьи
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                target_piece = board.get_piece(x, y)
                if target_piece:
                    if target_piece.color != self.color:  # Захват фигуры противника
                        moves.append((x, y))
                    break  # Прерываем движение, если есть фигура
                moves.append((x, y))
                x += dx
                y += dy

        return moves


class Pawn(Piece):
    def __init__(self, x, y, color):
        image_path = 'images/pawn_white.png' if color == 'white' else 'images/pawn_black.png'
        super().__init__(x, y, color, image_path)
        self.has_moved = False

    def valid_moves(self, board):
        moves = []
        direction = 1 if self.color == 'white' else -1

        # Стандартный ход на одну клетку вперед
        if 0 <= self.y + direction < 8 and board.is_empty(self.x, self.y + direction):
            moves.append((self.x, self.y + direction))

        # Два клетки вперед только на начальной позиции
        if not self.has_moved and 0 <= self.y + 2 * direction < 8:
            if board.is_empty(self.x, self.y + direction) and board.is_empty(self.x, self.y + 2 * direction):
                moves.append((self.x, self.y + 2 * direction))

        # Захват по диагонали
        for dx in [-1, 1]:
            if 0 <= self.x + dx < 8 and 0 <= self.y + direction < 8:
                target_piece = board.get_piece(self.x + dx, self.y + direction)
                if target_piece and target_piece.color != self.color:  # Если на клетке вражеская фигура
                    moves.append((self.x + dx, self.y + direction))

        return moves


# Шахматная доска и логика игры
class ChessBoard(QMainWindow):
    """Основной класс для шахмат."""

    def __init__(self):
        super().__init__()
        uic.loadUi('Chess.ui', self)
        self.setFixedSize(QSize(920, 680))
        self.setWindowTitle('Шахматы')

        self.figures = []  # Список всех фигур на доске
        self.selected_figure = None  # Выбранная фигура
        self.current_player = 'white'  # Текущий игрок
        self.create_pieces()  # Инициализация фигур на доске
        self.highlighted_squares = set()  # Множество подсвеченных клеток
        self.play_again.clicked.connect(self.play_again_clicked)
        self.status_btn.clicked.connect(self.show_status_window)

        self.game_over = False  # Флаг окончания игры
        self.king_in_check = None  # Координаты короля, если он под шахом
        # Инициализация базы данных
        self.db = GameDatabase()

    def is_empty(self, x, y):
        for figure in self.figures:
            if figure.x == x and figure.y == y:
                return False  # клетка занята
        return True

    def get_piece(self, x, y):
        for piece in self.figures:
            if piece.x == x and piece.y == y:
                return piece
        return None

    def show_status_window(self):
        """Открывает окно с информацией о прошлых играх."""
        status_window = StatusWindow(self.db)
        status_window.exec()

    def play_again_clicked(self):
        # Запись в бд
        if self.StatusList.count() > 1:  # Только если в StatusList есть записи
            game_status = "\n".join([self.StatusList.item(i).text() for i in range(self.StatusList.count())])
            self.db.insert_game_record(game_status)

        # Создаем диалоговое окно с вопросом
        reply = QMessageBox.question(
            self, 'Начать заново?', 'Вы уверены, что хотите начать партию заново?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        # Если пользователь нажал "Yes"
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_game()
        else:
            # Если "No", просто закрываем окно
            pass

    def reset_game(self):
        """Метод для сброса игры: возвращаем все фигуры на свои исходные позиции."""
        # Очистить текущие фигуры с доски
        self.figures.clear()

        # Снова добавляем все фигуры на их начальные позиции
        self.create_pieces()  # Эта функция восстанавливает фигуры на начальной позиции

        # Сбросить текущего игрока
        self.current_player = 'white'  # Белые начинают

        # Очистить выделение и подсветку возможных ходов
        self.selected_figure = None
        self.highlighted_squares.clear()

        # Очищаем все элементы, начиная с второго
        for i in range(1, self.StatusList.count()):  # Пропускаем первую строку (индекс 0)
            self.StatusList.takeItem(1)

        # Очистить подсветку шаха
        self.king_in_check = None

        # Сбрасываем флаг окончания игры
        self.game_over = False

        # Обновить доску
        self.update()

    def create_pieces(self):
        piece_data = {
            'black': {
                'king': (4, 7, 'black'),
                'queen': (3, 7, 'black'),
                'bishop': [(2, 7, 'black'), (5, 7, 'black')],
                'pawn': [(i, 6, 'black') for i in range(8)],
                'knight': [(1, 7, 'black'), (6, 7, 'black')],
                'rook': [(0, 7, 'black'), (7, 7, 'black')]
            },
            'white': {
                'king': (4, 0, 'white'),
                'queen': (3, 0, 'white'),
                'bishop': [(2, 0, 'white'), (5, 0, 'white')],
                'pawn': [(i, 1, 'white') for i in range(8)],
                'knight': [(1, 0, 'white'), (6, 0, 'white')],
                'rook': [(0, 0, 'white'), (7, 0, 'white')]
            }
        }

        # Создаем фигуры на основе данных
        for color, pieces in piece_data.items():
            for piece_type, positions in pieces.items():
                if isinstance(positions, tuple):
                    piece_class = globals()[piece_type.capitalize()]
                    self.figures.append(piece_class(*positions))
                else:
                    piece_class = globals()[piece_type.capitalize()]
                    for pos in positions:
                        self.figures.append(piece_class(*pos))

    def paintEvent(self, event):
        """Отрисовка интерфейса."""
        painter = QPainter(self)
        size = self.size()
        square_size = min(size.width(), size.height()) // 8

        # Рисуем доску
        light_color = QColor(255, 252, 201)
        dark_color = QColor(99, 136, 100)

        for i in range(8):
            for j in range(8):
                color = light_color if (i + j) % 2 == 0 else dark_color
                painter.fillRect(j * square_size, i * square_size, square_size, square_size, color)

        # Рисуем фигуры
        for figure in self.figures:
            figure.draw(painter, square_size)

        # Подсветка рамок возможных ходов
        pen = QPen(QColor(255, 0, 0), 2)  # Красная рамка шириной 2 пикселя
        painter.setPen(pen)
        for x, y in self.highlighted_squares:
            painter.drawRect(x * square_size, y * square_size, square_size, square_size)

        # Подсветка короля, если он под шахом
        if self.king_in_check:
            pen = QPen(QColor(0, 0, 255), 2)  # Синяя рамка шириной 2 пикселя
            painter.setPen(pen)
            king_x, king_y = self.king_in_check
            painter.drawRect(king_x * square_size, king_y * square_size, square_size, square_size)

        # Рисуем координаты столбцов (a-h)
        text_pen = QPen(QColor(0, 0, 0))  # Черный цвет для текста
        painter.setPen(text_pen)
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        for col in range(8):
            letter = chr(ord('a') + col)  # Преобразуем индекс в букву (a-h)
            painter.drawText(col * square_size + square_size // 2 - 7, 15, letter)

        # Рисуем координаты рядов (1-8)
        for row in range(8):
            painter.drawText(10, row * square_size + square_size // 2 + 5, str(8 - row))  # Инвертируем ряды

    def mousePressEvent(self, event):
        """Обработчик нажатия."""
        if self.game_over:
            return  # Если игра окончена, блокируем взаимодействие с полем

        x, y = event.position().x(), event.position().y()
        square_size = min(self.size().width(), self.size().height()) // 8
        col = int(x // square_size)
        row = int(y // square_size)

        if self.selected_figure:
            if (col, row) in self.selected_figure.valid_moves(self):
                # Логика хода
                target_piece = self.get_piece(col, row)
                captured_piece = None  # Для захваченной фигуры

                if target_piece:
                    if target_piece.color != self.current_player:
                        captured_piece = target_piece  # Сохраняем захваченную фигуру
                        self.figures.remove(target_piece)  # Удаляем захваченную фигуру

                        # Добавление записи в StatusList
                        captured_piece_name = (f"{target_piece.color.capitalize()}_"
                                               f"{target_piece.__class__.__name__.lower()}")
                        self.StatusList.addItem(
                            f"{self.current_player.capitalize()}_{self.selected_figure.__class__.__name__.lower()} "
                            f"убил {captured_piece_name} -> {chr(ord('a') + col)}{8 - row}"
                        )

                # Проверяем, не подставил ли игрок своего короля под шах
                original_x, original_y = self.selected_figure.x, self.selected_figure.y  # Запоминаем исходную позицию
                self.selected_figure.x = col
                self.selected_figure.y = row

                # Проверка, не подставил ли игрок своего короля под шах после хода
                if self.is_in_check(self.current_player):
                    QMessageBox.warning(self, "Шах!", "Ваш король под угрозой!")
                    self.selected_figure.x, self.selected_figure.y = original_x, original_y  # Возвращаем фигуру
                    if captured_piece:
                        self.figures.append(captured_piece)  # Возвращаем захваченную фигуру

                    self.update()
                    return
                # Превращение пешки, если она дошла до конца поля
                if isinstance(self.selected_figure, Pawn):
                    self.selected_figure.has_moved = True
                    # Белая пешка на последней линии
                    if self.selected_figure.color == 'white' and self.selected_figure.y == 7:
                        piece_names = ['Queen', 'Rook', 'Bishop', 'Knight']
                        new_piece_name, ok = QInputDialog.getItem(self, "Выберите фигуру", "Преобразовать в:",
                                                                  piece_names, 0, False)
                        if ok:
                            # Создаем новую фигуру в зависимости от выбора
                            if new_piece_name == 'Queen':
                                new_piece = Queen(col, row, self.selected_figure.color)
                            elif new_piece_name == 'Rook':
                                new_piece = Rook(col, row, self.selected_figure.color)
                            elif new_piece_name == 'Bishop':
                                new_piece = Bishop(col, row, self.selected_figure.color)
                            else:
                                new_piece = Knight(col, row, self.selected_figure.color)

                            # Превращаем пешку в новую фигуру
                            self.figures.remove(self.selected_figure)  # Удаляем старую пешку
                            self.figures.append(new_piece)  # Добавляем новую фигуру
                            self.selected_figure = new_piece  # Устанавливаем новую фигуру как выбранную

                    # Черная пешка на последней линии
                    elif self.selected_figure.color == 'black' and self.selected_figure.y == 0:
                        piece_names = ['Queen', 'Rook', 'Bishop', 'Knight']
                        new_piece_name, ok = QInputDialog.getItem(self, "Выберите фигуру", "Преобразовать в:",
                                                                  piece_names, 0, False)
                        if ok:
                            # Создаем новую фигуру в зависимости от выбора
                            if new_piece_name == 'Queen':
                                new_piece = Queen(col, row, self.selected_figure.color)
                            elif new_piece_name == 'Rook':
                                new_piece = Rook(col, row, self.selected_figure.color)
                            elif new_piece_name == 'Bishop':
                                new_piece = Bishop(col, row, self.selected_figure.color)
                            else:
                                new_piece = Knight(col, row, self.selected_figure.color)

                            # Превращаем пешку в новую фигуру
                            self.figures.remove(self.selected_figure)  # Удаляем старую пешку
                            self.figures.append(new_piece)  # Добавляем новую фигуру
                            self.selected_figure = new_piece  # Устанавливаем новую фигуру как выбранную

                # Если шах противнику, подсветить его короля
                if self.is_in_check('black' if self.current_player == 'white' else 'white'):
                    QMessageBox.information(self, "Шах!", f"{self.current_player.capitalize()} угрожает королю шахом!")
                    self.StatusList.addItem(f"{self.current_player.capitalize()} ставит шах!")

                # Проверяем мат для противника
                opponent = 'black' if self.current_player == 'white' else 'white'
                if self.is_in_check(opponent) and self.checkmate(opponent):
                    QMessageBox.information(self, "Мат!", f"{self.current_player.capitalize()} победил!")
                    self.StatusList.addItem(f"{self.current_player.capitalize()} ставит мат!")
                    self.game_over = True  # Устанавливаем флаг окончания игры
                    return

                # Смена игрока
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                self.selected_figure = None
                self.highlighted_squares.clear()
                self.update()
            else:
                self.selected_figure = None
                self.highlighted_squares.clear()
                self.update()
        else:
            # Выбор фигуры
            for figure in self.figures:
                if figure.x == col and figure.y == row and figure.color == self.current_player:
                    self.selected_figure = figure
                    self.highlighted_squares = set(figure.valid_moves(self))
                    self.update()
                    break

    def checkmate(self, player):
        """Проверка на мат, после шаха."""
        if not self.is_in_check(player):
            return False  # Если нет шаха, то мата тоже нет

        # Проверяем все возможные ходы игрока
        for piece in self.figures:
            if piece.color == player:
                original_pos = (piece.x, piece.y)
                valid_moves = piece.valid_moves(self)

                for move in valid_moves:
                    target_piece = self.get_piece(*move)
                    # Выполняем временный ход
                    piece.x, piece.y = move
                    if target_piece:
                        self.figures.remove(target_piece)

                    # Проверяем, устраняет ли ход шах
                    if not self.is_in_check(player):
                        # Отменяем временный ход
                        piece.x, piece.y = original_pos
                        if target_piece:
                            self.figures.append(target_piece)
                        return False  # Найден ход, который устраняет шах

                    # Отменяем временный ход
                    piece.x, piece.y = original_pos
                    if target_piece:
                        self.figures.append(target_piece)

        # Если ни один ход не устраняет шах, это мат
        return True

    def is_in_check(self, color):
        """Проверка на шах."""
        # Находим короля текущего цвета
        king = next((figure for figure in self.figures if isinstance(figure, King) and figure.color == color), None)
        if not king:
            return False

        king_pos = (king.x, king.y)

        for piece in self.figures:
            if piece.color != color:  # Проверяем фигуры противника
                if king_pos in piece.valid_moves(self):  # Если угрожает
                    self.king_in_check = king_pos  # Сохраняем позицию короля
                    self.update()  # Обновляем доску для подсветки
                    return True

        self.king_in_check = None  # Если шаха нет, сбрасываем
        self.update()  # Обновляем доску
        return False


class GameDatabase:
    """Инициализация базы данных."""

    def __init__(self, db_name='chess_games.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_database()

    def create_database(self):
        """Создание таблицы для хранения истории партий, если она не существует."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT,
            game_status TEXT
        )
        """)
        self.conn.commit()

    def insert_game_record(self, game_status):
        """Запись информации."""
        if game_status:  # Записываем только если StatusList не пуст
            game_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO games (game_date, game_status) VALUES (?, ?)",
                                (game_date, game_status))
            self.conn.commit()

    def close(self):
        self.conn.close()


class StatusWindow(QDialog):
    """Класс для отображения информации с бд в новом окне"""
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("История игр")
        self.setGeometry(300, 200, 600, 500)

        # Основной макет
        layout = QVBoxLayout()

        # Таблица для отображения данных
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)  # Колонки: id, game_date, game_status
        self.table.setHorizontalHeaderLabels(["ID", "Дата игры", "Статус игры"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellClicked.connect(self.show_full_status)  # Обработчик кликов по ячейкам
        layout.addWidget(self.table)

        # Текстовый виджет для отображения полной информации
        self.full_status_text = QTextEdit(self)
        self.full_status_text.setReadOnly(True)
        layout.addWidget(self.full_status_text)

        self.setLayout(layout)

        # Загрузка данных из базы
        self.load_data(db)

    def load_data(self, db):
        """Получение данных из базы"""
        query = "SELECT id, game_date, game_status FROM games"
        db.cursor.execute(query)
        records = db.cursor.fetchall()

        # Установка количества строк
        self.table.setRowCount(len(records))

        # Заполнение таблицы
        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def show_full_status(self, row, column):
        """Отображает полный текст статуса из 3-й колонки."""
        if column == 2:  # Только для третьей колонки (индекс 2)
            full_status = self.table.item(row, column).text()
            self.full_status_text.setText(full_status)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ChessBoard()
    form.show()
    sys.exception = except_hook
    sys.exit(app.exec())
