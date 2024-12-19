import asyncio
import aioconsole
import sys
from ascii_magic import AsciiArt
import getpass
import os

def CalculTailleOctet(Nb):
    bit = 0
    while True:
        bit+=1
        if Nb < 2**bit :
            if(bit%8==0):
                return int(bit/8)
            else: 
                return int((bit/8)+1)


async def Listen(reader):
    global EXIT
    while not EXIT:
        data = await reader.read(1024)
        if not data :
            print("\nConnexion au serveur coupé")
            EXIT = True
        if not data : continue
        msg = data.decode()
        print(msg)

def Command(input):
    command = input[1:].split(" ")[0]
    match command :
        case "di":
            try:
                ImagePath = input[1:].split(" ")[1]
            except:
                print("Pas d'image donné")
                return None,None
            try:
                my_art = AsciiArt.from_image(ImagePath)
                return "Image",my_art
            except:
                print("Mauvais chemin")
                return None,None
        case "room":
            try:
                NbRoom = input[1:].split(" ")[1]
            except:
                print("Pas de numéro de room donné")
                return None,None
            try:
                NbRoom = int(NbRoom)
            except:
                print("La room donné n'est pas un nombre !")
                return None,None
            if(NbRoom > 999999):
                print("Numéro de room trop grand")
                return None,None
            return "room",NbRoom
        case _:
            print("Commande inconnu")
            return None,None

async def get_hidden_input(prompt=""):
    # Utilise getpass pour cacher l'input
    hidden_input = getpass.getpass(prompt)
    return hidden_input

async def SendInput(writer):
    global EXIT
    while not EXIT:
        input = await aioconsole.ainput()
        sys.stdout.write("\033[F")  #   Ces 2 lignes sont la pour cacher l'input de l'utilisateur
        sys.stdout.write("\033[K")  #   Et voir son message au bon format + couleur
        try:
            if(input[0] == "/"):
                type,result = Command(input)
                if type == None : continue
                if(type=="Image"):
                    image = result.to_terminal()
                    await SendMessage(image,writer)
                elif(type=="room"):
                    LenNb = CalculTailleOctet(result)
                    writer.write((3).to_bytes())
                    writer.write((LenNb).to_bytes(2))
                    writer.write(result.to_bytes(LenNb))
                    await writer.drain()
                    print("--------------------------------\n")
                    print(f"          Room n°{result}")
                    print("\n--------------------------------")
                continue
        except:
            continue
        await SendMessage(input,writer)

async def SendMessage(message,writer):
    LenMess = len(message) # on calcule la taille du message
    Header2 = CalculTailleOctet(LenMess) # on calcule la taille en octet de cette taille
    if Header2 == 1: # si la taille en octet de la taille du message est superieur a 1 octet (trop compliqué a comprendre comme phrase)
        writer.write(Header2.to_bytes())
        writer.write(LenMess.to_bytes())
        writer.write(message.encode())
        await writer.drain()
    else :
        deux = 2
        writer.write(deux.to_bytes())
        writer.write(Header2.to_bytes())
        writer.write(LenMess.to_bytes(Header2))
        writer.write(message.encode())
        await writer.drain()


async def main():
    print("-------------------------------------------\n")
    print("               Commandes :")
    print("          Pour afficher une image")
    print("        /di [chemin_de_votre_image]")
    print("          Pour changer de room")
    print("        /room [numero de la room]")
    print("\n-------------------------------------------\n")
    pseudo = input("Choisir votre pseudo :\n\n-------------------------------------------\n")
    
    if(len(pseudo)>15):
        print("pseudo trop long")
        return
    try:
        reader, writer = await asyncio.open_connection(host="127.0.0.1", port=7777)
    except:
        print("Connexion avec le serveur impossible")
        return
    writer.write(len(pseudo).to_bytes())
    writer.write(pseudo.encode())
    await writer.drain()
    tasks = [ Listen(reader), SendInput(writer) ]
    try:
        os.system('clear' if os.name != 'nt' else 'cls')
    except:
        sys.stdout.write("\033[2J")  #   On remonte le terminal pour plus de visibilité si le clear ne marche pas
        sys.stdout.write("\033[H") 
    await asyncio.gather(*tasks)
global EXIT
EXIT = False

if __name__ == "__main__" :
    asyncio.run(main())