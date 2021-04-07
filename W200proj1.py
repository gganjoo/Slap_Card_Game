
import random
import time

# I read up on the curses library from two main pages: https://www.devdungeon.com/content/curses-programming-python 
# and https://docs.python.org/3/library/curses.html
import curses

class PlayingCard:
    ''' Takes a rank as a string. 
        Creates a playing card with said rank'''
    
    def __init__(self, rank):
        # Checks that the rank given is a possible card value.
        if rank not in  ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]:
            raise Exception ('Invalid rank!.')
            
        # Assigns the PlayingCard attribute rank.
        self.rank = rank
    
    def __repr__(self):
        # formats the PlayingCard
        return '{self.rank}'.format(self=self)

        
class Deck:
    '''Creates either a deck with 52 cards with four cards of each rank, or a deck with no cards.
        Contains methods for drawing and adding cards, shuffling the deck, finding cards, and adding cards
        during a mistaken 'slap' '''

    def __init__(self, status= 'full'):
        '''Creates a deck of cards. If no argument is entered, the deck will have 52 cards consisting 
            of four cards for each possible rank. If 'empty' is passed through as an argument, then the deck
            will start with no cards, but still be able to have cards added later. '''
        if status=='full':
            deck = []
            for i in range(4):
                for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]:
                    deck.append(PlayingCard(rank))
        elif status== 'empty':
            deck = []
            
        #Saves the deck object and shuffles the deck after it is made.
        self.deck = deck
        self.shuffle_deck()

    def __repr__(self):
        return '{self.deck}'.format(self=self)
    
    def shuffle_deck(self):
        '''Randomly shuffles the cards in a deck.'''
        random.shuffle(self.deck)

    def draw_card(self):
        '''Removes the top card from a deck.'''
        if len(self.deck)>0:
            return self.deck.pop(0)

    def add_card(self,card):
        #Adds a card to the bottom of a deck.
        self.deck.append(card)

    def lose_cards(player, discard):
        '''Removes three cards from one deck(player) and adds them to the top of another deck(discard) '''
        #Check if the deck passed is long enough to have three cards removed.
        if len(player.deck)>=3:
            discard.deck.insert(0,player.deck.pop(0))
            discard.deck.insert(0,player.deck.pop(0))
            discard.deck.insert(0,player.deck.pop(0))


    def find_card(self,index):
        '''Defines indexing for a Deck object'''
        return self.deck[index]

 

class Board:
    '''Creates a string to represent the game's board. The object needs three Deck objects and a 
        string object for  controls'''

    def __init__(self, discard_pile, comp, play, controls):
        '''Creates a string object to represent the game board. The board's layout is the computer's deck and number of cards, 
            then a blank space for the discard pile, then the player's deck and number of cards, then keyboard control instructions.
            The card emoji comes from https://emojipedia.org/joker/ '''

        # Check if the discard pile has any cards in it to display yet. If yes, the board shows it. If not, the spot for 
        # the discard pile is left empty.
        if len(discard_pile.deck)>0:
            board = '🃏 computer ' + str(len(comp.deck)) +'\n' + str(Deck.find_card(discard_pile,-1)) \
            + '\n🃏 you ' + str(len(play.deck)) + '\n\n' +controls
        else:
            board = '🃏 computer ' + str(len(comp.deck)) +'\n\n🃏 you ' + str(len(play.deck)) + '\n\n' +controls

        # Saves the board.
        self.board = board

    def __repr__(self):
        return self.board


class Instructions:
    '''Creates and displays the instructions for the game. Because the window object was having formatting issues displaying one string, 
        I decided to display them line by line through a loop.'''

    def __init__(self, screen):
        '''The Instructions are displayed via the object each time it is called. It takes as an argument the screen the instructions
            will be displayed on.'''
        instructions = ["Instructions:\n","There are two players, you and the computer.\n", 
                                "Each player starts with 26 cards from a randomly shuffled 52 card deck.\n",
                                "You will see two cards representing each player and the number of remaining cards each player has left.\n", 
                                "You will take turns drawing a card, by pressing d, from your decks and adding them to a discard pile,\n which you will see appear on the screen.\n" 
                                "Keep track of the previous cards.\n", 
                                "If two of the same card are placed in a row on the discard pile, a slap event is triggered.\n",
                                "When this happens, press s to 'slap' the discard pile.\n",
                                "If you 'slap' within two seconds, you get to add the discard pile to your deck.\n",
                                "If you 'slap' after two seconds, discard pile is added to the computer's deck.\n",
                                "The loser is whoever runs out of cards first.\n",
                                "Don't press s outside of a slap event, otherwise you will lose three cards from your deck.",
                                "Note: make sure you check the number of cards in each persons deck, because that tells you if another card was added,\n even if the top card does not change.\n",
                                "To quit early press q. To see the instructions again, press i.\n\n"]
        self.instructions = instructions
        self.screen = screen

    def display_instructions(self):
        # Displays the instructions. 
        for item in self.instructions:
            self.screen.addstr(item)


