import os
import random
import sys
import time
import threading
import copy
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QSound

from Dialog import *
from output import Ui_tictactoe


class Game(QMainWindow, Ui_tictactoe):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.turn = None
        self.timer = QTimer()
        
        # Shows only the close button
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.sounds = dict(circle=QSound("circle.wav"),
                           cross=QSound("cross.wav"),
                           win=QSound("win.wav"),
                           lose=QSound("lose.wav"))

        xIconPath = os.path.join("Icons", "x.png")
        oIconPath = os.path.join("Icons", "o.png")
        
        self.xIcon = QIcon(xIconPath)
        self.oIcon = QIcon(oIconPath)

        # To make the icons appear in full color while disabled
        self.xIcon.addPixmap(QPixmap(xIconPath), QIcon.Disabled)
        self.oIcon.addPixmap(QPixmap(oIconPath), QIcon.Disabled)

        self.allButtons = self.frame.findChildren(QToolButton)
        self.availabeButtons = self.allButtons[:]
        self.defaultPalette = QApplication.palette()
        
        self.buttonGroup1 = [
            self.button1, self.button2, self.button3]

        # across the middle
        self.buttonGroup2 = [
            self.button4, self.button5, self.button6]

        # across the bottom
        self.buttonGroup3 = [
            self.button7, self.button8, self.button9]

        # down the left side
        self.buttonGroup4 = [
            self.button1, self.button4, self.button7]

        # down the middle
        self.buttonGroup5 = [
            self.button2, self.button5, self.button8]

        # down the right side
        self.buttonGroup6 = [
            self.button3, self.button6, self.button9]

        # diagonal
        self.buttonGroup7 = [
            self.button1, self.button5, self.button9]

        # diagonal
        self.buttonGroup8 = [
            self.button3, self.button5, self.button7]

        # connections
        for button in self.allButtons:
            button.clicked.connect(self.hum_play)

        self.actionNew_Game.triggered.connect(self.new_game)
        self.actionDark_Theme.toggled.connect(self.dark_theme)
        self.action_Exit.triggered.connect(self.close)
        self.comboBox.currentIndexChanged.connect(self.combo)

        self.com = ai(self)

        self.setFocus()  # sets the focus to the main window
        self.new_game()  # starts a new game

        self.timer.setInterval(50)
        self.timer.timeout.connect(self.tot_timer)
        self.timer.start()

    def combo(self,i):
        if i==0:
            self.com.set_algorithm(self.com.max_alpha_beta,[-2,2])
        elif i==1:
            self.com.set_algorithm(self.com.max,[])
        elif i==2:
            self.com.set_algorithm(self.com.a_star,[self.com.h1])
        elif i==3:
            self.com.set_algorithm(self.com.a_star,[self.com.h2])
        elif i==4:
            self.com.set_algorithm(self.com.a_star,[self.com.h3])
        elif i==5:
            self.com.set_algorithm(self.com.a_star,[self.com.h4])
        elif i==6:
            self.com.set_algorithm(self.com.a_star,[self.com.hybrid])
        else:
            print(i)

    def tot_timer(self):
        delta= time.time()-self.start_time
        if not (self.is_end() or len(self.availabeButtons)==0):
            self.total_timer.setText("Game timer: %.2f S" % delta)

    def new_game(self):
        self.reset()
        if self.start_AI.isChecked():
            self.com_play()
            self.turn = 2
        else:
            self.turn = 1

    def reset(self):
        self.turn = None
        self.Hum_timer.setText("Human timer: 0 S")
        self.AI_timer.setText("AI timer: 0 S")
        self.start_time=time.time()
        self.ai_timer=0
        self.frame.setEnabled(True)
        self.availabeButtons = self.allButtons[:]

        for button in self.availabeButtons:
            button.setText("")
            button.setIcon(QIcon())
            button.setEnabled(True)

    def is_end(self):
        if (self.check_list(self.buttonGroup1) or self.check_list(self.buttonGroup2) or
            self.check_list(self.buttonGroup3) or self.check_list(self.buttonGroup4) or
            self.check_list(self.buttonGroup5) or self.check_list(self.buttonGroup6) or
            self.check_list(self.buttonGroup7) or self.check_list(self.buttonGroup8)):
            return True
        else:
            return False

    def check(self):
        if self.is_end():
            return self.end_game(self.turn)

    def check_list(self, lst):
        for member in lst:
            if member.text() != str(self.turn):
                return False
        return True

    def end_game(self, state):
        """Ends the game"""

        if state == 1:
            self.sounds["win"].play()
            Dialog(self, state).show()

            for button in self.availabeButtons:
                button.setEnabled(False)
            self.availabeButtons.clear()
            return True

        elif state == 2:
            self.sounds["lose"].play()
            Dialog(self, state).show()

            for button in self.availabeButtons:
                button.setEnabled(False)
            self.availabeButtons.clear()
            return True

        elif state == 3:
            Dialog(self, state).show()

            for button in self.allButtons:
                button.setEnabled(False)
            return True
        return False

    def hum_play(self):
        button = self.sender()

        self.sounds["cross"].play()

        button.setText("1")
        button.setIcon(self.xIcon)
        button.setEnabled(False)
        self.availabeButtons.remove(button)
        if self.check():
            return

        self.turn = 2
        self.frame.setEnabled(False)

        delta=time.time()-self.start_time-self.ai_timer
        self.Hum_timer.setText("Human timer: %.2f S" % delta)
        self.timer.singleShot(400, self.com_play)

    def com_play(self):
        if len(self.availabeButtons)>0:
            before_time=time.time()
            best_button = self.com.best_move()
            self.ai_timer+=time.time()-before_time
            self.AI_timer.setText("AI timer: %.8f S" % self.ai_timer)
        else:
            self.turn = 3
            self.end_game(self.turn)
            return

        self.sounds["circle"].play()
        best_button.setText("2")
        best_button.setIcon(self.oIcon)
        best_button.setEnabled(False)
        self.availabeButtons.remove(best_button)
        if len(self.availabeButtons)==0:
            self.turn=3
            self.end_game(self.turn)
            return
        if self.check():
            return
        self.frame.setEnabled(True)
        self.turn = 1

    def dark_theme(self):
        """Changes the theme between dark and normal"""
        if self.actionDark_Theme.isChecked():
            QApplication.setStyle(QStyleFactory.create("Fusion"))
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(15, 15, 15))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(0, 24, 193).lighter())
            palette.setColor(QPalette.HighlightedText, Qt.black)
            palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
            palette.setColor(
                QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
            app.setPalette(palette)
            return

        app.setPalette(self.defaultPalette)

class ai():
    def __init__ (self,game):
        self.game=game
        self.current_state=[['0','1','3'],
                            ['0','1','3'],
                            ['0','1','3']]
        self.set_algorithm(self.max_alpha_beta,[-2,2])

    def set_algorithm(self,algorithm,args):
        self.algorithm=algorithm
        self.alg_args=args
    
    def is_end(self):
        for i in range(0, 3):
            if (self.current_state[0][i] != '.' and
                self.current_state[0][i] == self.current_state[1][i] == self.current_state[2][i]):
                return self.current_state[0][i]

        for i in range(0, 3):
            if (self.current_state[i] == ['X', 'X', 'X']):
                return 'X'
            elif (self.current_state[i] == ['O', 'O', 'O']):
                return 'O'

        if (self.current_state[0][0] != '.' and
            self.current_state[0][0] == self.current_state[1][1] == self.current_state[2][2]):
            return self.current_state[0][0]

        if (self.current_state[0][2] != '.' and
            self.current_state[0][2] == self.current_state[1][1] == self.current_state[2][0]):
            return self.current_state[0][2]

        for i in range(0, 3):
            for j in range(0, 3):
                if (self.current_state[i][j] == '.'):
                    return None
        return '.'
        
    def update_state(self):
        self.matrix = [self.game.buttonGroup1, self.game.buttonGroup2, self.game.buttonGroup3]
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if col.text() == '1': #human
                    self.current_state[i][j] = 'X'
                elif col.text() == '2': #ai
                    self.current_state[i][j] = 'O'
                else: #3 eq
                    self.current_state[i][j] = '.'

    def min(self):

        minv = 2
        qx = None
        qy = None

        result = self.is_end()

        if result == 'X': # -1 - win
            return (-1, 0, 0)
        elif result == 'O': # 1  - loss
            return (1, 0, 0)
        elif result == '.': # 0  - draw
            return (0, 0, 0)

        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    self.current_state[i][j] = 'X'
                    (m, max_i, max_j) = self.max()
                    if m < minv:
                        minv = m
                        qx = i
                        qy = j
                    self.current_state[i][j] = '.'

        return (minv, qx, qy)

    def max(self):

        maxv = -2
        px = None
        py = None

        result = self.is_end()

        if result == 'X': # -1 - loss
            return (-1, 0, 0)
        elif result == 'O': # 1  - win
            return (1, 0, 0)
        elif result == '.': # 0  - draw
            return (0, 0, 0)

        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    self.current_state[i][j] = 'O'
                    (m, min_i, min_j) = self.min()
                    if m > maxv:
                        maxv = m
                        px = i
                        py = j
                    self.current_state[i][j] = '.'
        return (maxv, px, py)

    def max_alpha_beta(self, alpha, beta):
        maxv = -2
        px = None
        py = None

        result = self.is_end()

        if result == 'X': # -1 - loss
            return (-1, 0, 0)
        elif result == 'O': # 1  - win
            return (1, 0, 0)
        elif result == '.': # 0  - draw
            return (0, 0, 0)

        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    self.current_state[i][j] = 'O'
                    (m, min_i, in_j) = self.min_alpha_beta(alpha, beta)
                    if m > maxv:
                        maxv = m
                        px = i
                        py = j
                    self.current_state[i][j] = '.'

                    if maxv >= beta:
                        return (maxv, px, py)

                    if maxv > alpha:
                        alpha = maxv

        return (maxv, px, py)
    
    def min_alpha_beta(self, alpha, beta):
    
        minv = 2

        qx = None
        qy = None

        result = self.is_end()

        if result == 'X': # -1 - win
            return (-1, 0, 0)
        elif result == 'O': # 1  - loss
            return (1, 0, 0)
        elif result == '.': # 0  - draw
            return (0, 0, 0)

        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    self.current_state[i][j] = 'X'
                    (m, max_i, max_j) = self.max_alpha_beta(alpha, beta)
                    if m < minv:
                        minv = m
                        qx = i
                        qy = j
                    self.current_state[i][j] = '.'

                    if minv <= alpha:
                        return (minv, qx, qy)

                    if minv < beta:
                        beta = minv

        return (minv, qx, qy)

    def getBestChild(self,h):
        h_best = -1
        empty=[]
        for i in range(0,3):
            for j in range(0,3):
                if self.current_state[i][j] == '.':
                    empty.append((i,j))
        for k in empty:
            i,j=k
            h_state=h(i,j)
            if h_state >= h_best:
                x,y = i,j
                h_best = h_state
            elif h_state< -1:
                (z,x,y) = self.max_alpha_beta(-2,2)
                return x,y

        return x,y

    def h1(self,i,j):
        count = 0
        trans_node = np.array(self.current_state).transpose().tolist()
        lines=[self.current_state[i],trans_node[j]]
        if [i,j] == [[0,0],[1,1],[2,2]]:
            lines+=[[self.current_state[0][0], self.current_state[1][1], self.current_state[2][2]]]
        if [i,j] == [[2,0],[1,1],[2,0]]:
            lines+=[[self.current_state[0][2], self.current_state[1][1], self.current_state[2][0]]]

        count += lines.count(['.','.','.'])
        count += 10 * (lines.count(['X','X','.'])+ lines.count(['X','.','X']) + lines.count(['.','X','X']))
        return count

    def h2(self,i,j):
        count = 0
        trans_node = np.array(self.current_state).transpose().tolist()
        lines=[self.current_state[i],trans_node[j]]
        if [i,j] == [[0,0],[1,1],[2,2]]:
            lines+=[[self.current_state[0][0], self.current_state[1][1], self.current_state[2][2]]]
        if [i,j] == [[2,0],[1,1],[2,0]]:
            lines+=[[self.current_state[0][2], self.current_state[1][1], self.current_state[2][0]]]

        count += lines.count(['.','.','.'])

        count -= lines.count(['X','.','.']) + lines.count(['.','X','.']) + lines.count(['.','.','X'])

        count += 10 * (lines.count(['O','.','.']) + lines.count(['.','O','.']) + lines.count(['.','.','O']))

        count += 100 * (lines.count(['X','X','.']) + lines.count(['X','.','X']) + lines.count(['.','X','X']))
        
        count += 1000*(lines.count(['O','O','.'])+ lines.count(['O','.','O']) + lines.count(['.','O','O']))
        
        return count

    def h3(self,i,j):
        count = 0
        trans_node = np.array(self.current_state).transpose().tolist()
        lines=[self.current_state[i],trans_node[j]]
        if [i,j] == [[0,0],[1,1],[2,2]]:
            lines+=[[self.current_state[0][0], self.current_state[1][1], self.current_state[2][2]]]
        if [i,j] == [[2,0],[1,1],[2,0]]:
            lines+=[[self.current_state[0][2], self.current_state[1][1], self.current_state[2][0]]]
        
        count += 10 * (lines.count(['O','.','.']) + lines.count(['.','O','.']) + lines.count(['.','.','O']))

        count += 100 * (lines.count(['X','X','.']) + lines.count(['X','.','X']) + lines.count(['.','X','X']))
        
        count += 1000 * (lines.count(['O','O','.'])+ lines.count(['O','.','O']) + lines.count(['.','O','O']))

        return count

    def h4(self,i,j):
        arr_node=np.array(self.current_state)
        flat_node=np.array(self.current_state).flatten().tolist()
        trans_node = np.array(self.current_state).transpose().tolist()
        lines=[self.current_state[i],trans_node[j]]
        if [i,j] == [[0,0],[1,1],[2,2]]:
            lines+=[[self.current_state[0][0], self.current_state[1][1], self.current_state[2][2]]]
        if [i,j] == [[2,0],[1,1],[2,0]]:
            lines+=[[self.current_state[0][2], self.current_state[1][1], self.current_state[2][0]]]

        if flat_node.count('.') == 9:
            if [i,j] == [0,0]:
                return 1
            else:
                return 0
        elif flat_node.count('.') == 8:
            if 'X' in [self.current_state[0][0],self.current_state[0][2],self.current_state[2][0],self.current_state[2][2]]:
                if [i,j] == [1,1]:
                    return 1
                else:
                    return 0
            elif 'X' in [self.current_state[1][1],self.current_state[1][0],self.current_state[1][2],self.current_state[0][1],self.current_state[2][0]]:
                if [i,j] == [0,0]:
                    return 1
                else:
                    return 0
        elif ['O','O','.'] in lines or ['O','.','O'] in lines or ['.','O','O'] in lines:
            return 1000
        elif ['X','X','.'] in lines or ['X','.','X'] in lines or ['.','X','X'] in lines:
            return 100
        elif ['O','.','.'] in lines or ['.','O','.'] in lines or ['.','.','O'] in lines:
            return 10

        count=0
        for i in lines:
            if 'O' in i and "X" not in i:
                count += 1
            if 'O' not in i and "X" in i:
                count -= 1
        return count

    def hybrid(self,i,j):
        arr_node=np.array(self.current_state)
        flat_node=np.array(self.current_state).flatten().tolist()
        trans_node = np.array(self.current_state).transpose().tolist()
        lines=[self.current_state[i],trans_node[j]]
        if [i,j] == [[0,0],[1,1],[2,2]]:
            lines+=[[self.current_state[0][0], self.current_state[1][1], self.current_state[2][2]]]
        if [i,j] == [[2,0],[1,1],[2,0]]:
            lines+=[[self.current_state[0][2], self.current_state[1][1], self.current_state[2][0]]]

        if flat_node.count('.') == 9:
            if [i,j] == [0,0]:
                return 1
            else:
                return 0
        elif flat_node.count('.') == 8:
            if 'X' in [self.current_state[0][0],self.current_state[0][2],self.current_state[2][0],self.current_state[2][2]]:
                if [i,j] == [1,1]:
                    return 1
                else:
                    return 0
            elif 'X' in [self.current_state[1][1],self.current_state[1][0],self.current_state[1][2],self.current_state[0][1],self.current_state[2][0]]:
                if [i,j] == [0,0]:
                    return 1
                else:
                    return 0
        elif ['O','O','.'] in lines or ['O','.','O'] in lines or ['.','O','O'] in lines:
            return 1000
        elif ['X','X','.'] in lines or ['X','.','X'] in lines or ['.','X','X'] in lines:
            return 100
        return -2

    def a_star(self,h):
        x,y = self.getBestChild(h)
        return (0,x,y)

    def best_move(self):
        self.update_state()
        res=self.algorithm(*self.alg_args)
        return self.matrix[res[1]][res[2]]



app = QApplication(sys.argv)
game = Game()
game.dark_theme()
game.show()
app.exec_()