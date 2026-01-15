import sys
from ticket_generator import produce_tickets

def main():
    if len(sys.argv) < 2:                          # Vérifie la présence d'un argument de ligne de commande
        print("Usage : python main.py ticket_generator")
        sys.exit(1)                                # Quitte si aucun argument n'est fourni    

    command = sys.argv[1]                          # Récupère la commande de la ligne de commande 

    if command == "ticket_generator":                      # Si la commande est "ticket_generator"   
        produce_tickets()                          # Appelle la fonction pour démarrer le producteur de tickets
    else:
        print(f"Commande inconnue : {command}")

if __name__ == "__main__":
    main()