class Slap:
    '''This is the game object. It starts by creating two decks(player and computer) of 26 cards from a 52 card deck, as well as an 
        empty deck(discard pile). The game starts by using the curses library in python and opening a window in the terminal. The player will 
        press d to draw a card from their own deck and add it to the discard pile. The player and the computer will each add cards to the discard
        pile one after another and the board will continually be updated to show the top card on the discard pile as well as the amount of cards 
        the computer and the player each have. Occasionally there will be a slap event where the player will press the s key as fast as they can
        . If they press the s key within two seconds, the discard pile is added into the player's deck and the player's deck is reshuffled.
        If not, then the discard pile is added to the computer's deck. The loser is the first person to run put of cards. A slap event is triggered 
        when the top two cards on the discard pile are the same (ex: 2 2, K K), called a Double event, or when the first and third cards on top of
        the discard pile are the same (ex: 2 5 2, K 7 K ), called a Sandwhich event. After an event occurs, messages will appear on screen to 
        let the player know the result. If the player slaps when it is not a slap event, then the player loses 3 cards to the discard pile.
        If the player presses i, the instructions will be displayed. If the the player presses q, they will quit the game early. If other keys are 
        pressed, messages will appear to help the player. When the game is finished or comleted, the window will close and print out a message
        for the player.'''

    def __init__(self):
        '''Creates the player's deck, the computer's deck, and the discard pile.'''
        #Initializes decks.
        deck = Deck()
        discard_pile = Deck('empty')
        player = Deck('empty')
        computer= Deck('empty')
        
        #Fills the player deck and the computer's deck.
        while len(deck.deck)>0:
            player.add_card(deck.draw_card())
            computer.add_card(deck.draw_card())

        #Saves the decks.
        self.deck = deck
        self.discard_pile = discard_pile
        self.player = player
        self.computer = computer
        self.screen = curses.initscr()
        self.instructions = Instructions(self.screen)

    def game_start(self):
        '''Starts the game and the user interface'''

        #To make the code less wordy, assigning the different deck's names here so I can write 'self' less.
        discard_pile = self.discard_pile
        player = self.player
        computer = self.computer
        screen = self.screen
        instructions = self.instructions

        # Turns off echo so that player's key presses aren't displayed.
        curses.noecho()
        # Turns on cbreak so that the player does not need to hit enter when playing.
        curses.cbreak()

        # Remembers the controls that will be displayed at the bottom of the Window object.
        CONTROLS = "Press d to draw\nPress s to slap\nPress i for instructions\nPress q to quit"

        # Remembers how much time a player has to press 's' in order to win a slap event
        WAIT_TIME = 1

        # Declares the variables for remembering whose turn it is and if the game is ongoing.
        gameon = True
        player_turn = True


        # Asks player to press a key to start. 
        screen.addstr('Ready to start? Press any key to begin\n')
        curses.napms(700)
        c = screen.getch()

        # Shows the instructions.
        screen.clear()
        instructions.display_instructions()
        screen.addstr('Press any key to continue.')
        screen.refresh()
        screen.getch()


        # Displays the initial game board on the screen.
        screen.clear()
        screen.addstr(Board(discard_pile,computer,player, CONTROLS).board)
        screen.refresh()

        # Saves the display message for the player if they exit the game early. If the game is completed, the message will be updated later on.
        event = 'You exited early'

        # Starts a loop that terminates when the game is over. 
        while gameon:

            # This loop runs when it is the player's turn i.e. when player_turn == True
            while player_turn:

                # Checks if the player has any cards left in their deck. If not, then the player lost.
                if len(player.deck)<1:
                    gameon = False # Changes flag to tell that the game is over
                    event = 'Sorry player, you lost' # Changes the final messge to the player
                    break 

                #Asks the player to press any key.
                c = screen.getch()

                #If the the player presses 'i', the window will be cleared and will pull up the instructions
                if c == ord('i'):
                    # Clears the window and displays the instructions
                    screen.clear()
                    instructions.display_instructions()
                    # Instructions(screen)
                    screen.addstr('Press q to quit. Press any other key to continue game')

                    # If the player presses 'q', the game will quit.
                    q = screen.getch()
                    if q == ord('q'):
                        gameon = False
                        break

                    # Clears the window of the instructions and displays the updated board again. 
                    screen.clear()
                    screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                    screen.refresh()

                # If the player presses 'd', a card from the 'player' deck will be added to the discard pile. 
                # The board displayed will be updated to show the newly added card.
                elif c == ord('d'):
                    # Adds a card from the 'player' deck to discard pile.
                    discard_pile.add_card(player.draw_card())

                    # Clears the window and displays the updated board with the newly added card.
                    screen.clear()
                    top_card = Deck.find_card(discard_pile,-1)
                    screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                    screen.refresh()
                    
                    # Checks if a Double event occurs.
                    if len(discard_pile.deck)>1:
                        if top_card.rank == discard_pile.deck[-2].rank:
                            # Times how long it takes for the player to press a key
                            start = time.time() 
                            did_slap = screen.getch()
                            end = time.time()
                            # Checks if the player pressed 's' and if the player was quick enough
                            if (did_slap == ord('s')) and ((end-start)<WAIT_TIME): 
                                # Adds cards to the player's deck and empties the discard pile
                                for item in discard_pile.deck:
                                    player.deck.append(item)
                                    player.shuffle_deck()
                                    discard_pile = Deck('empty')
                                    screen.clear()
                                    screen.addstr(Board(discard_pile,computer,player, CONTROLS).board)
                                    # Displays who won the event and which event it was
                                    screen.addstr("\n\nYou slapped first on the Double.")
                                    screen.refresh()
                            else:
                                # Adds cards to the computer's deck and empties the discard pile
                                for item in discard_pile.deck:
                                    computer.deck.append(item)
                                    computer.shuffle_deck()
                                    discard_pile = Deck('empty')
                                    screen.clear()
                                    screen.addstr(Board(discard_pile,computer,player, CONTROLS).board)
                                    # Displays who won the event and which event it was
                                    screen.addstr("\n\nComputer slapped first on the Double.")
                                    screen.refresh()
                    
                    # Checks if a Sandwhich event occurs.
                    if len(discard_pile.deck)>2:
                        if top_card.rank == Deck.find_card(discard_pile,-3).rank:
                             # Times how long it takes for the player to press a key
                            start = time.time()
                            did_slap = screen.getch()
                            end = time.time()
                            # Checks if the player pressed 's' and if the player was quick enough
                            if (did_slap == ord('s')) and  ((end-start)<WAIT_TIME):
                                # Adds cards to the player's deck and empties the discard pile
                                for item in discard_pile.deck:
                                    player.deck.append(item)
                                    player.shuffle_deck()
                                    discard_pile = Deck('empty')
                                    screen.clear()
                                    screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                                     # Displays who won the event and which event it was
                                    screen.addstr('\n\nYou slapped first on the Sandwhich')
                                    screen.refresh()
                            else:
                                # Adds cards to the computer's deck and empties the discard pile
                                for item in discard_pile.deck:
                                    computer.deck.append(item)
                                    computer.shuffle_deck()
                                    discard_pile = Deck('empty')
                                    screen.clear()
                                    screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                                     # Displays who won the event and which event it was
                                    screen.addstr('\n\nComputer slapped first on the Sandwhich.')
                                    screen.refresh()
                                    curses.napms(100) # Pauses to make sure player sees the message. Not neccesary everywhere.

                    curses.napms(600) # Pauses to make sure player sees the message. Done by trial and error.

                    # Flags that the player's turn is done.
                    player_turn = False

                # If playe presses 'q', the game will quit by changing the flags.
                elif c == ord('q'):
                    player_turn = False
                    gameon = False

                # If the player presses 's' and it is not a slap event, they lose three cards or lose.
                elif c == ord('s'):

                    #Checks if the player has enough cards in their deck to continue.
                    if len(player.deck)>=3:
                        screen.clear()
                        # Removes three cards from the player's deck and adds them to the discard pile.
                        Deck.lose_cards(player,discard_pile)
                        screen.addstr(Board(discard_pile,computer,player, CONTROLS).board)
                        # Adds a game message underneath the board.
                        screen.addstr('\n\nOh no. You slapped at the wrong time. 3 of your cards have been added to the bottom of the discard pile')
                        screen.refresh()
                    else:
                        # If the player has less than three cards left, then they automatically lose the game.
                        screen.clear()
                        # Gives player a game message and waits for them to press any key.
                        screen.addstr("\n\nOh no. You slapped at the wrong time. You don't have enough cards to add to the discard pile.")
                        screen.addstr('\n\nPress any key to continue')
                        screen.refresh()
                        screen.getch()
                        # Empties player's deck so that when control loops to the top, the player will lose.
                        player = Deck('empty')

                # Warning/error messages for player. The messages don't go away until 'd' or 's' is pressed.
                # If player presses capitol 'D', the game tells the player the caps lock is on.         
                elif c == ord('D'):
                    screen.addstr('\n\nCaps lock is on.')

                # If the player presses any key other that 'd','s','q','i', or 'D', the game tells the player that they pressed the worong key.
                else:
                    screen.addstr('\n\nWrong key :)')

            #Checks if game has ended after the player's turn.    
            if gameon==False:
                break

            # This loop runs for computer's turn i.e. if player_turn == False.
            while not player_turn:

                # Checks if the computer has no more cards and therefore the player has won.
                if len(computer.deck)<1:
                    gameon = False # Changes game status flag.
                    event = 'Congrats player, you won' # Changes final messge to user.
                    break

                # Adds a card from the 'computer' deck to the discard pile.
                discard_pile.add_card(computer.draw_card())

                # Clears the window and adds the updated board with newly added card.
                screen.clear()
                top_card = Deck.find_card(discard_pile,-1)
                screen.addstr(Board(discard_pile,computer,player, CONTROLS).board)  
                screen.refresh()

                # Checks for a Double event occurs
                if len(discard_pile.deck)>1:
                    if top_card.rank == discard_pile.deck[-2].rank:
                        # 
                        start = time.time()
                        did_slap = screen.getch()
                        end = time.time()
                        if (did_slap == ord('s')) and ((end-start)<1):
                            for item in discard_pile.deck:
                                player.deck.append(item)
                                player.shuffle_deck()
                                discard_pile = Deck('empty')
                                screen.clear()
                                screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                                screen.addstr('\n\nYou slapped first on the Double')
                                screen.refresh()

                        else:
                            for item in discard_pile.deck:
                                computer.deck.append(item)
                                computer.shuffle_deck()
                                discard_pile = Deck('empty')
                                screen.clear()
                                screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                                screen.addstr('\n\nComputer slapped first on the Double.')
                                screen.refresh()

                if len(discard_pile.deck)>2:
                    if top_card.rank == Deck.find_card(discard_pile,-3).rank:
                        start = time.time()
                        did_slap = screen.getch()
                        end = time.time()
                        if (did_slap == ord('s')) and  ((end-start)<1):
                            for item in discard_pile.deck:
                                player.deck.append(item)
                                player.shuffle_deck()
                                discard_pile = Deck('empty')
                                screen.clear()
                                screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                                screen.addstr('\n\nYou slapped first on the Sandwhich')
                                screen.refresh()
                        else:
                            for item in discard_pile.deck:
                                computer.deck.append(item)
                                computer.shuffle_deck()
                                discard_pile = Deck('empty')
                                screen.clear()
                                screen.addstr(Board(discard_pile,computer,player,CONTROLS).board)
                                screen.addstr('\n\nComputer slapped first on the Sandwhich.')
                                screen.refresh()

                curses.napms(500) 
                
                #Flags that the computer's turn is done.
                player_turn = True

        # Closes the window/game.
        curses.endwin()
        print(event)
       
game = Slap()
game.game_start()