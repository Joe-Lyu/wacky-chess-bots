import discord
import pickle
import random
from chess_framework import create_game, make_move, ChessPlayer

TOKEN = pickle.load(open('token.pkl','rb')) #not gonna show my token to ya :)



class ChessBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!challenge'):
            await message.reply("Ping who you want to challenge!")
            def is_name(msg):
                members = client.guilds[0].members
                member_ids = [member.id for member in members]
                try:
                    pinged_id = int(msg.content.lstrip('<@').rstrip('>'))
                except:
                    return False
                return msg.author == message.author and pinged_id in member_ids
            opponent = await self.wait_for('message', check=is_name)
            opponent = int(opponent.content.lstrip('<@').rstrip('>'))
            opponent = self.get_user(opponent)
            await message.channel.send("To accept the challenge, type \"yes\"")
            def is_yes(msg):
                return message.author == opponent and msg.content.lower() == "yes"
            accept = await self.wait_for('message', check=is_yes)
            if accept:
                await message.channel.send("Challenge accepted!")

                players = [message.author, opponent]
                random.shuffle(players)
                white, black = players
                game_name = f'{white.display_name} vs {black.display_name}'
                create_game(game_name,white.display_name,black.display_name)
                
                movecnt = 1
                while True:
                    print(movecnt)
                    await message.channel.send(file = discord.File('board.png'))
                    def is_white_move(msg):
                        return msg.author == white and len(msg.content) <= 6
                    def is_black_move(msg):
                        return msg.author == black and len(msg.content) <= 6
                    is_legal = False
                    while not is_legal:
                        if movecnt % 2 == 1:
                            move = await self.wait_for('message', check=is_white_move)
                            move = move.content
                        else:
                            move = await self.wait_for('message', check=is_black_move)
                            move = move.content
                        movecnt += 1
                        gamestate = make_move(game_name,move)
                        if gamestate != False:
                            is_legal = True

                    if type(gamestate) == str:
                        return await message.reply(f"Game finished; {gamestate}")
       
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = ChessBot(intents=intents)
client.run(TOKEN)