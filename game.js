/*
tic-tac-toe
3x3 board
one player places X, other player places circle
first to get a 3 in a row in direction wins

ex.

XXX
(left, middle, right)

X
X
X
(left, middle, right)

X
 X
  X

  X
 X
X 
*/

const prompt = require("prompt-sync")();

let board = [
    ['.', '.', '.'], 
    ['.', '.', '.'], 
    ['.', '.', '.']
]

// Giving random values to dictate who goes first
let playerA = Math.floor(Math.random() * 10);
let playerB = Math.floor(Math.random() * 10);

let turn = playerA > playerB ? 'A' : 'B'

if(turn === 'A') {
    console.log('PlayerA goes first')
} else {
    console.log('PlayerB goes first')
}

// Making user select proper values
let choice = prompt("Choose O or X: ");
while(!choice.includes('O') && !choice.includes('X')) {
    choice = prompt("Choose O or X: ");
}

let player = {}

if(turn === 'A') {
    player['A'] = [choice, 0]
    player['B'] = [player['A'][0] === 'X' ? 'O' : 'X', 0]
} else {
    player['B'] = [choice, 0]
    player['A'] = [player['B'][0] === 'X' ? 'O' : 'X', 0]
}

// Simulate game and print the board each time

function displayBoard(board) {
    for(let i = 0; i < board.length; i++) {
        for(let j = 0; j < board.length; j++) {
            process.stdout.write(board[i][j] + " ");
        }
        console.log()
    }
}

function win(board) {
    let threeDiagonalTopToBottom = new Set()
    let threeDiagonalBottomToTop = new Set()

    // Check rows and cols
    for(let i = 0; i < board.length; i++) {
        let threeInRow = new Set()
        let threeInCol = new Set()
        threeDiagonalTopToBottom.add(board[i][i])
        threeDiagonalBottomToTop.add(board[board.length - i - 1][board.length - i - 1])
        for(let j = 0; j < board.length; j++) {
            threeInRow.add(board[i][j])
            threeInCol.add(board[j][i])
        }
        if(threeInRow.size === 1 && !threeInRow.has('.'))return true
        if(threeInCol.size === 1 && !threeInCol.has('.'))return true
    }

    if(threeDiagonalBottomToTop.size === 1 && !threeDiagonalBottomToTop.has('.'))return true
    if(threeDiagonalTopToBottom.size === 1 && !threeDiagonalTopToBottom.has('.'))return true

    return false
}

while(!win(board)) {
    displayBoard(board)
    console.log(turn === 'A' ? 'Player A turn' : 'Player B turn')

    let coordinate = prompt('Choose a open spot and output in the format (1-indexed){row},{column}, ex. 2,2: ')
    let [row, column] = [Number(coordinate[0]), Number(coordinate[2])]
    console.log(row, column, '\n')
    board[row - 1][column - 1] = player[turn][0]

    turn = turn === 'A' ? 'B' : 'A'
}





