import discord
from discord.ext import commands
import os
import pandas as pd

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# global variables
rejections_file = None
col_names = ['Guild','Goal','Rejections','Celebrations','Reset']
default_goal = 25

# record a rejection, and celebrate if you've hit your goal
@bot.command(
    name="damage", 
    brief="To log a rejection, use the command *!damage 1* for one rejection, or change the number for multiple.", 
    description="To log a rejection, use the command *!damage 1* for one rejection, or change the number for multiple."
)
async def damage(context, num: int):
    celebrate = False
    rejections_df, guild_id, goal, rejections, celebrations, reset = get_guild_info(context) 
    for r in range(num):
        rejections += 1
        if int(rejections-reset) % goal == 0:
            celebrate = True
    rejections_df.loc[rejections_df['Guild'] == guild_id, 'Rejections'] = rejections
    if celebrate == True:
        reset = rejections
        celebrations += 1
        rejections_df.loc[rejections_df['Guild'] == guild_id, 'Reset'] = reset
        rejections_df.loc[rejections_df['Guild'] == guild_id, 'Celebrations'] = celebrations
        await context.reply(f"You are at {rejections} total rejections, and that means: :tada: :partying_face: congratulations, you've reached another {goal} rejections! :partying_face: :tada:  Rejection-sama demands that you go celebrate!")
    else:
        await context.reply(f"Rejection-sama thanks you for the rejections!  You're at {rejections} total rejections.") 
    rejections_df.loc[rejections_df['Guild'] == guild_id, 'Rejections'] = rejections
    rejections_df.to_csv(rejections_file, index=False)

# remove rejections if you accidentally on purpose add too many 
@bot.command(name="oops", 
    brief="To remove a rejection, use the command *!oops 1* to remove one rejection, or change the number for multiple.", 
    description="To remove a rejection, use the command *!oops 1* to remove one rejection, or change the number for multiple."
)
async def oops(context, num: int):
    rejections_df, guild_id, goal, rejections, celebrations, reset = get_guild_info(context)
    rejections -= num
    if rejections < 0:
        rejections = 0
        await context.reply(f"Rejection-sama cannot give you negative rejections, much as Rejection-sama would like... you are now at 0 rejections.")
    else:
        await context.reply(f"Rejection-sama has removed {num} rejections!  You are now at {rejections} total rejections.")
    rejections_df.loc[rejections_df['Guild'] == guild_id, 'Rejections'] = rejections
    rejections_df.to_csv(rejections_file, index=False)

# print the current number of rejections and the number of rejections left to the goal
@bot.command(name="progress",
    brief="To check the status of your rejections and how close you are to your goal, use the command *!progress*.",
    description="To check the status of your rejections and how close you are to your goal, use the command *!progress*."
)
async def progress(context):
    rejections_df, guild_id, goal, rejections, celebrations, reset = get_guild_info(context)
    to_go = goal - int(rejections-reset) % goal
    await context.reply(f"You are at {rejections} total rejections and have celebrated {celebrations} times.  Your last celebration was at {reset} rejections.  You have {to_go} rejections left to your next goal of {goal} rejections!")

# set goal number of rejections 
# if the new goal means a celebration has been reached, a celebration will be prompted, but only one
@bot.command(name="goal", 
    brief="To change your goal, use the command *!goal 50* to set your goal to 50 rejections, or use another number.", 
    description="To change your goal, use the command *!goal 50* to set your goal to 50 rejections, or use another number.  The goal is always counted as the number of rejections from your last celebration.  If you change your goal while progressing towards your next celebration and the new goal is lower than the current number of rejections since that last celebration, you'll immediately earn a celebration and then start counting again from there.  For instance, if you are trying to get to 10, and then set your goal to 5 when you are at 7, you earn a celebration at 7 and will earn your next celebration at 12."
)
async def goal(context, num: int):
    rejections_df, guild_id, goal, rejections, celebrations, reset = get_guild_info(context)
    if int((rejections-reset)/goal) < int((rejections-reset)/num):
        await context.reply(f"By resetting your goal to {num}, you have reached another celebration!  You may go celebrate if you wish!")
        await context.reply(f"Your goal is now to reach another {num} rejections from here.")
        rejections_df.loc[rejections_df['Guild'] == guild_id, 'Celebrations'] = celebrations + 1
    else:
        to_go = num - int(rejections-reset) % num
        await context.reply(f"Your goal is now to reach another {num} rejections, you have {to_go} rejections left to your next goal!")
    rejections_df.loc[rejections_df['Guild'] == guild_id, 'Goal'] = num
    rejections_df.to_csv(rejections_file, index=False)    

@bot.event
async def on_ready():
    print(f'Rejection-sama has been summoned! Target rejections set to {default_goal}, to set to another value, use goal command.')
        
def get_guild_info(context):
    guild_id = context.message.guild.id
    try:
        rejections_df = pd.read_csv(rejections_file)
    except:
        to_df = {}
        for i in col_names:
            to_df[i] = []
        rejections_df = pd.DataFrame(to_df, dtype=int)
    if guild_id not in rejections_df['Guild'].values:
        guild_to_append = pd.DataFrame({
            'Guild': [guild_id],
            'Goal': [default_goal],
            'Rejections': [0],
            'Celebrations': [0],
            'Reset': [0]
         })
        rejections_df = pd.concat([rejections_df,guild_to_append],names=col_names) 
        rejections_df.to_csv(rejections_file, index=False)
    guild_loc = rejections_df['Guild'] == guild_id 
    rejections = rejections_df.loc[guild_loc, 'Rejections'].item()
    goal = rejections_df.loc[guild_loc, 'Goal'].item()
    celebrations = rejections_df.loc[guild_loc, 'Celebrations'].item()
    resets = rejections_df.loc[guild_loc, 'Reset'].item() 
    return(rejections_df, guild_id, goal, rejections, celebrations, resets)

def main():
    with open(os.environ.get('DISCORD_TOKEN_FILE', './rejection_token_file.txt'), 'r') as f:
        TOKEN = f.read()
    global rejections_file
    rejections_file = os.environ.get('REJECTIONS_FILE', './rejections.csv')
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
