import pygame, copy
from threading import Thread
from pygame.locals import *
pygame.init()


class Color():
    orange = (255, 90, 0)
    gray = (42, 42, 46)
    light_blue = (0, 195, 255)

# classe qui gère la maniplulation des fichiers
class FileManager():
    contenu = ""
    values = []
    height = width = 0
    
    def start():
        FileManager.open()
        FileManager.set_size()

    def open():
        global contenu, values
        contenu = open("data/sudoku.txt", "r").read().split("\n")
        values = []

    def set_size():
        global width, height, contenu
        width = len(contenu[0])
        height = len(contenu)
      
    def get_size():
        global width, height
        return [width, height]

    @staticmethod
    def get_contenu():
        global contenu
        return contenu

    # récupère les 9 différentes valeurs déjà présente dans le fichiers (chiffre, lettre, etc)
    def get_values():
        global values
        for n_line in range(len(contenu)):
            for n_col in range(len(contenu[0])):
                if contenu[n_line][n_col] not in values and contenu[n_line][n_col] != "_":
                    values.append(contenu[n_line][n_col])
        return values
    
# classe qui gère l'affichage avec pygame
class Affichage():
    
    def __init__(self, w, h, start_matrice):
        pygame.display.set_caption('Sudoku solver')
        self.margin = 2
        self.screen_width = w
        self.screen_height = h
        self.case_width = self.case_height = (w/9)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)
        self.screen = pygame.display.set_mode((w, h))
        self.start_matrice = start_matrice
        self.set_background()
        
    # set background / set cases
    def set_background(self):
        self.screen.fill(Color.gray)
        for n_line in range(9):
            for n_col in range(9):
                rect = pygame.Rect([self.case_width*n_col, self.case_height*n_line, self.case_width-self.margin, self.case_height-self.margin])
                pygame.draw.rect(self.screen, Color.light_blue, rect)
        pygame.draw.rect(self.screen, Color.gray, [0, 3*self.case_height, self.screen_width, self.case_height*.025])
        pygame.draw.rect(self.screen, Color.gray, [0, 6*self.case_height, self.screen_width, self.case_height*.025])
        pygame.draw.rect(self.screen, Color.gray, [3*self.case_width, 0, self.case_width*.025, self.screen_height])
        pygame.draw.rect(self.screen, Color.gray, [6*self.case_width, 0, self.case_width*.025, self.screen_height])
        pygame.display.update()
        self.update(self.start_matrice)

    def update(self, board):
        for n_line in range(9):
            for n_col in range(9):
                if str(board[n_line][n_col]) == "_":
                    continue
                if str(board[n_line][n_col]) == self.start_matrice[n_line][n_col]:
                    current_color = Color.orange
                else:
                    current_color = Color.gray
                text = self.font.render(board[n_line][n_col], True, current_color)
                textpos = text.get_rect().move(n_col*self.case_width + self.case_width/2 - text.get_width()/2, n_line*self.case_height + self.case_height/2 - text.get_height()/2)
                self.screen.blit(text, textpos)
                pygame.display.update()
                pygame.time.wait(15)
      
# classe qui gère le jeu en lui même
class Jeu:
    
    def __init__(self):
        self.width, self.height = FileManager.get_size()
        self.start_matrice = [["_"] * self.width for i in range(self.height)]
        self.contenu = FileManager.get_contenu()
        self.set_matrice()

    # définit la matrice de base. (0 -> case vide)
    def set_matrice(self):
        for n_line in range(self.height):
            for n_col in range(self.width):
                self.start_matrice[n_line][n_col] = self.contenu[n_line][n_col]

    # vérifie si le jeu est terminé
    @staticmethod
    def check_end(matrice):
        value = 0
        for n_line in range(height):
            for n_col in range(width):
                if matrice[n_line][n_col] == "_":
                    return False
                else:
                    value += matrice[n_line][n_col]
            if value != 45:
                return False

        return True

