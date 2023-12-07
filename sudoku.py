import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

class UndoStack:
    def __init__(self):
        """Clase que implementa una pila para realizar deshacer."""
        self.stack = []

    def push(self, item):
        """Añade un estado al tope de la pila."""
        self.stack.append(item)

    def pop(self):
        """Elimina y devuelve el estado en el tope de la pila."""
        if self.stack:
            return self.stack.pop()

    def is_empty(self):
        """Verifica si la pila está vacía."""
        return not bool(self.stack)

    def print_stack(self):
        """Imprime la pila por consola."""
        print("Undo Stack:", self.stack)
        print()

class RedoStack:
    def __init__(self):
        """Clase que implementa una pila para realizar rehacer."""
        self.stack = []

    def push(self, item):
        """Añade un estado al tope de la pila."""
        self.stack.append(item)

    def pop(self):
        """Elimina y devuelve el estado en el tope de la pila."""
        if self.stack:
            return self.stack.pop()

    def is_empty(self):
        """Verifica si la pila está vacía."""
        return not bool(self.stack)

    def print_stack(self):
        """Imprime la pila por consola."""
        print("Redo Stack:", self.stack)
        print()

class SudokuGame:
    def __init__(self):
        """Clase principal que representa el juego de Sudoku."""
        self.root = tk.Tk()
        self.root.title("Sudoku")
        self.sudoku_board = [[0] * 9 for _ in range(9)]
        self.undo_stack = UndoStack()
        self.redo_stack = RedoStack()
        self.history = []
        self.create_widgets()

    def create_widgets(self):
        """Crea los widgets (etiquetas y botones) para la interfaz de usuario."""
        self.labels = []

        rows, cols = 9, 9
        cell_size = 40  # Ajusta el tamaño de la celda según tus necesidades

        for i in range(rows):
            row_labels = []
            for j in range(cols):
                label = tk.Label(self.root, text="", font=('Arial', 12), width=2, height=2, relief="ridge", borderwidth=1)
                label.grid(row=i, column=j, ipadx=cell_size, ipady=cell_size)
                label.bind("<Button-1>", lambda event, row=i, col=j: self.cell_clicked(row, col))
                row_labels.append(label)
            self.labels.append(row_labels)

        # Configurar colores de fondo y bordes para las regiones
        for i in range(0, rows, 3):
            for j in range(0, cols, 3):
                region_color = "lightgray" if (i // 3 + j // 3) % 2 == 0 else "white"
                for x in range(3):
                    for y in range(3):
                        label = self.labels[i + x][j + y]
                        label.config(bg=region_color, bd=2, relief="solid")

        # Hacer que la ventana sea cuadrada
        self.root.geometry(f"{cols * cell_size}x{rows * cell_size}")

        # Configurar filas y columnas de la ventana para que se expandan y centren
        for i in range(rows):
            self.root.grid_rowconfigure(i, weight=1)

        for j in range(cols):
            self.root.grid_columnconfigure(j, weight=1)

        # Añadir botones
        self.load_button = tk.Button(self.root, text="Cargar", width=10, height=1, command=self.load_board_from_file)
        self.load_button.grid(row=rows, column=0, columnspan=3)

        self.undo_button = tk.Button(self.root, text="Deshacer", width=10, height=1, command=self.undo)
        self.undo_button.grid(row=rows, column=3, columnspan=3)

        self.redo_button = tk.Button(self.root, text="Rehacer", width=10, height=1, command=self.redo)
        self.redo_button.grid(row=rows, column=6, columnspan=3)

        self.suggested_move_button = tk.Button(self.root, text="Sugerencia", width=10, height=1, command=self.suggested_move_button_click)
        self.suggested_move_button.grid(row=rows + 1, column=0, columnspan=3)

        self.view_moves_button = tk.Button(self.root, text="Ver Jugadas", width=10, height=1, command=self.view_moves)
        self.view_moves_button.grid(row=rows + 1, column=3, columnspan=3)

    def update_board(self):
        """Actualiza la interfaz gráfica del tablero de Sudoku."""
        for i in range(9):
            for j in range(9):
                value = self.sudoku_board[i][j]
                label = self.labels[i][j]
                label.config(text=str(value) if value != 0 else "")

    def load_board_from_file(self):
        """Carga un tablero de Sudoku desde un archivo de texto."""
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
        """Verifica si un movimiento es válido en el Sudoku."""
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
        """Registra un movimiento en el historial."""
        if action == "Nueva" and row is not None and col is not None and number is not None:
            self.history.append((action, row, col, number))
        elif action != "Nueva":
            self.history.append((action, row, col, number))

    def cell_clicked(self, row, col):
        """Maneja el evento de clic en una celda."""
        current_value = self.sudoku_board[row][col]
        user_input = simpledialog.askinteger("Ingresar número", f"Ingrese un número para la celda ({row}, {col}):", initialvalue=current_value, minvalue=0, maxvalue=9)

        if user_input is not None:
            if not self.is_valid_move(row, col, user_input):
                messagebox.showinfo("Advertencia", f"No se puede ingresar {user_input} en la fila, columna o región.")
            else:
                self.insert_number(row, col, user_input)
                self.record_move("Insertado", row, col, user_input)

    def insert_number(self, f, c, n):
        """Inserta un número en el tablero de Sudoku."""
        self.sudoku_board[f][c] = n
        self.undo_stack.push([row[:] for row in self.sudoku_board])
        self.update_board()

        if self.is_complete():
            messagebox.showinfo("Felicidades", "¡Sudoku completado!")

    def is_complete(self):
        """Verifica si el tablero de Sudoku está completo."""
        for i in range(9):
            for j in range(9):
                if self.sudoku_board[i][j] == 0:
                    return False
        return True

    def undo(self):
        """Deshace el último movimiento."""
        if self.undo_stack.is_empty():
            self.update_board()
            return

        previous_state = self.undo_stack.pop()
        if previous_state:
            self.sudoku_board = [row[:] for row in previous_state]
            self.redo_stack.push([row[:] for row in previous_state])
            self.update_board()
        if self.history:
            action, row, col, number = self.history[-1]
            self.update_board()
            if action == "Insertado":
                self.sudoku_board[row][col] = 0
                self.update_board()
            self.record_move("Deshacer", row, col, number)
        self.update_board()
        self.undo_stack.print_stack()
        self.redo_stack.print_stack()

    def redo(self):
        """Rehace el último movimiento deshecho."""
        if self.redo_stack.is_empty():
            self.update_board()
            return

        redo_state = self.redo_stack.pop()
        if redo_state:
            self.sudoku_board = [row[:] for row in redo_state]
            self.undo_stack.push([row[:] for row in redo_state])
            self.update_board()
            if self.history:
                action, row, col, number = self.history[-1]
                self.sudoku_board[row][col] = number
                self.record_move("Rehacer", row, col, number)
                self.update_board()
        self.update_board()
        self.undo_stack.print_stack()
        self.redo_stack.print_stack()

    def get_suggested_move(self):
        """Obtiene un movimiento sugerido para el Sudoku."""
        for i in range(9):
            for j in range(9):
                if self.sudoku_board[i][j] == 0:
                    for n in range(1, 10):
                        if self.is_valid_move(i, j, n):
                            return i, j, n
        return None

    def suggested_move_button_click(self):
        """Maneja el clic en el botón de sugerencia."""
        move = self.get_suggested_move()
        if move is not None:
            i, j, n = move
            self.insert_number(i, j, n)
            self.record_move("Sugerencia", i, j, n)

    def view_moves(self):
        """Muestra un cuadro de diálogo con el historial de movimientos."""
        moves_text = "\n".join([f"{action}: {number} en ({row}, {col})" if action != "Nueva" else f"{action} en ({row}, {col}) con {number}" for action, row, col, number in self.history])
        messagebox.showinfo("Historial de Jugadas", moves_text)

if __name__ == "__main__":
    game = SudokuGame()
    game.root.mainloop()