import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

class UndoStack:
    def __init__(self):
        # Clase para gestionar una pila de deshacer
        self.stack = []

    def push(self, item):
        # Agregar un estado a la pila de deshacer
        self.stack.append(item)

    def pop(self):
        # Deshacer la última acción y devolver el estado anterior
        if self.stack:
            return self.stack.pop()

    def is_empty(self):
        # Verificar si la pila de deshacer está vacía
        return not bool(self.stack)

class SudokuGame:
    def __init__(self):
        # Configuración inicial del juego
        self.root = tk.Tk()
        self.root.title("Sudoku")
        self.sudoku_board = [[0] * 9 for _ in range(9)]
        self.undo_stack = UndoStack()
        self.history = []  # Historial de jugadas
        self.create_widgets()

    def create_widgets(self):
        # Crear la interfaz gráfica del juego
        self.labels = []

        for i in range(9):
            row_labels = []
            for j in range(9):
                label = tk.Label(self.root, text="", width=2, height=2, relief="ridge", borderwidth=1)
                label.grid(row=i, column=j)
                label.bind("<Button-1>", lambda event, row=i, col=j: self.cell_clicked(row, col))
                row_labels.append(label)
            self.labels.append(row_labels)

        self.load_button = tk.Button(self.root, text="Cargar", width=10, height=1, command=self.load_board_from_file)
        self.load_button.grid(row=10, column=0, columnspan=3)

        self.undo_button = tk.Button(self.root, text="Deshacer", width=10, height=1, command=self.undo)
        self.undo_button.grid(row=10, column=3, columnspan=3)

        self.redo_button = tk.Button(self.root, text="Rehacer", width=10, height=1, command=self.redo)
        self.redo_button.grid(row=10, column=6, columnspan=3)

        self.suggested_move_button = tk.Button(self.root, text="Sugerencia", width=10, height=1, command=self.suggested_move_button_click)
        self.suggested_move_button.grid(row=11, column=0, columnspan=3)

        self.view_moves_button = tk.Button(self.root, text="Ver Jugadas", width=10, height=1, command=self.view_moves)
        self.view_moves_button.grid(row=11, column=3, columnspan=3)

    def update_board(self):
        # Actualizar la interfaz gráfica del tablero
        for i in range(9):
            for j in range(9):
                value = self.sudoku_board[i][j]
                self.labels[i][j].config(text=str(value) if value != 0 else "")

    def load_board_from_file(self):
        # Cargar un tablero de Sudoku desde un archivo
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.sudoku_board = []
                for line in file:
                    row = [int(num) if num.isdigit() else 0 for num in line.strip().replace('-', '0')]
                    self.sudoku_board.append(row)
            self.undo_stack.push([row[:] for row in self.sudoku_board])
            self.update_board()

    def is_valid_move(self, f, c, n):
        # Verificar si un movimiento es válido en una posición específica
        for i in range(9):
            if self.sudoku_board[f][i] == n or self.sudoku_board[i][c] == n:
                return False
        x = f // 3 * 3
        y = c // 3 * 3
        for i in range(x, x + 3):
            for j in range(y, y + 3):
                if self.sudoku_board[i][j] == n:
                    return False
        return True

    def record_move(self, action, row, col, number):
        # Registrar un movimiento en el historial
        if action == "Nueva" and row is not None and col is not None and number is not None:
            self.history.append((action, row, col, number))
        elif action != "Nueva":
            self.history.append((action, row, col, number))

    def cell_clicked(self, row, col):
        # Manejar el clic en una celda del tablero
        current_value = self.sudoku_board[row][col]
        user_input = simpledialog.askinteger("Ingresar número", f"Ingrese un número para la celda ({row}, {col}):", initialvalue=current_value, minvalue=0, maxvalue=9)

        if user_input is not None:
            if not self.is_valid_move(row, col, user_input):
                messagebox.showinfo("Advertencia", f"No se puede ingresar {user_input} en la fila, columna o región.")
            else:
                self.insert_number(row, col, user_input)
                self.record_move("Insertado", row, col, user_input)

    def insert_number(self, f, c, n):
        # Insertar un número en el tablero
        self.sudoku_board[f][c] = n
        self.undo_stack.push([row[:] for row in self.sudoku_board])
        self.update_board()

        if self.is_complete():
            messagebox.showinfo("Felicidades", "¡Sudoku completado!")

    def is_complete(self):
        # Verificar si el tablero está completo
        for i in range(9):
            for j in range(9):
                if self.sudoku_board[i][j] == 0:
                    return False
        return True

    def undo(self):
        # Deshacer la última acción
        if self.undo_stack.is_empty():
            return

        previous_state = self.undo_stack.pop()
        if previous_state:
            self.sudoku_board = [row[:] for row in previous_state]

        if self.history:
            # Obtén la última jugada sin eliminarla del historial
            action, row, col, number = self.history[-1]

            # Actualiza el estado del tablero solo si es una nueva inserción
            if action == "Insertado":
                self.sudoku_board[row][col] = 0

            self.record_move("Deshacer", row, col, number)
        self.update_board()

    def redo(self):
        # Rehacer la última acción deshecha
        if self.undo_stack.is_empty():
            return

        # Obtener el estado anterior al deshacer
        previous_state = self.undo_stack.stack[-1]

        # Deshacer una vez más para obtener la jugada original
        redo_state = self.undo_stack.pop()

        if redo_state:
            self.sudoku_board = [row[:] for row in redo_state]

            # Asegurarse de que haya jugadas en el historial
            if self.history:
                # Extraer la última jugada del historial
                action, row, col, number = self.history[-1]

                # Actualizar el estado del tablero y el historial
                self.sudoku_board[row][col] = number
                self.record_move("Rehacer", row, col, number)
        self.update_board()

    def get_suggested_move(self):
        # Obtener una sugerencia de movimiento
        for i in range(9):
            for j in range(9):
                if self.sudoku_board[i][j] == 0:
                    for n in range(1, 10):
                        if self.is_valid_move(i, j, n):
                            return i, j, n
        return None

    def suggested_move_button_click(self):
        # Manejar el clic en el botón de sugerencia
        move = self.get_suggested_move()
        if move is not None:
            i, j, n = move
            self.insert_number(i, j, n)
            self.record_move("Sugerencia", i, j, n)

    def view_moves(self):
        # Mostrar el historial de jugadas
        moves_text = "\n".join([f"{action}: {number} en ({row}, {col})" if action != "Nueva" else f"{action} en ({row}, {col}) con {number}" for action, row, col, number in self.history])
        messagebox.showinfo("Historial de Jugadas", moves_text)

if __name__ == "__main__":
    # Iniciar el juego
    game = SudokuGame()
    game.root.mainloop()