# classe qui gère l'IA
class AI:

    def __init__(self, width, height, values):
        self.width = width
        self.height = height
        self.solved_matrice = []
        self.values = values
        self.solved_moves = []

    def think(self, matrice):
        if self.solve(matrice):
            print("Board résolu: ")
            return True
        else:
            print("Board pas résolu.")
            return False

    # parcours toutes les cases (vides) et définit leur valeur, si il n'existe pas de valeur valide pour la case
    # le programme retourne en arrière de la ligne jusqu'a ce qu'il trouve la solution
    def solve(self, prev_board, n_line=0, n_col=0):
        board = copy.deepcopy(prev_board) # copie non mutable
        next_n_line, next_n_col = self.get_next_pos(n_line, n_col)               
        
        if n_line == 9: # fin
            global solved_matrice
            self.solved_matrice = board
            return True

        if board[n_line][n_col] == "_": # on doit modifier la valeur
            for i in range(0, 9):
                current_value = self.values[i]
                if self.is_position_valid(board, n_line, n_col, current_value): # on check si la valeur est ok a cet emplacement
                    board[n_line][n_col] = current_value
                    if self.solve(board, next_n_line, next_n_col): # recursion
                        self.solved_moves.append(board)
                        return True
                    board[n_line][n_col] = "_" # pas de valeur valide, retour en arrière
        else:
            if self.solve(board, next_n_line, next_n_col): # recursion
                self.solved_moves.append(board)
                return True
            board[n_line][n_col] = "_"

    # retourne la valeur suivante a check
    def get_next_pos(self, n_line, n_col):
        n_col += 1
        if n_col == 9:
            n_line += 1
            n_col = 0
        return n_line, n_col

    # verifie si on peut jouer sur cette case selon les règles du sudoku
    def is_position_valid(self, board, n_line, n_col, num):
        # Colonne
        # On vérifie que la ligne n'inclue pas deja cette valeur
        for ni_col in range(self.width): 
            if board[n_line][ni_col] == num:
                return False
        # Ligne
        # On vérifie que la colonne n'inclue pas deja cette valeur
        for ni_line in range(self.height): 
            if board[ni_line][n_col] == num:
                return False

        # Bloc
        # On vérifie que le bloc (3x3) n'inclut pas deja cette valeur
        # region bloc
        start_pos = [0, 0] # position du milieu du bloc [x, y]
        if n_line <= 2:
            start_pos[0] = 0
        elif n_line <= 5:
            start_pos[0] = 3
        else:
            start_pos[0] = 6

        if n_col <= 2:
            start_pos[1] = 0
        elif n_col <= 5:
            start_pos[1] = 3
        else:
            start_pos[1] = 6

        for ni_line in range(3):
            for ni_col in range(3):
                if board[start_pos[0]+ni_line][start_pos[1]+ni_col] == num:
                    return False

        # endregion

        return True
  
# classe (mère) qui gère l'avancement du programme
class SudokuManager:

    def __init__(self):
        FileManager.start()
        self.width, self.height = FileManager.get_size()
        self.jeu = Jeu()
        self.affichage = Affichage(900, 900, self.jeu.start_matrice)
        self.AI = AI(self.width, self.height, FileManager.get_values())
        thread = Thread(target=self.computing) # nouveau thread sur la gestion des calculs de l'IA
        thread.start()
        thread.join() # on attend le thread
        self.start()

    def start(self):
        self.run = True
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    pygame.display.quit()
                    pygame.quit()
                    exit(0)

    def computing(self):
        if self.AI.think(self.jeu.start_matrice):
            self.display(self.AI.solved_matrice, self.jeu.start_matrice)
            self.affichage.update(self.AI.solved_matrice)
    # Affichage dans la console
    def display(self, solved_board, base_board):
        for n_line in range(self.height):
            line = ""
            symb = ""
            for n_col in range(self.width):
                if n_col < self.width-1:
                    line += " | " + solved_board[n_line][n_col]
                else:
                    line += " | " + solved_board[n_line][n_col] + " |"
                symb += "   "
                if solved_board[n_line][n_col] == base_board[n_line][n_col]:
                    symb += "¯"
                else:
                    symb += " "
            if n_line == 0:
                print("")

            print(line)
            print(symb)

SM = SudokuManager()
