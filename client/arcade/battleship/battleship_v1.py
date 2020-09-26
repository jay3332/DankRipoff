## This version of battleship is very buggy. ##
## I recommend for you to use another battleship code! ##

# # # NOTE: some functions used here are not pre-defined. Use this at your own risk. # # # 
# # # NOTE: some parts of this code may not be the most efficient or the most organized. # # #

# # # ## # # #
# version: 1 #
# # # ## # # #

if command=='battleship' or command=='bs':
    start_message = await ctx.send(embed=self.embed(
        'Battleship',
        f'**{curr_user}** (Level {user_data["arcade_level"]}) wants to play a game of **battleship**!\n'
        f'React with 🎮 to play.',
        footer='You have 120 seconds.'
    ).set_author(name="🎮 Arcade"))
    await start_message.add_reaction('🎮')
    self.in_game.append(ctx.author.id)
    try:
        temp, tempu = await self.client.wait_for('reaction_add', timeout=120,
                                                 check=lambda reaction, user:
                                                          ((str(reaction.emoji))=='🎮')
                                                          and (user.id!=ctx.author.id)
                                                          and (user.id not in self.in_game)
                                                          and (reaction.message.id==start_message.id)
                                                          and (not user.bot))
    except Exception as error:
        await ctx.send('No one wanted to play with you.')
        self.in_game.remove(ctx.author.id)
        raise error
        #return
    player1 = ctx.author
    player2 = tempu
    op_data = await self.db.getindex(player2)
    self.in_game.append(player2.id)

    emotes = {
        'blank': '⚫',
        '0': '<:navy_square:758725624117329960>', # NAVY blue
        'water': '<:navy_square:758725624117329960>',
        'you_hit': '🔸',
        'you_miss': '🔹',
        '5': '🟥', # red
        '4': '🟪', # purple
        '31': '🟦', # blue
        '32': '🟩', # green
        '2': '🟧', # orange
        'hit': '💥',
        'miss': '💢'
    }

    await ctx.send(f'{player2.mention} ({op_data["arcade_level"]}) is now playing with'
                   f' {player1.mention} ({op_data["arcade_level"]}).\n{player1.mention} will go first.',
                   allowed_mentions=discord.AllowedMentions(users=True))

    p1board = [
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    ]

    p2board = [
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    ]

    def spawn():
        existing_coords = []
        ret = {
            "5": [],
            "4": [],
            "31": [],
            "32": [],
            "2": []
        }
        for ship in ret:
            length = int(ship[0])
            while True:
                hv = random.choice(['h', 'v'])
                temp_coords = []
                while True:
                    coord = (random.randint(1,10), random.randint(1,10))
                    if coord not in existing_coords:break
                temp_coords.append(coord)
                for i in range(length-1):
                    if hv=='h':
                        coord = (coord[0]+1, coord[1])
                        temp_coords.append(coord)
                    elif hv=='v':
                        coord = (coord[0], coord[1]+1)
                        temp_coords.append(coord)
                succ = True
                for c in temp_coords:
                    if c in existing_coords or (c[0]>10 or c[1]>10):
                        succ = False
                        break
                    else:
                        succ = True
                if succ:
                    existing_coords.extend(temp_coords)
                    ret[ship] = temp_coords
                    break
        return ret

    def get_all_coords(s):
        ret = []
        for i in s:
            ret.extend(s[i])
        return ret

    p1spawn = spawn()
    p2spawn = spawn()

    p1hitcoords = {}
    p2hitcoords = {}

    ships = ['5', '4', '31', '32', '2']
    for ship in ships:
        for coord in p1spawn[ship]:
            x, y = coord[0]-1, coord[1]-1
            p1board[y][x] = ship

        for coord in p2spawn[ship]:
            x, y = coord[0]-1, coord[1]-1
            p2board[y][x] = ship


    def render_board(board, opponent_hit_points):
        rows = ['`   A  B  C  D  E  F  G  H  I  J`']
        row_num = 0
        succ_hits = []
        bad_hits = []
        for item in opponent_hit_points:
            if opponent_hit_points[item]:
               succ_hits.append(item)
            else:bad_hits.append(item)
        for i in board:
            row_num+=1
            n = f'`{" " if not row_num==10 else ""}{row_num}`'
            col_num=0
            for j in i:
                col_num+=1
                if (col_num, row_num) in succ_hits:
                    n += emotes['hit']
                elif (col_num, row_num) in bad_hits:
                    n += emotes['miss']
                else:
                    n += emotes[j]
            rows.append(n)
        rows = '\n'.join(rows)
        return rows

    def render_hit_points(hit_points):
        rows = ['`   A  B  C  D  E  F  G  H  I  J`']
        br = [
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
        ]
        for point in hit_points:
            x, y = point[0]-1, point[1]-1
            br[y][x] = "1"

        row_num = 0
        for i in br:
            row_num += 1
            n = f'`{" " if not row_num==10 else ""}{row_num}`'
            m = 0
            for j in i:
                m += 1
                if j=='0':
                    n += emotes['blank']
                elif j=='1':
                    coord = (m, row_num)
                    if hit_points[coord]:
                        n += emotes['you_hit']
                    else:
                        n += emotes['you_miss']
            rows.append(n)

        rows = '\n'.join(rows)
        return rows

    shipnames = {
        "5": "Carrier",
        "4": "Battleship",
        "31": "Cruiser",
        "32": "Submarine",
        "2": "Destroyer"
    }

    turn = player1
    old_sunk_ships = []
    while True:
        oppo = player2 if turn==player1 else player1

        for part in splitLine("Your board:\n"+render_board(p1board, p2hitcoords), 2000):
            await player1.send(part)
        for part in splitLine("Your board:\n"+render_board(p2board, p1hitcoords), 2000):
            await player2.send(part)

        for part in splitLine("_ _\nTheir board:\n"+render_hit_points(p1hitcoords), 2000):
            await player1.send(part)
        for part in splitLine("_ _\nTheir board:\n"+render_hit_points(p2hitcoords), 2000):
            await player2.send(part)

        await turn.send(embed=self.embed(
            'It\'s your turn!',
            f'Type the coordinates of the point you want to aim for.'
            f'\nFormat it like `<alphabet><number>`, e.g.:\n'
            f'`A1` for the top left or `E5` for the center.\n'
            f'You may also type `surrender` to end the game.'
        ))

        await oppo.send('Waiting for your opponent\'s move...')

        avail = list('ABCDEFGHIJ')
        conv = {
            "A":1, "B":2, "C":3, "D":4, "E":5,
            "F":6, "G":7, "H":8, "I":9, "J":10
        }

        def check(m):
            if (m.channel == turn.dm_channel
                and m.author == turn):
                if m.content.lower()=='surrender':
                    return True
            try:
                return (m.channel == turn.dm_channel
                and m.author == turn and (m.content.upper()[0] in avail)
                and (int(m.content[1:]) > 0 and int(m.content[1:]) < 11))
            except:return False

        while True:
            hit_point = await self.client.wait_for('message', check=check)
            if hit_point.content.lower()=='surrender':
                await turn.send(f'You surrendered and ended the game, what a wimp')
                await oppo.send(f'Your opponent surrendered. The game is over.')
                self.in_game.remove(player1.id)
                self.in_game.remove(player2.id)
                return
            hit_point = hit_point.content.upper()
            in_tuple = (conv[hit_point[0]], int(hit_point[1:]))
            used_coords = p1hitcoords if turn==player1 else p2hitcoords
            if in_tuple in list(used_coords):
                await turn.send('You\'ve already hit there!\n'
                                'Aim at a spot you haven\'t used before.')
            else:break

        all_coords = get_all_coords(p1spawn if oppo==player1 else p2spawn)
        hit = None
        if in_tuple in all_coords:hit = True
        else:hit = False
        if turn==player1:p1hitcoords[in_tuple] = hit
        else:p2hitcoords[in_tuple] = hit

        if hit:
            await turn.send(embed=self.embed(
                f'Coordinates `{hit_point}`',
                f'{hit_point} was **hit**!'
            ))

            await oppo.send(embed=self.embed(
                description=f'Your opponent went for **{hit_point}**, which was a hit.'
            ))
        else:
            await turn.send(embed=self.embed(
                f'Coordinates `{hit_point}`',
                f'{hit_point} was **miss**.'
            ))

            await oppo.send(embed=self.embed(
                description=f'Your opponent went for **{hit_point}**, which was a miss.'
            ))

        used_coords = p1hitcoords if turn == player1 else p2hitcoords
        spawn = p1spawn if oppo==player1 else p2spawn
        sunk = False
        sunk_ship = None
        for ship in list(spawn):
            cds = spawn[ship]
            if all(cd in used_coords for cd in cds) and (tuple([ship, turn]) not in old_sunk_ships):
                sunk = True
                sunk_ship = ship
            else:
                sunk = False

        if sunk:
            old_sunk_ships.append((sunk_ship, turn))
            await turn.send(f'{turn.mention}, You\'ve sunk your opponent\'s **{shipnames[sunk_ship]}**!', allowed_mentions=discord.AllowedMentions(users=True))
            await oppo.send(f'{oppo.mention}, Oh no! Your opponent has sunk your **{shipnames[sunk_ship]}**!', allowed_mentions=discord.AllowedMentions(users=True))

        won = False
        winner = None

        used = list(used_coords)
        if all(k in all_coords for k in used):
            won = True
            winner = turn

        turn = oppo

        if won:
            await ctx.send(f'{winner} won')
            break

        # FIX: sunken ship like every move
        # FIX: not detecting win
        # ADD: add xp/coins
        # ADD: nukes



    self.in_game.remove(player1.id)
    self.in_game.remove(player2.id)
