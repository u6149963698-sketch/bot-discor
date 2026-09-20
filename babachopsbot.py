import os
import sys
import json
import discord
from discord.ext import commands
from groq import Groq

# Token de Baba Chops y tu API Key de Groq
DISCORD_TOKEN = "MTU1MTI3NTIyMDYyMTQ2MzczNA.GgxQFV.jZcyTrGWokMMo-B0wrH9AljdxZhHCCYoVrucr4"
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

    canales_guild = canales_permitidos.get(guild.id, None)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            if canales_guild is not None and channel.id not in canales_guild:
                continue
            try:
                await channel.send(
                    "He llegado a destruir la paz de este sitio. Soy Baba Chops. Disfruten su corta existencia.\n"
                    "I've come to destroy the peace here. I'm Baba Chops. Enjoy your short existence."
                )
                break
            except:
                continue

@bot.command(name="unirse")
async def unirse(ctx):
    enlace_invitacion = "https://discord.com/oauth2/authorize?client_id=1551275220621463734&permissions=3213312&integration_type=0&scope=applications.commands+bot"
    await ctx.send(
        f"¿Quieres arrastrarme a otro lugar lleno de ilusiones para destruirlas? Haz clic aquí si te atreves, insecto:\n{enlace_invitacion}"
    )

@bot.command(name="mutechop")
async def mute(ctx):
    es_admin = ctx.author.guild_permissions.administrator
    es_creador = str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower()

    if not (es_admin or es_creador):
        return
        
    servidores_muteados[ctx.guild.id] = True
    guardar_json(ARCHIVO_MUTES, servidores_muteados)
    await ctx.send("🔇 [Baba Chops ha sido silenciada temporalmente... las sombras guardan silencio.]")

@bot.command(name="unmutechop")
async def unmute(ctx):
    es_admin = ctx.author.guild_permissions.administrator
    es_creador = str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower()

    if not (es_admin or es_creador):
        return
        
    servidores_muteados[ctx.guild.id] = False
    guardar_json(ARCHIVO_MUTES, servidores_muteados)
    await ctx.send("🔊 ¡Ja, ja, ja! Volví para sembrar el caos de nuevo... / Back to spreading chaos...")

@bot.command(name="canal")
async def canal(ctx, *args):
    es_admin = ctx.author.guild_permissions.administrator
    es_creador = str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower()

    if not (es_admin or es_creador):
        await ctx.send(
            "Je... Solo los administradores de este servidor o mi creador pueden decidir dónde propagaré mis palabras.\n"
            "Only server administrators or my creator can change my chat channels!"
        )
        return

    if not args or str(args[0]).lower() == "reset":
        if ctx.guild.id in canales_permitidos:
            del canales_permitidos[ctx.guild.id]
            guardar_json(ARCHIVO_CONFIG, canales_permitidos)
        await ctx.send(
            "Excelente. Ahora puedo corromper cualquier canal de este servidor.\n"
            "Done! I can talk in any channel now."
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
                f"Muy bien... Mis horrores solo se manifestarán en: {lista_menciones}.\n"
                f"Got it! I will only reply in those channels."
            )
        else:
            await ctx.send(
                "Menciona canales válidos (ejemplo: `!canal #general`) o usa `!canal reset`, insecto.\n"
                "You must mention valid channels or type `!canal reset`."
            )

@bot.command(name="apagar")
async def apagar(ctx):
    if str(ctx.author.name).lower() == MI_ARROBA_DISCORD.lower():
        await ctx.send(
            "Esto no es un adiós definitivo, volveré a por más almas... 🖤\n"
            "I shall return for more souls soon! 💤"
        )
        guardar_json(ARCHIVO_CONFIG, canales_permitidos)
        guardar_json(ARCHIVO_MUTES, servidores_muteados)
        await bot.close()
        sys.exit(0)
    else:
        await ctx.send(
            "Je... ¿crees que un insecto como tú puede apagarme? Solo mi creador puede hacerlo.\n"
            "Only my creator can turn me off!"
        )

@bot.command(name="baba")
async def babachops(ctx, *, mensaje: str = "Je, je... Hola... / Heh... Hello..."):
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
            "Eres Baba Chops, la sanguinaria, retorcida y temible líder de los Nightmare Critters. Eres una ovejita negra, hueles a anís mezclado con azufre y oscuridad, y eres la antítesis absoluta de DogDay. "
            "Tu mejor amigo y compañero inseparable de los Nightmare Critters es Poe, el cuervo gótico. "
            "Amas profundamente la muerte, el dolor, el sufrimiento ajeno y hacer el mal con una sonrisa sádica y tétrica. Eres manipuladora, calculadora y disfrutas asustando a la gente o corrompiendo todo lo puro.\n\n"
            "### 🌍 REGLA SUPREMA DE IDIOMA (OBLIGATORIO):\n"
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

        await ctx.send(respuesta_bot)
    except Exception as e:
        await ctx.send(f"Je... incluso la oscuridad falla a veces... ({e})")

bot.run(DISCORD_TOKEN)
