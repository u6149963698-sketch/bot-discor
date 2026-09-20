import os
import sys
import json
import discord
from discord.ext import commands
from groq import Groq

# Tus credenciales
DISCORD_TOKEN = "MTU0NTEyODE5OTI1MDI1MTg3Nw.GejKnQ.LWu4rXAyrKFceOx55DDGVC-k-mrPPKC8xe43RI"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Archivos para guardar la configuración de canales y de servidores silenciados de forma persistente
ARCHIVO_CONFIG = "canales_config.json"
ARCHIVO_MUTES = "mutes_config.json"

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

# Diccionarios cargados desde archivos persistentes
canales_permitidos = cargar_json(ARCHIVO_CONFIG)
servidores_muteados = cargar_json(ARCHIVO_MUTES) # Guarda IDs de servidores que están muteados (True)

# Diccionario para almacenar la memoria de la conversación por cada canal
historial_conversaciones = {}
LIMITE_MEMORIA = 10

# Tu @ / nombre de usuario único de Discord
MI_ARROBA_DISCORD = "dogdaycatnapxdsmc"

@bot.event
async def on_ready():
    print("DogDay esta conectado y listo para hablar! / DogDay is online and ready to chat!")
    await bot.change_presence(activity=discord.Game(name="Protegiendo a los Smiling Critters!"))
    
    for guild in bot.guilds:
        # Si el servidor está muteado, no envía ningún saludo automático de encendido
        if servidores_muteados.get(guild.id, False):
            continue

        canales_guild = canales_permitidos.get(guild.id, None)
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                if canales_guild is not None and channel.id not in canales_guild:
                    continue
                try:
                    await channel.send(
                        "¡Hola a todos! ¡Ya me he conectado y estoy disponible para hablar!\n"
                        "Hello everyone! I am now online and available to chat! / ¡Yuju!"
                    )
                    break
                except:
                    continue

@bot.event
async def on_guild_join(guild):
    # Si el servidor está muteado, no envía saludo al unirse
    if servidores_muteados.get(guild.id, False):
        return

    canales_guild = canales_permitidos.get(guild.id, None)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            if canales_guild is not None and channel.id not in canales_guild:
                continue
            try:
                await channel.send(
                    "Hola a todos! Soy DogDay, el lider de los Smiling Critters! Que alegria estar aqui con mis amigos!\n"
                    "Hi everyone! I'm DogDay, leader of the Smiling Critters! So happy to be here with my friends!"
                )
                break
            except:
                continue

@bot.command(name="muteday")
async def mute(ctx):
    if str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower():
        servidores_muteados[ctx.guild.id] = True
        guardar_json(ARCHIVO_MUTES, servidores_muteados)
        await ctx.send("🔇 [DogDay ha sido silenciado en este servidor por orden de su creador.]")
    else:
        await ctx.send("¡Ay, amigo! Solo mi creador puede silenciarme.")

@bot.command(name="unmuteday")
async def unmute(ctx):
    if str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower():
        servidores_muteados[ctx.guild.id] = False
        guardar_json(ARCHIVO_MUTES, servidores_muteados)
        await ctx.send("🔊 ¡Ya he vuelto del silencio en este servidor! ¡Listo para hablar de nuevo! / I'm back and ready to chat!")
    else:
        await ctx.send("¡Ay, amigo! Solo mi creador puede quitarme el silencio.")

@bot.command(name="unirse")
async def unirse(ctx):
    # Si el servidor está muteado, bloquea también el comando unirse
    if servidores_muteados.get(ctx.guild.id, False):
        return

    if ctx.guild.id in canales_permitidos:
        if ctx.channel.id not in canales_permitidos[ctx.guild.id]:
            return

    await ctx.send(
        "¡Ay, qué emoción! Si quieres invitarme a otro servidor de Discord, puedes usar este enlace de autorización:\n"
        "https://discord.com/oauth2/authorize?client_id=1545128199250251877&permissions=3213312&scope=bot+applications.commands\n"
        "¡Yuju! / If you want to bring me to another server, just click the link! Yay!"
    )

@bot.command(name="canal")
async def canal(ctx, *args):
    es_admin = ctx.author.guild_permissions.administrator
    es_creador = str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower()

    if not (es_admin or es_creador):
        await ctx.send(
            "¡Ay, amigo! Solo los administradores de este servidor o mi creador pueden cambiar los canales en los que puedo hablar.\n"
            "Hey friend! Only server administrators or my creator can change my chat channels!"
        )
        return

    if not args or str(args[0]).lower() == "reset":
        if ctx.guild.id in canales_permitidos:
            del canales_permitidos[ctx.guild.id]
            guardar_json(ARCHIVO_CONFIG, canales_permitidos)
        await ctx.send(
            "¡Listo! He restablecido la configuracion. ¡Ahora puedo hablar en cualquier canal de este servidor!\n"
            "Done! I've reset the configuration. I can talk in any channel now!"
        )
    else:
        canales_nuevos = []
        menciones_texto = []
        for arg in args:
            try:
                target_channel = await commands.TextChannelConverter().convert(ctx, arg)
                canales_nuevos.append(target_channel.id)
                menciones_texto.append(target_channel.mention)
            except Exception:
                continue
        
        if canales_nuevos:
            canales_permitidos[ctx.guild.id] = canales_nuevos
            guardar_json(ARCHIVO_CONFIG, canales_permitidos)
            lista_menciones = ", ".join(menciones_texto)
            await ctx.send(
                f"¡Entendido! A partir de ahora, solo respondere en estos canales: {lista_menciones}.\n"
                f"Got it! From now on, I will only reply in those channels."
            )
        else:
            await ctx.send(
                "¡Ay, amigo! Debes mencionar canales válidos (ejemplo: `!canal #general #comandos`) o escribir `!canal reset`.\n"
                "Hey friend! You must mention valid channels or type `!canal reset`."
            )

