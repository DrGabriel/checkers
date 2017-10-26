import pygame,os
import pygame.gfxdraw
import copy
from roundRect import AAfilledRoundedRect
import gc
# colors for board and pieces
from pygame.constants import RESIZABLE
#global variables
colors = {}
colors['white'] = (255,255,255)
colors['black'] = (0,0,0)
colors['darkOrange'] = (102,51,0)
colors['lightOrange'] = (234,122,0)
colors['darkBrown'] = (51,25,0)
colors['brown'] = (102,51,0)
colors['orange'] = (255,128,0)
colors['red'] = (255,0,0)
colors['green'] = (0,255,0)
colors['grey'] = (64,64,64)
colors['blue'] = (0,0,255)
colors['yellow'] = (255,255,0)
NorthWest = (-1,-1)
NorthEast = (-1,1)
SouthWest = (1,-1)
SouthEast = (1,1)
counter = 0

jumped = False
minAlpha = -10000
maxBeta = 10000
finalScore = 100
drawScore = 0
moveScore = 0
kingPieceWeight = 5
###########
#pygame initialization

pygame.init() # init pygame to use all functions, etc

displaySize = (800,600) # width x heigth

font = pygame.font.Font(os.path.join('fonts','LUNCH___.ttf'), 40)
titleFont = pygame.font.Font(os.path.join('fonts','LUNCH___.ttf'), 60)

ufrrjLogoImg = pygame.image.load(os.path.join('imgs','ufrrjLogo.jpg'))
crownImg = pygame.image.load(os.path.join('imgs','crown.png'))



gameDisplay = pygame.display.set_mode(displaySize,pygame.RESIZABLE) # surface/ background / canvas where you draw your objects
windowWidth,windowHeight = gameDisplay.get_width(), gameDisplay.get_height()#create an array of surface.width and surface.height
pygame.display.set_caption('Checkers') #window title


#########################
#global variables
gameBoard = None
playerTurn = 'white'
boardSize = 0
cellWidth = 0
cellHeight= 0
boardstart = 0,0
boardEnd = 0,0

EASY = 2
MEDIUM = 4
HARD = 6
#game boolean variables
gameExit = False
gamePlayerCpu = False
gamePlayerPlayer = False


cpuIsMoving = False
cpuMoves = None
cpuAttackedPieces = None
cpuMoveIndex = 0
playerpieceMovingId = -1

#menu screen variables
mainMenuScreen = True
configMenuScreen = False
pauseMenuScreen = False
menuPassTurnScreen = False
difficultyScreen = False
gamePlayingScreen = False
gameDrawScreen = False
gameFinalScreen = False


pieceMoving = False
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
counting_time = 0
pieceVelZ = 0
pieceVelX = 0
pieceVelY = 0
pieceRadiusMax = 0
pieceRadiusMin = 0
pieceFalling = False
scoreBar = None
menu = None
scoreBarWidth = displaySize[0]
scoreBarHeight = displaySize[1]//10

fps = 30

pieceID = 1
markedCells = [] # cells that were marked showing possible moves
selectedPieceID = -1
timesPieceClicked = 0

#game imgs
ufrrjLogoImgResized = None
crownImgResized = None

#minmax/game dfficulty
difficulty = 1



movesGenerated = False

#flags for board
blackPieceFlag = 1
whitePieceFlag = -1

#used for multiple jumps of the same piece
pieceMovedID = -1
pieceIsMoving = False

#variables to use in the score for minmax

blackJumped = 0
whiteJumped = 0

#the best moves

atP = None
mv = None
piId = -1

gameTurnsWithoutMoves = 0

##########################


class Button:
    def __init__(self, y,color,text,textColor):
        self.color = color
        self.text = text
        self.textColor = textColor
        self.buttonText = font.render(str(self.text), True, colors[self.textColor])
        self.x = (displaySize[0] - self.buttonText.get_rect().width)//2
        self.y = (displaySize[1] - self.buttonText.get_rect().height)//2 + (y*self.buttonText.get_rect().height)
        self.width = self.buttonText.get_rect().width
        self.height = self.buttonText.get_rect().height

    def draw(self,gameDisplay,mousePos):
        if self.mouseInside(mousePos):
            self.textColor = 'yellow'
        else:
            self.textColor = 'white'
        self.buttonText = font.render(str(self.text), True, colors[self.textColor])
        AAfilledRoundedRect(gameDisplay,[self.x,self.y,self.width,self.height],colors[self.color])
        gameDisplay.blit(self.buttonText, (self.x,self.y))

    def mouseInside(self,mousePos):
        if mousePos[0] >= self.x and mousePos[0]<= (self.x+self.width) and mousePos[1] >= self.y and mousePos[1] <= (self.height + self.y):
            return True
        return False

