import random

# constants
colors = 5
numbers = 11
hand_size = 8
bridge_location = 7
passed_bridge_max = 5
last_space = 9
player_start_turn = 0
big_guys = 1
little_guys = 4

# players and strategies
playerTest = {
    "start_cutoff":2,
    "pile_max":4,
    "max_dif":2,
    "max_discard":2
}

specials = [
    {"type":"skip"},
    {"type":"skip"},
    {"type":"skip"},
    {"type":"token"},
    {"type":"token"},
    {"type":"token"},
    {"type":"coin","value":5},
    {"type":"coin","value":10},
    {"type":"coin","value":15},
]

path_options = [
    [3,5,6,7,9],
    [2,4,5,7,9],
    [2,3,5,7,9],
    [3,4,6,7,9],
    [2,4,5,7,9] # this is used twice
]

points_map = [-20,-15,-10,5,10,15,30,35,50]
tokens_map = [-20,-15,10,15,30,50]

players = []
for i in range(4):
    players.append(playerTest.copy())

## --- DON'T CHANGE BELOW HERE ---

def check_special(piece,last_space, player, board):
    if piece["position"] in board[piece["color"]]:
        new_special = board[piece["color"]][piece["position"]]
        if new_special["type"] == "skip":
            move_other(last_space, player, board)
        elif new_special["type"] == "token":
            player["tokens"] += 1
            new_special = board[piece["color"]].pop(piece["position"])
        elif new_special["type"] == "coin":
            player["coins"] += new_special["value"]

def move_piece(piece,last_space, player, board):
    piece["position"] += 1
    check_special(piece,last_space, player, board)

def move_other(last_space, player, board):
    for piece in sorted(player["pieces"], key = lambda i: i['position'], reverse = True):
        if piece["position"] != last_space and piece["position"] != None:
            move_piece(piece,last_space, player, board)

def move_self(card, last_space, player, board):
    found_used_color = False
    for piece in player["pieces"]:
        if piece["color"] == card["color"]:
            found_used_color = True
            if piece["position"] == last_space:
                move_other(last_space, player, board)
            else:
                move_piece(piece,last_space, player, board)
    
    if not found_used_color:
        for piece in player["pieces"]:
            if piece["position"] == None:
                piece["position"] = 1
                piece["color"] = card["color"]
                break

    if "dif" in card:
        del card["dif"]
    player["cards"].remove(card)
    player["piles"][card["color"]].append(card)