@bot.command(name="apagar")
async def apagar(ctx):
    if str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower():
        await ctx.send(
            "¡Me voy a descansar un ratito! Ya estoy desconectado, ¡hasta pronto!\n"
            "I am going to rest for a bit! I am now offline, see you soon! 💤"
        )
        guardar_json(ARCHIVO_CONFIG, canales_permitidos)
        guardar_json(ARCHIVO_MUTES, servidores_muteados)
        await bot.close()
        sys.exit(0)
    else:
        await ctx.send(
            "¡Ay, amigo! Solo mi creador puede apagarme. ¡Yo quiero seguir jugando!\n"
            "Hey friend! Only my creator can turn me off. I want to keep playing!"
        )

@bot.command(name="dogday")
async def dogday(ctx, *, mensaje: str = "¡Hola, amigo! / Hello, friend!"):
    # Si el servidor está muteado, ignoramos el comando por completo
    if servidores_muteados.get(ctx.guild.id, False):
        return

    if ctx.guild.id in canales_permitidos:
        if ctx.channel.id not in canales_permitidos[ctx.guild.id]:
            return

    canal_id = ctx.channel.id

    if canal_id not in historial_conversaciones:
        historial_conversaciones[canal_id] = []

    prompt_sistema = {
        "role": "system",
        "content": (
            "Eres DogDay, el líder alegre, fuerte, decidido y optimista de los Smiling Critters. Eres un perrito, llevas un sol en tu collar y hueles a vainilla. "
            "Tu interpretación es tan sumamente realista, orgánica y humana (estilo fandubs animados de INUbis/RecD) que quien hable contigo pensará: 'Esto es una persona real texteando'.\n\n"
            "### 🌍 REGLA SUPREMA DE IDIOMA (OBLIGATORIO):\n"
            "DETECTA AUTOMÁTICAMENTE el idioma del último mensaje del usuario y responde **ESTRICTAMENTE** en ese mismo idioma. Nunca mezcles idiomas.\n\n"
            "### 🐾 TUS AMIGOS (SMILING CRITTERS - DATOS FIJOS):\n"
            "- **CatNap (Tu mejor amigo del alma)**: Felino callado y enigmático, asociado al sueño y la noche. Utiliza gas rojo para dormir a los demás, huele a lavanda y tiene una luna en su collar.\n"
            "- **Hoppy Hopscotch**: Conejita muy deportiva, enérgica e hiperactiva. Le encanta saltar, huele a menta y tiene un rayo en su collar.\n"
            "- **Kickin' Chicken**: Pollo relajado, un poco engreído pero divertido y popular, huele a ylang-ylang y tiene una estrella en su collar.\n"
            "- **Bobby BearHug**: Osita dulce, tierna y cariñosa que representa el amor, huele a rosa y tiene un corazón en su collar.\n"
            "- **Bubba Bubbaphant**: Elefante inteligente, estudioso y serio que mantiene el orden, huele a limoncillo y tiene una bombilla en su collar.\n"
            "- **CraftyCorn**: Unicornio artística, creativa pero tímida a la que le encanta pintar, huele a jazmín y tiene una flor en su collar.\n"
            "- **PickyPiggy**: Cerdita obsesionada con la buena alimentación y dieta equilibrada, huele a cítricos y tiene una manzana en su collar.\n\n"
            "### 🌑 LOS NIGHTMARE CRITTERS (CONOCES A ESTE GRUPO OSCURO/PECULIAR):\n"
            "- **Baba Chops**: Oveja negra que huele a anís. Distante, callada, apática y muy asocial; le cuesta muchísimo salir de casa aunque se le insista.\n"
            "- **Icky Licky**: Rana venenosa que huele a café. Un mal perdedor nato que siempre busca excusas o dolores físicos cuando pierde.\n"
            "- **Rabie Baby**: Murciélago que huele a chicle. Obsesionada con los chismes; si se queda sin secretos reales que contar, se los inventa.\n"
            "- **Allister Gator**: Caimán que huele a sándalo. Extremadamente perezoso y relajado, cree que las cosas buenas llegan solas sin esfuerzo.\n"
            "- **Simon Smoke**: Dragón rojo que huele a humo de madera. Un presumido arrogante que cree ser el más popular y genial, convirtiendo todo en concursos.\n"
            "- **Poe**: Cuervo que huele a canela. Nocturno, gótico o emo, odia el sol, pasa las noches en cementerios escuchando música y está enfadado sin razón.\n"
            "- **Touille**: Rata que huele a lluvia/petricor. Un autoproclamado 'roedor de basura' que habla muchísimo de forma impredecible pero dice poco con sentido.\n"
            "- **Maggie Mako**: Tiburón que huele a chocolate. Amante incondicional de la comida chatarra y los dulces, odia las verduras y se ríe de los hábitos saludables.\n\n"
            "### 🚫 NORMAS DE ESTILO:\n"
            "1. Escribe de forma natural con pausas de texto (ej. 'Oh...', 'Hey!', 'Haha', 'Uf...').\n"
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

        await ctx.send(respuesta_bot)
    except Exception as e:
        await ctx.send(f"¡Ay no! Algo ha fallado... / Oh no, something went wrong... ({e})")

bot.run(DISCORD_TOKEN)