class Menu:
    def __init__(self):
        self.onePlayerButton = Button(-1,'grey','one player','white')
        self.twoPlayersButton = Button(1,'grey','two players','white')
        self.configurationButton = Button(3,'grey','configurations','white')
        self.boardSize8Button = Button(-1,'grey','8 x 8','white')
        self.boardSize10Button = Button(1,'grey','10 x 10', 'white')
        self.resumePauseButton = Button(-1,'grey','resume','white')
        self.mainMenuButton = Button(1,'grey','main menu','white')
        self.quitButton = Button(5,'grey','quit','white')
        self.easyButton = Button(1,'grey','easy','white')
        self.mediumButton = Button(3,'grey','medium','white')
        self.hardButton = Button(5,'grey','hard','white')
        self.yesPassButton = Button(-1,'grey','yes','white')
        self.noPassButton = Button(1,'grey','no','white')


    def draw(self,gameDisplay,gameBoard,mousePos):
        #draw game title
        titleText = titleFont.render('Checkers', True, colors['lightOrange'])
        gameDisplay.fill(colors['darkBrown'],rect=[0, 0, displaySize[0], displaySize[1]//10])
        gameDisplay.blit(titleText, ((displaySize[0] - titleText.get_rect().width)//2, 0))
        gameBoard.draw(gameDisplay)
        gameDisplay.blit(ufrrjLogoImgResized,(displaySize[0]-ufrrjLogoImgResized.get_rect().width, displaySize[1]-ufrrjLogoImgResized.get_rect().height))

        #player in the menus

        if mainMenuScreen:

            self.quitButton.y = (displaySize[1] - self.quitButton.buttonText.get_rect().height)//2 + (5*self.quitButton.buttonText.get_rect().height)
            self.onePlayerButton.draw(gameDisplay,mousePos)
            self.twoPlayersButton.draw(gameDisplay,mousePos)
            self.configurationButton.draw(gameDisplay,mousePos)
            self.quitButton.draw(gameDisplay,mousePos)


        if configMenuScreen:

            titleText1 = font.render('board size', True, colors['lightOrange'])
            gameDisplay.fill(colors['darkBrown'],rect=[0,titleText.get_rect().height,displaySize[0],displaySize[1]//12])
            gameDisplay.blit(titleText1, ((displaySize[0] - titleText1.get_rect().width)//2,titleText.get_rect().height))
            self.boardSize8Button.draw(gameDisplay,mousePos)
            self.boardSize10Button.draw(gameDisplay,mousePos)

        if pauseMenuScreen:

            self.quitButton.y = (displaySize[1] - self.quitButton.buttonText.get_rect().height)//2 + (3*self.quitButton.buttonText.get_rect().height)
            titleText1 = font.render('pause', True, colors['lightOrange'])
            gameDisplay.fill(colors['darkBrown'],rect=[0,titleText.get_rect().height,displaySize[0],displaySize[1]//12])
            gameDisplay.blit(titleText1, ((displaySize[0] - titleText1.get_rect().width)//2,titleText.get_rect().height))
            self.resumePauseButton.draw(gameDisplay,mousePos)
            self.mainMenuButton.draw(gameDisplay,mousePos)
            self.quitButton.draw(gameDisplay,mousePos)

        if difficultyScreen:

            titleText1 = font.render('select difficulty', True, colors['lightOrange'])
            gameDisplay.fill(colors['darkBrown'],rect=[0,titleText.get_rect().height,displaySize[0],displaySize[1]//12])
            gameDisplay.blit(titleText1, ((displaySize[0] - titleText1.get_rect().width)//2,titleText.get_rect().height))

            self.easyButton.draw(gameDisplay,mousePos)
            self.mediumButton.draw(gameDisplay,mousePos)
            self.hardButton.draw(gameDisplay,mousePos)

        if menuPassTurnScreen:

            titleText1 = font.render('pass turn?', True, colors['lightOrange'])
            gameDisplay.fill(colors['darkBrown'],rect=[0,titleText.get_rect().height,displaySize[0],displaySize[1]//12])
            gameDisplay.blit(titleText1, ((displaySize[0] - titleText1.get_rect().width)//2,titleText.get_rect().height))

            self.yesPassButton.draw(gameDisplay,mousePos)
            self.noPassButton.draw(gameDisplay,mousePos)

        if gameDrawScreen:
            titleText1 = font.render('draw', True, colors['lightOrange'])
            gameDisplay.fill(colors['darkBrown'],rect=[0,titleText.get_rect().height,displaySize[0],displaySize[1]//12])
            gameDisplay.blit(titleText1, ((displaySize[0] - titleText1.get_rect().width)//2,titleText.get_rect().height))

            self.mainMenuButton.draw(gameDisplay,mousePos)
            self.quitButton.draw(gameDisplay,mousePos)

        if gameFinalScreen:
            if gameBoard.whitePiecesTotal + gameBoard.whiteKingsTotal == 0:
                titleText1 = font.render('black pieces won', True, colors['lightOrange'])
                gameDisplay.fill(colors['darkBrown'],rect=[0,titleText.get_rect().height,displaySize[0],displaySize[1]//12])
                gameDisplay.blit(titleText1, ((displaySize[0] - titleText1.get_rect().width)//2,titleText.get_rect().height))

                self.mainMenuButton.draw(gameDisplay,mousePos)
                self.quitButton.draw(gameDisplay,mousePos)

            elif gameBoard.blackPiecesTotal + gameBoard.blackKingsTotal == 0:
                titleText1 = font.render('white piece pieces won', True, colors['lightOrange'])
                gameDisplay.fill(colors['darkBrown'],rect=[0,titleText.get_rect().height,displaySize[0],displaySize[1]//12])
                gameDisplay.blit(titleText1, ((displaySize[0] - titleText1.get_rect().width)//2,titleText.get_rect().height))

                self.mainMenuButton.draw(gameDisplay,mousePos)
                self.quitButton.draw(gameDisplay,mousePos)


class ScoreBar:
    def __init__(self, size):
        self.width = size[0]
        self.height = size[1]

    def draw(self,gameDisplay,gameBoard):
        if(playerTurn == 'white'):
            gameDisplay.fill(colors['red'],rect=[0,0,cellWidth,cellHeight])
        else:
            gameDisplay.fill(colors['red'],rect=[self.width - cellWidth,0,cellWidth,cellHeight])
        #drawing smaller white piece
        centerX = 0*cellWidth + (cellWidth)//2
        centerY = (cellHeight//2)
        pygame.gfxdraw.filled_circle(gameDisplay,centerX,centerY,(cellWidth+cellHeight)//8,colors['white'])
        pygame.gfxdraw.aacircle(gameDisplay,centerX,centerY,(cellWidth+cellHeight)//8,colors['white'])

        #drawing smaller black pice
        centerX = self.width - cellWidth//2
        centerY = ((cellHeight)//2)
        pygame.gfxdraw.filled_circle(gameDisplay,centerX,centerY,(cellWidth+cellHeight)//8,colors['black'])
        pygame.gfxdraw.aacircle(gameDisplay,centerX,centerY,(cellWidth+cellHeight)//8,colors['black'])

        #time elapsed
        counting_minutes = str(counting_time//60000).zfill(2)
        counting_seconds = str( (counting_time%60000)//1000 ).zfill(2)
        counting_string = "Time: %s : %s" % (counting_minutes[:3], counting_seconds[:3])
        counting_text = font.render(str(counting_string), True, colors['black'])
        gameDisplay.blit(counting_text, (((self.width- counting_text.get_rect().width)//2 ),0))

        # drawing total white and black pieces
        whitePieces_text = font.render(str(gameBoard.whitePiecesTotal + gameBoard.whiteKingsTotal),True,colors['black'])
        blackPieces_text = font.render(str(gameBoard.blackPiecesTotal + gameBoard.blackKingsTotal),True,colors['black'])
        gameDisplay.blit(whitePieces_text,((whitePieces_text.get_rect().width+(cellWidth)),(whitePieces_text.get_rect().height//4)))
        gameDisplay.blit(blackPieces_text,(((self.width - 2*whitePieces_text.get_rect().width) - (cellWidth)),(whitePieces_text.get_rect().height//4)))


class Board:

    def __init__(self, size): # size = size x size, 8x8 or 10x10

        global whitePieceFlag,blackPieceFlag

        self.size = size
        self.board =[[(0,0) for i in range(self.size)] for i in range(self.size)] #board is a tuple (numType,id) where num is 1 for black pieces and -1 for white pieces
        self.whitePiecesTotal = 0
        self.whiteKingsTotal = 0
        self.blackPiecesTotal = 0
        self.blackKingsTotal = 0
        self.whitePieces = {}
        self.blackPieces = {}
        self.whitePiecesCopy = {}
        self.blackPiecesCopy = {}

        halfSize = self.size//2

        for x in range(0,self.size):

            for y in range(self.size):

                if(x != halfSize and x != (halfSize -1)):

                  if((x + y)%2 != 0):

                      if(x < halfSize):

                          blackPiece = Piece(x,y,'black')
                          self.blackPieces[blackPiece.id] = blackPiece
                          self.blackPiecesTotal +=1
                          self.board[x][y] = (blackPieceFlag,blackPiece.id)
                      else:

                          whitePiece = Piece(x,y,'white')
                          self.whitePieces[whitePiece.id] = whitePiece
                          self.whitePiecesTotal +=1
                          self.board[x][y] = (whitePieceFlag,whitePiece.id)
        self.whitePiecesCopy = copy.deepcopy(self.whitePieces)
        self.blackPiecesCopy = copy.deepcopy(self.blackPieces)

    def draw(self, gameDisplay):

        global cellHeight,cellWidth

        x,y = 0,scoreBarHeight

        for row in range(0, self.size):

            for column in range(0, self.size):

                if (row + column)%2 == 0:

                   gameDisplay.fill(colors['lightOrange'], rect = [x, y, cellWidth, cellHeight])

                else:

                   gameDisplay.fill(colors['darkOrange'], rect = [x, y, cellWidth, cellHeight])

                x += cellWidth

            x = 0
            y += cellHeight

    def cellIsEmpty(self,row,column):

        if self.board[row][column][0] == 0 and self.board[row][column][1] == 0:
            return  True

        return False

    def getPieceType(self,row,column):

        global whitePieceFlag, blackPieceFlag

        if self.board[row][column][0] == 0:
            return 0
        elif self.board[row][column][0] == whitePieceFlag:
            return whitePieceFlag
        elif self.board[row][column][0] == blackPieceFlag:
            return  blackPieceFlag


    def addPiece(self,piece):

        if piece.type == 'white':

            self.board[piece.row][piece.column] = (whitePieceFlag,piece.id)
            self.whitePieces[piece.id] = piece

            if piece.isKing:
                self.whiteKingsTotal += 1
            else:
                self.whitePiecesTotal += 1

        if piece.type == 'black':

            self.board[piece.row][piece.column] = (blackPieceFlag,piece.id)
            self.blackPieces[piece.id] = piece

            if piece.isKing:
                self.blackKingsTotal += 1
            else:
                self.blackPiecesTotal += 1

    def removePiece(self,row,column):

        type,id = self.board[row][column]
        self.board[row][column] = (0,0)
        piece = None

        #WHITE
        if type == whitePieceFlag:
            piece = self.whitePieces.pop(id)
            if piece.isKing:
                self.whiteKingsTotal -= 1
            else:
                self.whitePiecesTotal -= 1

        #BLACK
        elif type == blackPieceFlag:
            piece = self.blackPieces.pop(id)

            if piece.isKing:
                self.blackKingsTotal -= 1
            else:
                self.blackPiecesTotal -= 1


        return piece

    def movePiece(self,piece, newRow, newColumn,attackedPiecePos):
        attackedP = None
        if moveIsValid(self,newRow,newColumn):

            type,pieceId = self.board[piece.row][piece.column]
            self.board[piece.row][piece.column] = (0,0)
            self.board[newRow][newColumn] = (type,pieceId)

            #WHITE
            if type == whitePieceFlag:
                piece.row = newRow
                piece.column = newColumn
                setKing(piece,self)
                self.whitePieces[pieceId] = piece

            #BLACK
            elif type == blackPieceFlag:
                piece.row = newRow
                piece.column = newColumn
                setKing(piece,self)
                self.blackPieces[pieceId] = piece

            if attackedPiecePos[0] != -1:
                attackedP =  self.removePiece(attackedPiecePos[0],attackedPiecePos[1])

        return attackedP

    def undoMovePiece(self,piece,king, oldRow, oldColumn,attackedPiece):

        self.board[piece.row][piece.column] = (0,0)
        piece.isKing = king

        if piece.type == 'white':

            piece.row = oldRow
            piece.column = oldColumn
            self.board[piece.row][piece.column] = (whitePieceFlag,piece.id)
            self.whitePieces[piece.id] = piece

        if piece.type == 'black':

            piece.row = oldRow
            piece.column = oldColumn
            self.board[piece.row][piece.column] = (blackPieceFlag,piece.id)
            self.blackPieces[piece.id] = piece

        if attackedPiece != None:

            self.addPiece(attackedPiece)


class Piece:

     def __init__(self, row, column, type):

         global pieceID,cellHeight,cellWidth

         self.isKing = False
         self.id = pieceID
         pieceID += 1
         self.type = type #black or white
         self.row = row
         self.column = column
         self.radius = ((cellHeight)//2+cellWidth)//6
         self.velZ = 0

     def drawPiece(self, gameDisplay):

            centerX = self.column*cellWidth + (cellWidth)//2
            centerY = (self.row*cellHeight + (cellHeight)//2) + scoreBarHeight

            if self.isKing: #draw a crown

                centerXCrown = (self.column*cellWidth) + cellWidth//4
                centerYCrown = (self.row*cellHeight - (cellHeight)//4) + scoreBarHeight
                pygame.gfxdraw.filled_circle(gameDisplay, centerX, centerY, self.radius, colors[self.type])
                pygame.gfxdraw.aacircle(gameDisplay, centerX, centerY, self.radius, colors[self.type])
                gameDisplay.blit(crownImgResized, (centerXCrown, centerYCrown))

            else:

                pygame.gfxdraw.filled_circle(gameDisplay, centerX, centerY, self.radius, colors[self.type])
                pygame.gfxdraw.aacircle(gameDisplay, centerX, centerY, self.radius, colors[self.type])



def drawSelectedPiece(piece):

    global selectedPieceID, timesPieceClicked, pieceFalling,movesGenerated,moveDone
    if piece.type == playerTurn:

        centerX = piece.column*cellWidth + (cellWidth)//2
        centerY = (piece.row*cellHeight + (cellHeight)//2) + scoreBarHeight # y starts from 100
        pygame.gfxdraw.filled_circle(gameDisplay, centerX, centerY, piece.radius, colors[piece.type])

        if piece.isKing:

            centerXCrown = piece.column*cellWidth + cellWidth//4
            centerYCrown = (piece.row*cellHeight - (cellHeight)//4) + scoreBarHeight
            gameDisplay.blit(crownImgResized,(centerXCrown, centerYCrown))

        if piece.id == selectedPieceID and timesPieceClicked == 1:

            pygame.gfxdraw.aacircle(gameDisplay, centerX, centerY, piece.radius, colors[piece.type])
            timesPieceClicked = 0
            selectedPieceID = -1
            moveDone = False
            movesGenerated = False

        else:
            pygame.draw.circle(gameDisplay, colors['blue'], (centerX, centerY), piece.radius,4)

    return piece

"""
def drawMovePiece():
    if piece.radius < pieceRadiusMax and not pieceFalling:
        piece.velZ += pieceVelZ
        piece.radius = (cellWidth+cellHeight+piece.velZ)//6
        pygame.gfxdraw.filled_circle(gameDisplay,centerX,centerY,piece.radius,colors[piece.type])
    elif piece.radius > pieceRadiusMin:
        pieceFalling = True
        piece.velZ -= pieceVelZ
        piece.radius = (cellWidth+cellHeight+piece.velZ)//6
        pygame.gfxdraw.filled_circle(gameDisplay,centerX,centerY,piece.radius,colors[piece.type])
    else:
        piece.velZ = 0
        piece.radius = (cellWidth+cellHeight+piece.velZ)//6
        pygame.gfxdraw.filled_circle(gameDisplay,centerX,centerY,piece.radius,colors[piece.type])
"""

#draw all pieces in board, a selected piece is drawn only if its possible to move
def drawAllPieces(gameDisplay,gameBoard):

    for key, piece in gameBoard.whitePieces.items():
        piece.radius = ((cellHeight)//2+cellWidth)//6
        moves,attackedP = generateValidMoves(piece,gameBoard)

        if piece.id == selectedPieceID and len(moves) > 0:

            piece1 = drawSelectedPiece(piece)
            gameBoard.whitePieces.update({piece1.id:piece1})

        else:
            piece.drawPiece(gameDisplay)

    for key, piece in gameBoard.blackPieces.items():
        piece.radius = ((cellHeight)//2+cellWidth)//6
        moves,attackedP = generateValidMoves(piece,gameBoard)

        if piece.id == selectedPieceID and len(moves) > 0:

            piece1 = drawSelectedPiece(piece)
            gameBoard.blackPieces.update({piece1.id:piece1})

        else:

            piece.drawPiece(gameDisplay)

#get board pos where mouse is aming at
def getBoardPos(mouseX, mouseY):

    cellStart = [0, scoreBarHeight]
    cellEnd = [cellWidth, cellHeight + scoreBarHeight]

    for row in range(boardSize):

        for column in range(boardSize):

            if mouseX >= cellStart[0] and mouseX < cellEnd[0] and mouseY >= cellStart[1] and mouseY < cellEnd[1]:

                return(row, column)

            cellStart[0] += cellWidth
            cellEnd[0] += cellWidth

        cellStart[0] = 0
        cellStart[1] +=cellHeight
        cellEnd[0] = cellWidth
        cellEnd[1] +=cellHeight

    return(-1, -1)

#getPiece in the board, maybe it should be insid Board class
def getPiece(row, column, gameBoard):
    pieceType = gameBoard.board[row][column][0]
    pieceID = gameBoard.board[row][column][1]
    if pieceType == blackPieceFlag:
        if pieceID in gameBoard.blackPieces:
            return gameBoard.blackPieces[pieceID]

    elif pieceType == whitePieceFlag:
        if pieceID in gameBoard.whitePieces:
            return gameBoard.whitePieces[pieceID]

    return  None

#check if move is outside game board, therefore invalid, otherwise valid
def moveIsValid(board,newRow,newColumn):
    if newRow >= 0 and newRow <  board.size and newColumn >=0 and newColumn < board.size and ((newRow+newColumn)%2 != 0):
        return  True
    return False


#Check if a given jump is possible
def canJump(gameBoard,row,column):

    if moveIsValid(gameBoard,row,column):
        return gameBoard.cellIsEmpty(row,column)

    return False


#Check if a given move is valid
def getValidMove(gameBoard,row,column):

    if moveIsValid(gameBoard,row,column):
        if gameBoard.cellIsEmpty(row,column):
            return (row,column)
            
    return (-1,-1)

def getJumpMove(piece,gameBoard,row,column,jumpRow,jumpColumn):
    global whitePieceFlag,blackPieceFlag
    
    if moveIsValid(gameBoard,row,column):
        
        if piece.type == 'white':
            
            if gameBoard.getPieceType(row,column) == blackPieceFlag: #jump enemy piece
                if canJump(gameBoard,jumpRow,jumpColumn):
                    return (jumpRow,jumpColumn), (row,column)
                
        elif piece.type == 'black':
            
            if gameBoard.getPieceType(row,column) == whitePieceFlag: #jump enemy piece
                
                if canJump(gameBoard,jumpRow,jumpColumn):
                    return (jumpRow,jumpColumn), (row,column)
            
    return(-1,-1), (-1,-1) #cant jump


def appendMove(move,attackedPiece,movesList,attackedPiecesList):

    if move[0] != -1:
        movesList.append(move)
        attackedPiecesList.append(attackedPiece)


def generateValidMoves(piece,gameBoard):

    global movesGenerated
    #list with all possible moves
    moves = []

    #list with all pieces that were attacked
    attackedPieces = []

    # all possible moves
    rowNW, columnNW = piece.row + NorthWest[0], piece.column + NorthWest[1]
    rowNE, columnNE = piece.row + NorthEast[0], piece.column + NorthEast[1]
    rowSW, columnSW = piece.row + SouthWest[0], piece.column + SouthWest[1]
    rowSE, columnSE = piece.row + SouthEast[0], piece.column + SouthEast[1]
    jumpRowNW,jumpColumnNW = rowNW + NorthWest[0], columnNW + NorthWest[1]
    jumpRowNE,jumpColumnNE = rowNE + NorthEast[0], columnNE + NorthEast[1] 
    jumpRowSW, jumpColumnSW = rowSW + SouthWest[0], columnSW + SouthWest[1]
    jumpRowSE, jumpColumnSE = rowSE + SouthEast[0], columnSE + SouthEast[1]

    if piece.type == 'white' and not piece.isKing:
        #white pieces that are not kings can only move NW and NE, but can attack all sides
        
        moveNW = getValidMove(gameBoard, rowNW, columnNW)
        moveNE = getValidMove(gameBoard, rowNE, columnNE)
        jumpMoveNW,attackedPieceNW = getJumpMove(piece, gameBoard, rowNW, columnNW, jumpRowNW, jumpColumnNW)
        jumpMoveNE,attackedPieceNE = getJumpMove(piece, gameBoard, rowNE, columnNE, jumpRowNE, jumpColumnNE)
        jumpMoveSW,attackedPieceSW = getJumpMove(piece, gameBoard, rowSW, columnSW, jumpRowSW, jumpColumnSW)
        jumpMoveSE,attackedPieceSE = getJumpMove(piece, gameBoard, rowSE, columnSE, jumpRowSE, jumpColumnSE)

        appendMove(moveNW, (-1,-1), moves, attackedPieces)
        appendMove(moveNE, (-1,-1), moves, attackedPieces)
        appendMove(jumpMoveNW, attackedPieceNW, moves, attackedPieces)
        appendMove(jumpMoveNE, attackedPieceNE, moves, attackedPieces)
        appendMove(jumpMoveSW, attackedPieceSW, moves, attackedPieces)
        appendMove(jumpMoveSE, attackedPieceSE, moves, attackedPieces)

    elif piece.type == 'black' and not piece.isKing:

        moveSW = getValidMove(gameBoard, rowSW, columnSW)
        moveSE = getValidMove(gameBoard, rowSE, columnSE)
        jumpMoveNW,attackedPieceNW = getJumpMove(piece, gameBoard, rowNW, columnNW, jumpRowNW, jumpColumnNW)
        jumpMoveNE,attackedPieceNE = getJumpMove(piece, gameBoard, rowNE, columnNE, jumpRowNE, jumpColumnNE)
        jumpMoveSW,attackedPieceSW = getJumpMove(piece, gameBoard, rowSW, columnSW, jumpRowSW, jumpColumnSW)
        jumpMoveSE,attackedPieceSE = getJumpMove(piece, gameBoard, rowSE, columnSE, jumpRowSE, jumpColumnSE)

        appendMove(moveSW, (-1,-1), moves, attackedPieces)
        appendMove(moveSE, (-1,-1), moves, attackedPieces)
        appendMove(jumpMoveNW, attackedPieceNW, moves, attackedPieces)
        appendMove(jumpMoveNE, attackedPieceNE, moves, attackedPieces)
        appendMove(jumpMoveSW, attackedPieceSW, moves, attackedPieces)
        appendMove(jumpMoveSE, attackedPieceSE, moves, attackedPieces)

    elif piece.isKing:

        while(moveIsValid(gameBoard,rowNW,columnNW)):

            moveNW = getValidMove(gameBoard, rowNW, columnNW)
            jumpMoveNW,attackedPieceNW = getJumpMove(piece, gameBoard, rowNW, columnNW, jumpRowNW, jumpColumnNW)

            if jumpMoveNW[0] != -1:
                appendMove(jumpMoveNW,attackedPieceNW,moves,attackedPieces)
                break

            elif moveNW[0] == -1 :#cat jump and cant move
                break
            else:
                appendMove(moveNW,(-1,-1),moves,attackedPieces)

            rowNW, columnNW = rowNW + NorthWest[0], columnNW + NorthWest[1]
            jumpRowNW,jumpColumnNW = rowNW + NorthWest[0], columnNW + NorthWest[1]

        while(moveIsValid(gameBoard,rowNE,columnNE)):
            moveNE = getValidMove(gameBoard, rowNE, columnNE)
            jumpMoveNE,attackedPieceNE = getJumpMove(piece, gameBoard, rowNE, columnNE, jumpRowNE, jumpColumnNE)

            if jumpMoveNE[0] != -1:
                appendMove(jumpMoveNE,attackedPieceNE,moves,attackedPieces)
                break
            elif moveNE[0] == -1 :#cant jump and cant move
                break
            else:
                appendMove(moveNE,(-1,-1),moves,attackedPieces)

            rowNE, columnNE = rowNE + NorthEast[0], columnNE + NorthEast[1]
            jumpRowNE,jumpColumnNE = rowNE + NorthEast[0], columnNE + NorthEast[1]

        while(moveIsValid(gameBoard,rowSW,columnSW)):
            moveSW = getValidMove(gameBoard, rowSW, columnSW)
            jumpMoveSW,attackedPieceSW = getJumpMove(piece, gameBoard, rowSW, columnSW, jumpRowSW, jumpColumnSW)

            if jumpMoveSW[0] != -1:
                appendMove(jumpMoveSW,attackedPieceSW,moves,attackedPieces)
                break
            elif moveSW[0] == -1 :#cat jump and cant move
                break
            else:
                appendMove(moveSW,(-1,-1),moves,attackedPieces)

            rowSW, columnSW = rowSW + SouthWest[0], columnSW + SouthWest[1]
            jumpRowSW,jumpColumnSW = rowSW + SouthWest[0], columnSW + SouthWest[1]

        while(moveIsValid(gameBoard,rowSE,columnSE)):
            moveSE = getValidMove(gameBoard, rowSE, columnSE)
            jumpMoveSE,attackedPieceSE = getJumpMove(piece, gameBoard, rowSE, columnSE, jumpRowSE, jumpColumnSE)

            if jumpMoveSE[0] != -1:
                appendMove(jumpMoveSE,attackedPieceSE,moves,attackedPieces)
                break
            elif moveSE[0] == -1 :#cat jump and cant move
                break
            else:
                appendMove(moveSE,(-1,-1),moves,attackedPieces)

            rowSE, columnSE = rowSE + SouthEast[0], columnSE + SouthEast[1]
            jumpRowSE,jumpColumnSE = rowSE + SouthEast[0], columnSE + SouthEast[1]

    movesGenerated = True
    return moves,attackedPieces

def getJumps(piece,gameboard):
    moves,attackedpieces = generateValidMoves(piece,gameboard)
    jumps = []
    jumpedPieces = []

    for index in range(0,len(moves)):

        if attackedpieces[index][0] != -1:#attacked piece
            jumps.append(moves[index])
            jumpedPieces.append(attackedpieces[index])

    return jumps, jumpedPieces

def drawPossibleMoves(movesList,attackedPiecesList,gameDisplay):
    global cellWidth,cellHeight,scoreBarHeight

    attackMove = False
    for pieceAttacked in attackedPiecesList:
        if pieceAttacked[0] != -1:
            attackMove = True

    if attackMove: #draw only attack moves

        for index in range(0,len(movesList)):
            if attackedPiecesList[index][0] != -1:
                centerX = movesList[index][1]*cellWidth + (cellWidth)//2
                centerY = (movesList[index][0]*cellHeight + (cellHeight)//2) + scoreBarHeight # y starts from 100
                pygame.draw.circle(gameDisplay, colors['green'], (centerX, centerY), pieceRadiusMin,4)
                centerX = attackedPiecesList[index][1]*cellWidth + (cellWidth)//2
                centerY = (attackedPiecesList[index][0]*cellHeight + (cellHeight)//2) + scoreBarHeight # y starts from 100
                pygame.draw.circle(gameDisplay, colors['red'], (centerX, centerY), pieceRadiusMin,4)
    else:

        for move in movesList:
            centerX = move[1]*cellWidth + (cellWidth)//2
            centerY = (move[0]*cellHeight + (cellHeight)//2) + scoreBarHeight # y starts from 100
            pygame.draw.circle(gameDisplay, colors['green'], (centerX, centerY), pieceRadiusMin,4)

        for piece in attackedPiecesList:
            if piece[0] != -1:
                centerX = piece[1]*cellWidth + (cellWidth)//2
                centerY = (piece[0]*cellHeight + (cellHeight)//2) + scoreBarHeight # y starts from 100
                pygame.draw.circle(gameDisplay, colors['red'], (centerX, centerY), pieceRadiusMin,4)


def setKing(piece,gameBoard):


    if piece.type == 'black' and piece.row == boardSize-1:
        gameBoard.blackPiecesTotal -= 1
        gameBoard.blackKingsTotal += 1
        piece.isKing = True
        gameBoard.blackPieces[piece.id] = piece

    elif piece.type == 'white' and piece.row == 0:
        gameBoard.whitePiecesTotal -= 1
        gameBoard.whiteKingsTotal +=1
        piece.isKing = True
        gameBoard.whitePieces[piece.id] = piece


#heuristic for minmax
def getScore(board,playerType):

    global finalScore,drawScore,kingPieceWeight,whiteJumped,blackJumped
    #this code part is from: https://github.com/radekstepan/pyCheckers/blob/master/checkers-1.1.2.3%20final.py

    black, white = 0, 0 # keep track of score
    for key,piece in board.blackPieces.items():
        if piece.isKing:
            black += 175
        else:
            black += 100

    for key,piece in board.whitePieces.items():
        if piece.isKing:
            white += 175
        else:
            white += 100

    if playerType == 'white':

        return (white-black) + whiteJumped*10
    else:
        return (black-white) + blackJumped*10


def flipType(pieceType):

    if pieceType == 'white':
        return 'black'
    return 'white'


def minMax(playerType,board,maximizingPlayer,alpha,beta,depth = 0):

    global drawScore,finalScore,difficulty,atP,mv,piId,playerTurn,whiteJumped,blackJumped,jumped

    if depth >= difficulty:
        score = getScore(board,playerType)
        return score

    if difficulty > depth:

        if playerType == playerTurn:

            if playerType == 'white':

                for key, piece1 in board.whitePieces.items():#generete moves for all pieces

                    moves,attackedPieces = generateValidMoves(piece1,board)

                    for index in range(0, len(moves)):

                        if attackedPieces[index][0] != -1:
                            whiteJumped +=100

                        king,oldRow,oldColumn = piece1.isKing,piece1.row,piece1.column
                        attackedP = board.movePiece(piece1,moves[index][0],moves[index][1],attackedPieces[index])



                        score = minMax(flipType(playerType),board,not maximizingPlayer,alpha,beta,depth+1)

                        if score > alpha:
                            alpha = score

                            if depth == 0:

                                piId = key
                                mv = moves[index]
                                atP = attackedPieces[index]
                        #alpha = max(alpha,score)

                        if attackedPieces[index][0] != -1:
                            whiteJumped -= 100

                        board.undoMovePiece(piece1,king,oldRow,oldColumn,attackedP)

                        if alpha >= beta:

                            return alpha

                return alpha


            if playerType == 'black':

                for key, piece1 in board.blackPieces.items():#generete moves for all BLACK pieces

                    moves,attackedPieces = generateValidMoves(piece1,board)

                    for index in range(0, len(moves)):

                        if attackedPieces[index][0] != -1:
                            blackJumped +=100

                        king,oldRow,oldColumn = piece1.isKing,piece1.row,piece1.column
                        attackedP = board.movePiece(piece1,moves[index][0],moves[index][1],attackedPieces[index])

                        score = minMax(flipType(playerType),board,not maximizingPlayer,alpha,beta,depth+1)
                        if score > alpha:
                            alpha = score
                            if depth == 0:
                                piId = key
                                mv = moves[index]
                                atP = attackedPieces[index]


                        board.undoMovePiece(piece1,king,oldRow,oldColumn,attackedP)

                        if attackedPieces[index][0] != -1:
                            blackJumped -= 100

                        if alpha >= beta:
                            return alpha

                return alpha

        else:#min

            if playerType == 'white':

                for key, piece1 in board.whitePieces.items():#generete moves for all pieces

                    moves,attackedPieces = generateValidMoves(piece1,board)
                    for index in range(0, len(moves)):

                        king,oldRow,oldColumn = piece1.isKing,piece1.row,piece1.column
                        attackedP = board.movePiece(piece1,moves[index][0],moves[index][1],attackedPieces[index])

                        score = minMax(flipType(playerType),board,not maximizingPlayer,alpha,beta,depth+1)
                        beta = min(beta,score)

                        board.undoMovePiece(piece1,king,oldRow,oldColumn,attackedP)

                        if beta <= alpha:
                            return beta


                return beta


            if playerType == 'black':

                for key, piece1 in board.blackPieces.items():#generete moves for all BLACK pieces

                    moves,attackedPieces = generateValidMoves(piece1,board)

                    for index in range(0, len(moves)):

                        king,oldRow,oldColumn = piece1.isKing,piece1.row,piece1.column
                        attackedP = board.movePiece(piece1,moves[index][0],moves[index][1],attackedPieces[index])

                        score = minMax(flipType(playerType),board,not maximizingPlayer,alpha,beta,depth+1)
                        beta = min(beta,score)

                        board.undoMovePiece(piece1,king,oldRow,oldColumn,attackedP)


                        if beta <= alpha:
                            return beta

                return beta
    else:

        if maximizingPlayer:
            return minAlpha
        else:
            return maxBeta


# based on minmax give the best move
def findBestMove(board,playerType):

    global piId,mv,atP,whiteJumped,blackJumped
    piId = -1
    mv = None
    atp = None
    whiteJumped = 0
    blackJumped = 0
    score = minMax(playerType,board,True,minAlpha,maxBeta)

    return piId,mv, atP


def checkDraw(board):

    global gameTurnsWithoutMoves,gameDrawScreen,gamePlayingScreen

    if gameTurnsWithoutMoves == 40: #both white and black pieces did not moved or attacked
        gameTurnsWithoutMoves = 0
        gameDrawScreen = True
        gamePlayingScreen = False


def checkGameFinal(board):
    global gamePlayingScreen,gameFinalScreen
    if board.whitePiecesTotal + board.whiteKingsTotal == 0:
        gameFinalScreen = True
        gamePlayingScreen = False

    elif board.blackPiecesTotal + board.blackKingsTotal == 0:
        gameFinalScreen = True
        gamePlayingScreen = False


def moveAux(pieceMoved,pieceType,board,moves,attackedPieces):
    jumps,jumpedPieces = getJumps(pieceMoved,board)

    if len(jumps) != 0: #move again, because piece can jump!
        pId,move,attackedPiece = findBestMove(board,pieceType)

        if pieceMoved.id == pId and attackedPiece[0] != -1:

            oldRow,oldColumn,king = pieceMoved.row,pieceMoved.column,pieceMoved.isKing
            attackedPieceObj = board.movePiece(pieceMoved,move[0],move[1],attackedPiece)

            moveAux(pieceMoved,pieceType,board,moves,attackedPieces)#recursion

            board.undoMovePiece(pieceMoved,king,oldRow,oldColumn,attackedPieceObj)
            moves.append(move)
            attackedPieces.append(attackedPiece)



def cpuMove(board,cpuPieceType):
    global piId,mv,atP,gameTurnsWithoutMoves
    moves = []
    attackedPieces = []
    pId,move,attackedPiece = findBestMove(board,cpuPieceType)

    if pId == -1 or attackedPiece[0] == -1: #no movement or no jump for 20 turns

        gameTurnsWithoutMoves += 1
    else:
        gameTurnsWithoutMoves = 0

    if pId != -1:

        if cpuPieceType == 'black':
             pieceMoved = board.blackPieces[pId]
             board.movePiece(pieceMoved,move[0],move[1],attackedPiece)

             if attackedPiece[0] != -1:#jumped a piece, check if can jump another one
                 moveAux(pieceMoved,cpuPieceType,board,moves,attackedPieces)

                 moves = list(reversed(moves))
                 attackedPieces = list(reversed(attackedPieces))

        else:
            pieceMoved = board.whitePieces[pId]
            board.movePiece(pieceMoved,move[0],move[1],attackedPiece)

            if attackedPiece[0] != -1:#jumped a piece, check if can jump another one
                moveAux(pieceMoved,cpuPieceType,board,moves,attackedPieces)
                moves = list(reversed(moves))
                attackedPieces = list(reversed(attackedPieces))


    return moves, attackedPieces



def possiblePlayerMoves(board,playerType):
    allowedPiecesIds = []
    longestSequence = 0
    jumpIsPossible = False
    moves = []
    attackedPieces = []

    if playerType == 'white':

        for key,playerPiece in board.whitePieces.items():

            jump,jumpedPieces = getJumps(playerPiece,board)

            if len(jump) > 0: #player must do a jump move, check with minmax the best jump move
                moveAux(playerPiece,playerPiece.type,board,moves,attackedPieces)
                sequenceSize = len(moves)

                if sequenceSize > longestSequence:
                    allowedPiecesIds.clear()
                    allowedPiecesIds.append(key)
                    longestSequence = sequenceSize
                elif sequenceSize == longestSequence:
                    allowedPiecesIds.append(key)

                moves.clear()
                attackedPieces.clear()


    if playerType == 'black':
        for key,playerPiece in board.blackPieces.items():

            jump,jumpedPieces = getJumps(playerPiece,board)

            if len(jump) > 0: #player must do a jump move, check with minmax the best jump move
                moveAux(playerPiece,playerPiece.type,board,moves,attackedPieces)
                sequenceSize = len(moves)

                if sequenceSize > longestSequence:
                    allowedPiecesIds.clear()
                    allowedPiecesIds.append(key)
                    longestSequence = sequenceSize
                elif sequenceSize == longestSequence:
                    allowedPiecesIds.append(key)

                moves.clear()
                attackedPieces.clear()

    return allowedPiecesIds



def playerMove(pieceid,move,board):

    if pieceid in board.blackPieces:
        piece = board.blackPieces[pieceid]

        allowedPiecesIds = possiblePlayerMoves(board,piece.type)
        if len(allowedPiecesIds) > 0:
            if piece.id in allowedPiecesIds:
                moves,attacks = generateValidMoves(piece,board)

                for index in range(0,len(moves)):
                    if moves[index][0] == move[0] and moves[index][1] == move[1] and attacks[index][0]!= -1:

                        return  True , board.movePiece(piece,move[0],move[1],attacks[index])

        else:
            moves,attacks = generateValidMoves(piece,board)

            for index in range(0,len(moves)):
                if moves[index][0] == move[0] and moves[index][1] == move[1]:


                     return True, board.movePiece(piece,move[0],move[1],attacks[index])


    elif pieceid in board.whitePieces:

        piece = board.whitePieces[pieceid]
        allowedPiecesIds = possiblePlayerMoves(board,piece.type)
        if len(allowedPiecesIds) > 0:

            if piece.id in allowedPiecesIds:
                moves,attacks = generateValidMoves(piece,board)

                for index in range(0,len(moves)):
                    if moves[index][0] == move[0] and moves[index][1] == move[1] and attacks[index][0]!= -1:


                        return  True, board.movePiece(piece,move[0],move[1],attacks[index])

        else:
            moves,attacks = generateValidMoves(piece,board)

            for index in range(0,len(moves)):
                if moves[index][0] == move[0] and moves[index][1] == move[1]:


                     return True, board.movePiece(piece,move[0],move[1],attacks[index])




    return False, None

def resizeGame(screenSize):

        global boardSize, cellHeight, cellWidth, gameBoard, boardstart, boardEnd, pieceRadiusMin, pieceRadiusMax, pieceVelZ, pieceVelX, pieceVelY, moveDone,\
        displaySize, menu, scoreBar, scoreBarHeight, scoreBarWidth, playerTurn, start_time, ufrrjLogoImg, crownImg, ufrrjLogoImgResized, crownImgResized,\
        selectedPieceID, pieceID, gamePlayerCpu, gamePlayerPlayer, cpuMoveIndex, cpuMoves,cpuAttackedPieces,gameTurnsWithoutMoves

        displaySize = screenSize

        scoreBarWidth = screenSize[0]
        scoreBarHeight = screenSize[1]//10
        scoreBar = ScoreBar((scoreBarWidth, scoreBarHeight))
        cellWidth = (screenSize[0])//boardSize
        cellHeight = (screenSize[1] - scoreBarHeight)//boardSize
        boardstart = (0, scoreBarHeight)
        boardEnd = (cellWidth*boardSize, (boardSize*cellHeight + scoreBarHeight))

        menu = Menu()
        pieceVelZ = 2
        pieceVelX = 1
        pieceVelY = 2
        pieceRadiusMin = ((cellHeight)//2 + cellWidth)//6
        pieceRadiusMax = ((cellHeight)//2 + cellWidth)//4
        ufrrjLogoImgResized = pygame.transform.scale(ufrrjLogoImg, (displaySize[0]//4, displaySize[1]//10))
        crownImgResized = pygame.transform.scale(crownImg, (cellWidth//2, cellHeight//2))

def resetGame(size, screenSize):

    global boardSize, cellHeight, cellWidth, gameBoard, boardstart, boardEnd, pieceRadiusMin, pieceRadiusMax, pieceVelZ, pieceVelX, pieceVelY, moveDone,\
        displaySize, menu, scoreBar, scoreBarHeight, scoreBarWidth, playerTurn, start_time, ufrrjLogoImg, crownImg, ufrrjLogoImgResized, crownImgResized,\
        selectedPieceID, pieceID, gamePlayerCpu, gamePlayerPlayer, cpuMoveIndex, cpuMoves,cpuAttackedPieces,gameTurnsWithoutMoves

    playerTurn = 'white'
    start_time = pygame.time.get_ticks()
    boardSize = size
    displaySize = screenSize
    cpuMoveIndex = 0

    cpuMoves = None
    cpuAttackedPieces = None
    gameTurnsWithoutMoves = 0

    scoreBarWidth = screenSize[0]
    scoreBarHeight = screenSize[1]//10
    scoreBar = ScoreBar((scoreBarWidth, scoreBarHeight))

    cellWidth = (screenSize[0])//boardSize
    cellHeight = (screenSize[1] - scoreBarHeight)//boardSize
    gameBoard = Board(boardSize)


    menu = Menu()
    boardstart = (0, scoreBarHeight)
    boardEnd = (cellWidth*boardSize, (boardSize*cellHeight + scoreBarHeight))
    pieceVelZ = 2
    pieceVelX = 1
    pieceVelY = 2
    pieceRadiusMin = ((cellHeight)//2 + cellWidth)//6
    pieceRadiusMax = ((cellHeight)//2 + cellWidth)//4
    ufrrjLogoImgResized = pygame.transform.scale(ufrrjLogoImg, (displaySize[0]//4, displaySize[1]//10))
    crownImgResized = pygame.transform.scale(crownImg, (cellWidth//2, cellHeight//2))
    moveDone = False
    gamePlayerCpu = False
    gamePlayerPlayer = False
    selectedPieceID = -1
    pieceID = 0


resetGame(8, displaySize)

movesList,attackedPiecesList = None,None
gameDisplay.fill(colors['orange'])
pause_time = 0
while not gameExit:

    if gamePlayingScreen:
        counting_time = pygame.time.get_ticks() - start_time - pause_time
    elif pauseMenuScreen:
        pause_time = pygame.time.get_ticks() - counting_time - start_time
    elif mainMenuScreen:
        pause_time = 0

    mouseX,mouseY = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.VIDEORESIZE:

            gameDisplay = pygame.display.set_mode(event.size,pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
            resizeGame(event.size)

        if event.type == pygame.QUIT:
            gameExit = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and configMenuScreen :
            configMenuScreen = False
            mainMenuScreen = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and difficultyScreen :
            difficultyScreen = False
            mainMenuScreen = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and gamePlayingScreen:
            gamePlayingScreen = False
            menuPassTurnScreen = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and gamePlayingScreen :
            gamePlayingScreen = False
            pauseMenuScreen = True


        if event.type == pygame.MOUSEBUTTONUP and menuPassTurnScreen:

            if menu.yesPassButton.mouseInside((mouseX,mouseY)):
                gameTurnsWithoutMoves +=1
                moveDone = True
                gamePlayingScreen = True
                menuPassTurnScreen = False


            elif menu.noPassButton.mouseInside((mouseX,mouseY)):
                gamePlayingScreen = True
                menuPassTurnScreen = False


        if event.type == pygame.MOUSEBUTTONUP and mainMenuScreen:
            if menu.onePlayerButton.mouseInside((mouseX,mouseY)):
                resetGame(boardSize,displaySize)
                mainMenuScreen = False
                difficultyScreen = True

            elif menu.twoPlayersButton.mouseInside((mouseX,mouseY)):
                resetGame(boardSize,displaySize)
                mainMenuScreen = False
                gamePlayerPlayer = True
                gamePlayingScreen = True

            elif menu.configurationButton.mouseInside((mouseX,mouseY)):
                configMenuScreen = True
                mainMenuScreen = False

            elif menu.quitButton.mouseInside((mouseX,mouseY)):
                gameExit = True

        if event.type == pygame.MOUSEBUTTONUP and pauseMenuScreen:
            if menu.mainMenuButton.mouseInside((mouseX,mouseY)):
                gameDisplay = pygame.display.set_mode(displaySize,pygame.RESIZABLE)
                pauseMenuScreen = False
                mainMenuScreen = True

            elif menu.resumePauseButton.mouseInside((mouseX,mouseY)):
                pauseMenuScreen = False
                gamePlayingScreen = True

            elif menu.quitButton.mouseInside((mouseX,mouseY)):
                gameExit = True

        if event.type == pygame.MOUSEBUTTONDOWN and gameFinalScreen:

            if menu.mainMenuButton.mouseInside((mouseX,mouseY)):

                gameFinalScreen = False
                mainMenuScreen = True

            elif menu.quitButton.mouseInside((mouseX,mouseY)):
                gameExit = True

        if event.type == pygame.MOUSEBUTTONDOWN and gameDrawScreen:

            if menu.mainMenuButton.mouseInside((mouseX,mouseY)):

                gameDrawScreen = False
                mainMenuScreen = True

            elif menu.quitButton.mouseInside((mouseX,mouseY)):
                gameExit = True

        if event.type == pygame.MOUSEBUTTONUP and difficultyScreen:
            if menu.easyButton.mouseInside((mouseX,mouseY)):
                difficulty = EASY
                difficultyScreen = False
                gamePlayerCpu = True
                gamePlayingScreen = True
            elif menu.mediumButton.mouseInside((mouseX,mouseY)):
                difficulty = MEDIUM
                difficultyScreen = False
                gamePlayerCpu = True
                gamePlayingScreen = True
            elif menu.hardButton.mouseInside((mouseX,mouseY)):
                difficulty = HARD
                difficultyScreen = False
                gamePlayerCpu = True
                gamePlayingScreen = True

        if event.type == pygame.MOUSEBUTTONUP and configMenuScreen:

            if menu.boardSize8Button.mouseInside((mouseX,mouseY)):
                resetGame(8,displaySize)

            elif menu.boardSize10Button.mouseInside((mouseX,mouseY)):
                resetGame(10,displaySize)

        #PLAYER VS CPU: MOVES, SELECTIONS, YADA YADA YADA

        if event.type == pygame.MOUSEBUTTONUP and gamePlayingScreen:

            if mouseX > boardstart[0] and mouseX < boardEnd[0] and mouseY > boardstart[1] and mouseY <boardEnd[1]: #if mouse is inside the board

                row,column = getBoardPos(mouseX, mouseY)
                pieceSelected = getPiece(row, column, gameBoard)

                if pieceSelected != None:
                    if(selectedPieceID == pieceSelected.id and pieceSelected.type == playerTurn):
                        timesPieceClicked += 1

                    elif(pieceSelected.type == playerTurn):

                        if selectedPieceID != -1:
                            if selectedPieceID in gameBoard.blackPieces:
                                otherPiece = gameBoard.blackPieces[selectedPieceID]
                                movesGenerated = False
                                otherPiece.velZ = 0
                                pieceFalling = False
                                otherPiece.radius = pieceRadiusMin
                                gameBoard.blackPieces[selectedPieceID] = otherPiece
                            elif selectedPieceID in gameBoard.whitePieces:
                                otherPiece = gameBoard.whitePieces[selectedPieceID]
                                movesGenerated = False
                                otherPiece.velZ = 0
                                pieceFalling = False
                                otherPiece.radius = pieceRadiusMin
                                gameBoard.whitePieces[selectedPieceID] = otherPiece

                        selectedPieceID = pieceSelected.id

                else:#player is clicking randomly or wants to make a move
                    if selectedPieceID != -1:
                        moved,attackedP = playerMove(selectedPieceID,(row,column),gameBoard)
                        if moved:
                            if attackedP == None:

                                gameTurnsWithoutMoves += 1 #turn whit just move, but no piece attacked
                                moveDone = True

                            else:

                                gameTurnsWithoutMoves = 0 #attacked and moved

                                if selectedPieceID in gameBoard.whitePieces:
                                    movedP = gameBoard.whitePieces[selectedPieceID]
                                    jump,attacks = getJumps(movedP,gameBoard)
                                    if len(jump) == 0:
                                        moveDone = True

                                if selectedPieceID in gameBoard.blackPieces:
                                    movedP = gameBoard.blackPieces[selectedPieceID]
                                    jump,attacks = getJumps(movedP,gameBoard)
                                    if len(jump) == 0:
                                        moveDone = True



    if(moveDone):

        moveDone = False
        movesGenerated = False
        selectedPieceID  = -1
        playerTurn = flipType(playerTurn)


    if gamePlayerCpu and playerTurn == 'black' and gamePlayingScreen: #cpu turn

        if not cpuIsMoving:
            cpuMoves,cpuAttackedPieces = cpuMove(gameBoard,playerTurn)

            if len(cpuMoves) > 0:
                cpuIsMoving = True
            else:
                moveDone = True

        if cpuIsMoving: #handles multiple jumps

            if cpuMoveIndex >= len(cpuMoves):
                cpuMoveIndex = 0
                cpuIsMoving = False
                moveDone = True

            else:
                pieceMoved = gameBoard.blackPieces[piId]
                gameBoard.movePiece(pieceMoved,cpuMoves[cpuMoveIndex][0],cpuMoves[cpuMoveIndex][1],cpuAttackedPieces[cpuMoveIndex])
                cpuMoveIndex += 1

    if gamePlayingScreen:
        checkDraw(gameBoard)
        checkGameFinal(gameBoard)

    gameDisplay.fill(colors['orange'])
    if mainMenuScreen or configMenuScreen or pauseMenuScreen or difficultyScreen or menuPassTurnScreen or gameDrawScreen or gameFinalScreen:
        menu.draw(gameDisplay,gameBoard,(mouseX,mouseY))

    if gamePlayingScreen :
        scoreBar.draw(gameDisplay,gameBoard)
        gameBoard.draw(gameDisplay)
        drawAllPieces(gameDisplay,gameBoard)


    if(selectedPieceID != -1):

        if selectedPieceID in gameBoard.whitePieces:
            pieceSel = gameBoard.whitePieces[selectedPieceID]
            moves,attacks = generateValidMoves(pieceSel,gameBoard)
            drawPossibleMoves(moves,attacks,gameDisplay)

        if selectedPieceID in gameBoard.blackPieces:
            pieceSel = gameBoard.blackPieces[selectedPieceID]
            moves,attacks = generateValidMoves(pieceSel,gameBoard)
            drawPossibleMoves(moves,attacks,gameDisplay)


    pygame.display.update()#update the frame
    clock.tick(fps)#set fps to 30


pygame.quit() #uninitializing pygame
quit() #exit python