avg_points = []
for i in range (300):

    # make board
    board = {}
    for color in range(colors):
        board[color] = {}
        for space in path_options[color]:
            board[color][space] = random.choice(specials)

    # make discard piles
    discard_piles = {}
    for color in range(colors):
        discard_piles[color] = []

    # make cards
    cards = []
    for i in range(2):
        for color in range(colors):
            for number in range(numbers):
                cards.append({"color":color, "number":number})
        
    # shuffle cards
    random.shuffle(cards)

    # setup players
    for player in players:
        # setup pieces
        player["pieces"] = []
        for i in range(big_guys):
            player["pieces"].append({"type":"big","position": None,"color":None})
        for i in range(little_guys):
            player["pieces"].append({"type":"little","position": None,"color":None})

        # setup piles
        player["piles"] = {}
        for color in range(colors):
            player["piles"][color] = []

        # distribute cards
        player["cards"] = []
        for i in range(hand_size):
            player["cards"].append(cards.pop())
        
        # discard variable
        player["times_discarded"] = 0

        # tokens variable
        player["tokens"] = 0

        # coins variable
        player["coins"] = 0

    # DEBUG
    # print(players)
    # quit()

    # game
    player_turn = player_start_turn
    passed_bridge = 0
    round_number = 1
    while len(cards) > 0 and passed_bridge < passed_bridge_max :
        
        # turn
        player = players[player_turn]

        # calculate next turn
        if player_turn >= len(players)-1:
            player_turn = 0
            round_number += 1
        else:
            player_turn += 1
        
        # var to see if we need to try the next option
        turn_complete = False

        # check if we should start a new pile
        piles_used = 0
        for color, pile in player["piles"].items():
            if len(pile) > 0:
                piles_used += 1

        if piles_used < player["pile_max"]:
            for card in sorted(player["cards"], key = lambda i: i['number']):
                if card["number"] <= player["start_cutoff"] and len(player["piles"][card["color"]]) == 0:
                    move_self(card, last_space, player, board)
                    turn_complete = True
                    break

        # play card
        if not turn_complete:
            # find differences
            for card in player["cards"]:
                if len(player["piles"][card["color"]]) > 0:
                    card["dif"] = card["number"] - player["piles"][card["color"]][-1]["number"]
                else:
                    card["dif"] = None
            
            # choose card less than max dif
            for card in sorted(player["cards"], key = lambda i: i['dif']):
                if card["dif"] != None and card["dif"] >= 0 and card["dif"] <= player["max_dif"]:
                    move_self(card, last_space, player, board)
                    turn_complete = True
                    break

        # use a card with high dif if we've discarded too many
        if not turn_complete and player["times_discarded"] >= player["max_discard"]:
            for card in sorted(player["cards"], key = lambda i: i['dif']):
                if card["dif"] != None and card["dif"] >= 0:
                    move_self(card, last_space, player, board)
                    turn_complete = True
                    break
        
        # discard not usable card
        if not turn_complete:
            for card in sorted(player["cards"], key = lambda i: i['dif']):
                if card["dif"] != None and card["dif"] < 0:
                    del card["dif"]
                    player["cards"].remove(card)
                    discard_piles[card["color"]].append(card)
                    player["times_discarded"] += 1
                    turn_complete = True
                    break

        # discard color not used and not many cards
        if not turn_complete:
            #count num of each color
            color_quant = {}
            for color in range(colors):
                color_quant[color] = 0
            for card in player["cards"]:
                color_quant[card["color"]] += 1

            # in order of least other colors, check if any piles exist and if not then discard
            for color, num in sorted(color_quant.items(), key=lambda item: item[1]):
                if num > 0:
                    for card in player["cards"]:
                        if card["color"] == color:
                            if len(player["piles"][card["color"]]) == 0:
                                del card["dif"]
                                player["cards"].remove(card)
                                discard_piles[card["color"]].append(card)
                                player["times_discarded"] += 1
                                turn_complete = True
                                break

        # use a card with high dif
        if not turn_complete:
            for card in sorted(player["cards"], key = lambda i: i['dif']):
                if card["dif"] != None and card["dif"] >= 0:
                    move_self(card, last_space, player, board)
                    turn_complete = True
                    break

        # last resort -- choose random
        if not turn_complete:
            random.shuffle(player["cards"])
            new_discard = player["cards"].pop()
            del new_discard["dif"]
            discard_piles[new_discard["color"]].append(new_discard)
            player["times_discarded"] += 1


        # take new cards
        took_from_discard = False
        for color, pile in discard_piles.items():
            if len(pile)>0 and len(player["piles"][color]) > 0:
                topcard = pile[-1]
                if topcard["number"] - player["piles"][color][-1]["number"] >= 0:
                    player["cards"].append(topcard)
                    pile.remove(topcard)
                    took_from_discard = True
        if not took_from_discard:
            player["cards"].append(cards.pop())


        passed_bridge = 0
        for player_bridge in players:
            for piece_bridge in  player_bridge["pieces"]:
                if piece_bridge["position"] >= bridge_location:
                    passed_bridge +=1

        # DEBUG
        # if round_number >= 20:
        #     for piece in player["pieces"]:
        #         print(piece["color"],piece["position"])
        #     quit()

   

    i = 0
    while i < len(players):
        player = players[i]
        points = 0
        # print ("player number: "+ str(i+1))
        for piece in player["pieces"]:
            # print(piece)
            if piece["position"]:
                points += points_map[piece["position"]-1]
                if piece["type"] == "big":
                    points += points_map[piece["position"]-1]
        
        points += player["coins"]
        if player["tokens"] >=6:
            player["tokens"] = 5
        points += tokens_map[player["tokens"]]

        avg_points.append(points)
        # print("points: "+str(points))
        # print("")
        i += 1

    # print("passed bridge: "+str(passed_bridge))
    # print("round number: "+str(round_number))
    # print("cards remaining: "+str(len(cards)))
def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None

print ("average:" + str(sum(avg_points) / len(avg_points)))
print ("median:" + str(median(avg_points)))
