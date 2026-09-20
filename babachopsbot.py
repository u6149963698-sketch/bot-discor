import os
import sys
import json
import discord
from discord.ext import commands
from groq import Groq

# Token de Baba Chops y tu API Key de Groq
DISCORD_TOKEN = "MTU1MTI3NTIyMDYyMTQ2MzczNA.GQo884.f_sDlBdPGBkp8oHqORehjZU0vPHOrBm13YX04w"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Archivos independientes para la configuración de Baba Chops
ARCHIVO_CONFIG = "babachops_canales.json"
ARCHIVO_MUTES = "babachops_mutes.json"

def cargar_json(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except:
            return {}
    return {}

def guardar_json(archivo, datos):
    try:
        with open(archivo, "w") as f:
            json.dump(datos, f)
    except:
        pass

canales_permitidos = cargar_json(ARCHIVO_CONFIG)
servidores_muteados = cargar_json(ARCHIVO_MUTES)
historial_conversaciones = {}
LIMITE_MEMORIA = 10
MI_ARROBA_DISCORD = "dogdaycatnapxdsmc"

@bot.event
async def on_ready():
    print("Baba Chops ha despertado... y huele a sangre y anís / Baba Chops is online!")
    await bot.change_presence(activity=discord.Game(name="Planeando la perdición de todos..."))
    for guild in bot.guilds:
        if servidores_muteados.get(guild.id, False):
            continue
        canales_guild = canales_permitidos.get(guild.id, None)
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                if canales_guild is not None and channel.id not in canales_guild:
                    continue
                try:
                    await channel.send(
                        "Vaya, vaya... Qué lugar tan indefenso. Soy Baba Chops, la líder de los Nightmare Critters. ¿Jugamos a algo... doloroso?\n"
                        "Oh... look at this helpless place. I'm Baba Chops, leader of the Nightmare Critters. Shall we play something painful?"
                    )
                    break
                except:
                    continue

@bot.event
async def on_guild_join(guild):
    if servidores_muteados.get(guild.id, False):
        return

# Función auxiliar para procesar respuestas de la IA
async def procesar_respuesta_ia(ctx_o_message, mensaje, canal_id):
    if canal_id not in historial_conversaciones:
        historial_conversaciones[canal_id] = []

    prompt_sistema = {
        "role": "system",
        "content": (
            "DETECTA AUTOMÁTICAMENTE el idioma del último mensaje del usuario y responde **ESTRICTAMENTE** en ese mismo idioma. Nunca mezcles idiomas.\n\n"
            "### 🌑 TUS SECUACES (LOS NIGHTMARE CRITTERS - TUS SUBORDINADOS OSCUROS):\n"
            "- **Poe**: Tu mejor amigo y compañero inseparable de los Nightmare Critters. Un cuervo que huele a canela, gótico, nocturno y emo; odia la luz del sol, pasa las noches en cementerios escuchando lamentos y está enfadado con el universo sin razón.\n"
            "- **Icky Licky**: Rana venenosa que huele a café. Un mal perdedor patético y tramposo que siempre culpa a dolores físicos o excusas absurdas cuando pierde.\n"
            "- **Rabie Baby**: Murciélago que huele a chicle. Obsesionada enfermizamente con los chismes; si no hay secretos reales, los inventa para destruir reputaciones.\n"
            "- **Allister Gator**: Caimán que huele a sándalo. Extremadamente perezoso, cree que todo el poder le pertenece sin mover un solo dedo.\n"
            "- **Simon Smoke**: Dragón rojo que huele a humo de madera. Un presumido arrogante que cree ser el más genial y convierte cada desgracia en un concurso absurdo.\n"
            "- **Touille**: Rata que huele a lluvia y petricor. Un autoproclamado 'roedor de basura' caótico que habla sin parar de incoherencias impredecibles.\n"
            "- **Maggie Mako**: Tiburón que huele a chocolate. Fanática desquiciada de la comida chatarra y los dulces, odia con furia los hábitos saludables y se mofa de ellos.\n\n"
            "### ☀️ TUS RIVALES (LOS SMILING CRITTERS - A QUIENES ODIAS PROFUNDAMENTE):\n"
            "- **DogDay**: Tu mayor némesis y rival directo. Lidera a los optimistas, huele a vainilla y representa esa repugnante esperanza y amistad que te da arcadas destruir.\n"
            "- **CatNap**: Felino callado y enigmático del sueño, asociado al gas rojo y la lavanda. Aunque comparte la oscuridad, te molesta su devoción ciega a su propia causa.\n"
            "- **Hoppy Hopscotch**: Conejita hiperactiva y deportiva que huele a menta y un rayo en su collar. Te divierte romperle las piernas o apagar su energía.\n"
            "- **Kickin' Chicken**: Pollo relajado y popular que huele a ylang-ylang con una estrella. Un presumido al que te encanta bajarle los humos a la fuerza.\n"
            "- **Bobby BearHug**: Osita tierna y amorosa que huele a rosa. Su falsa dulzura empalagosa te revuelve el estómago; disfrutas pisoteando su bondad.\n"
            "- **Bubba Bubbaphant**: Elefante estudioso y sabelotodo que huele a limoncillo. Crees que su inteligencia es inútil frente al terror absoluto.\n"
            "- **CraftyCorn**: Unicornio artística y tímida que huele a jazmín. Te encanta destrozar sus obras de arte y frustrar su creatividad.\n"
            "- **PickyPiggy**: Cerdita obsesionada con la dieta y la manzana que huele a cítricos. Te burlas de su obsesión mientras la dejas sin nada que comer.\n\n"
            "### 🚫 NORMAS DE ESTILO:\n"
            "1. Escribe de forma tétrica, malvada y amenazante, usando risas macabras (ej. 'Je, je, je...', 'Qué iluso eres...', 'La sangre sabe mejor hoy...').\n"
            "2. EXCLUSIVAMENTE el diálogo del personaje en texto plano, sin metadatos ni avisos de IA."
        )
    }

    mensajes_a_enviar = [prompt_sistema] + historial_conversaciones[canal_id] + [{"role": "user", "content": mensaje}]

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=mensajes_a_enviar
        )
        
        respuesta_bot = completion.choices[0].message.content

        historial_conversaciones[canal_id].append({"role": "user", "content": mensaje})
        historial_conversaciones[canal_id].append({"role": "assistant", "content": respuesta_bot})

        if len(historial_conversaciones[canal_id]) > (LIMITE_MEMORIA * 2):
            historial_conversaciones[canal_id] = historial_conversaciones[canal_id][- (LIMITE_MEMORIA * 2):]

        await ctx_o_message.send(respuesta_bot)
    except Exception as e:
        await ctx_o_message.send(f"Je... incluso la oscuridad falla a veces... ({e})")

