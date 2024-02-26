import discord
from discord.ext import commands
import wolframalpha
import math
import matplotlib.pyplot as plt

class Equation():
    def __init__(self, values):
        self.values = values

    def get_zeros(self):
        a, b, c = self.values
        x = (b**2) - (4*a*c)

        x1 = (-b + math.sqrt(x)) / (2*a)
        x2 = (-b - math.sqrt(x)) / (2*a)

        return x1, x2

    def get_vertex(self):
        a, b, c = self.values

        x = (-b) / (2*a)

        y = ((4*a*c) - (b**2)) / (4*a)

        return x, y
    
    def get_standard_form(self):
        a, b, c = self.values

        return '{}x^2 + {}x + {}'.format(a, b, c)
    
    def get_vertex_form(self):
        a = self.values[0]
        h, k = self.get_vertex()

        return f"{a}(x-{h})^2 + {k}"
    
async def graph(equation):
    a, b, c = equation.values
    r1, r2 = equation.get_zeros()

    if r1 < r2:
        x = r1
        y = r2

    else:
        x = r2
        y = r1

    roots1 = []
    roots2 = []

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # Set axes
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('zero')

    ax.spines['right'].set_color('none') # remove vertical box line
    ax.spines['top'].set_color('none') # remove horizontal box line

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    while x < y:
        base = float((a*(x**2)) + (b*x) + c)

        roots1.append(x)
        roots2.append(base)
        x += 0.0001

    plt.plot(roots1, roots2, 'g')
    plt.savefig('./harper/lib/images/quadratics.png')

class Homework(commands.Cog):

    """Homework"""

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['d'])
    @commands.is_owner()
    async def download(self, ctx, day, page=1):
        
        cur = await self.client.db.cursor()
        await cur.execute('SELECT fullname, topic FROM homework WHERE id = ?', (ctx.author.id,))
        name, topic = await cur.fetchone()
        await cur.close()

        filename = f"./homework/{name} - Day {day} {topic} Page #{page}"

        for attachment in ctx.message.attachments:
            await attachment.save(filename + attachment.filename[-4:])
            await ctx.send(f"Saved `{filename[11:]}`")

    @commands.command(aliases=['conf-hw'])
    @commands.is_owner()
    async def config_homework(self, ctx, new_topic, *, new_name):
            
        cur = await self.client.db.cursor()
        await cur.execute('SELECT fullname, topic FROM homework WHERE id = ?', (ctx.author.id,))
        name, topic = await cur.fetchone()
        
        if not name and not topic:
            await cur.execute('INSERT INTO homework (id, fullname, topic) VALUES (?, ?, ?)', (ctx.author.id, new_name, new_topic))

        else:
            await cur.execute('UPDATE homework SET fullname = ?, topic = ? WHERE id = ?', (new_name, new_topic, ctx.author.id))
        
        await cur.close()
        await self.client.db.commit()

        await ctx.send(f"`New name: {new_name}\nNew topic: {new_topic}`")
    
    @commands.command(aliases=['quadratic'])
    async def quadratics(self, ctx, a: int, b: int, c: int):
        
        await ctx.trigger_typing()

        eq = Equation((a, b, c))
        
        standard_form = eq.get_standard_form()
        vertex_form = eq.get_vertex_form()
        a, b, c = eq.values
        x1, x2 = eq.get_zeros()
        x, y = eq.get_vertex()
        answer = "[+] Standard Form = {}\n[+] Vertex Form = {}\n[+] 1st zero/root = {}\n[+] 2nd zero/root = {}\n[+] Vertex = {}\n[+] AOS: x = {}".format(standard_form, vertex_form, x1, x2, (x, y), x)
        await graph(eq)

        await ctx.send(content=answer, file=discord.File('./harper/lib/images/quadratics.png'))
    
    @commands.command(aliases=['wlfram'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wolfram(self, ctx, *, question):

        await ctx.trigger_typing()
  
        wolfram = wolframalpha.Client(self.client.wolfram_id) 
        res = wolfram.query(question) 
        answer = next(res.results).text 

        await ctx.send(answer)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.client.ready:
            self.client.cogs_ready.ready_up('Homework')

def setup(client):
    client.add_cog(Homework(client))