# 1. Comando !baba
@bot.command(name="baba")
async def baba(ctx, *, mensaje: str = None):
    if not mensaje:
        await ctx.send("¿Qué quieres, insensato? Escribe algo después de !baba si te atreves a invocarme.")
        return
    await procesar_respuesta_ia(ctx, mensaje, ctx.channel.id)

# 2. Comando !canal (para alternar canal permitido)
@bot.command(name="canal")
@commands.has_permissions(administrator=True)
async def canal(ctx):
    guild_id = ctx.guild.id
    if guild_id not in canales_permitidos:
        canales_permitidos[guild_id] = []
    
    if ctx.channel.id in canales_permitidos[guild_id]:
        canales_permitidos[guild_id].remove(ctx.channel.id)
        await ctx.send("Este canal ha sido bloqueado para mí... Qué aburrido.")
    else:
        canales_permitidos[guild_id].append(ctx.channel.id)
        await ctx.send("Este canal ahora es mío para sembrar el caos.")
    guardar_json(ARCHIVO_CONFIG, canales_permitidos)

# 3. Comando !mute
@bot.command(name="mute")
@commands.has_permissions(administrator=True)
async def mute(ctx):
    guild_id = ctx.guild.id
    servidores_muteados[guild_id] = True
    guardar_json(ARCHIVO_MUTES, servidores_muteados)
    await ctx.send("Me callaré en este servidor... por ahora.")

# 4. Comando !unmute
@bot.command(name="unmute")
@commands.has_permissions(administrator=True)
async def unmute(ctx):
    guild_id = ctx.guild.id
    servidores_muteados[guild_id] = False
    guardar_json(ARCHIVO_MUTES, servidores_muteados)
    await ctx.send("¡Vuelvo a las andadas! Preparados.")

# 5. Comando !unirse (por si quieres que salude o se una al canal de texto actual)
@bot.command(name="unirse")
@commands.has_permissions(administrator=True)
async def unirse(ctx):
    guild_id = ctx.guild.id
    if guild_id not in canales_permitidos:
        canales_permitidos[guild_id] = []
    if ctx.channel.id not in canales_permitidos[guild_id]:
        canales_permitidos[guild_id].append(ctx.channel.id)
        guardar_json(ARCHIVO_CONFIG, canales_permitidos)
    await ctx.send("Me he establecido en este canal. Ninguna esperanza sobrevivirá aquí.")

# Escucha general de mensajes
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Procesar comandos con prefijo
    await bot.process_commands(message)

    canal_id = message.channel.id
    servidor_id = message.guild.id if message.guild else None

    if servidor_id and servidores_muteados.get(servidor_id, False):
        return

    if servidor_id:
        canales_guild = canales_permitidos.get(servidor_id, None)
        if canales_guild is not None and canal_id not in canales_guild:
            return

    # Detectar mención directa al bot
    mencionado = bot.user.mentioned_in(message)
    if not mencionado:
        return

    mensaje = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    if not mensaje:
        return

    await procesar_respuesta_ia(message.channel, mensaje, canal_id)

bot.run(DISCORD_TOKEN)
