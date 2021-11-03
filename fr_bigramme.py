import logging
import numpy as np

from collections import Counter

lettre=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
lettre2=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',' ']


def frequence(texte):
    
    compteur=[]                 #On commence par créer un compteur pour chaque lettre
                                
    for i in range(26):
        compteur.append(0)
    
    for i in range(len(texte)):
        for k in range(len(lettre)):
            if texte[i].upper()==lettre[k]:
                compteur[k]+=1

    return np.argsort(compteur)   

def frequence_generale():
    """
        Calcule la fréquence générale de chaque lettre de l'alphabet dans le 
        texte des Misérables de Victor Hugo.

        Pour simplifier le décodage, on considère que toutes les lettres sont
        des majuscules sans accent.
    """

    fichier = open(r'Les-misérables.txt','r')
    livre= fichier.read()

    counter = Counter(livre)
    total = counter.sum(counter.values)

    compteur=[]                 #On commence par créer un compteur pour chaque lettre
    total=0                     #compteur pour le nombre total de lettre
    for i in range(26):
        compteur.append(0)

    for i in range(len(livre)):

        if livre[i].upper() in lettre:                  #upper() permet de convertir les caractères en majuscule
            for k in range(len(lettre)):
                if livre[i].upper()==lettre[k]:         #On ajoute 1 au compteur à chaque fois que l'on croise la lettre correspondante
                    compteur[k]+=1
                    total+=1

    
    for i in range(len(compteur)):
        compteur[i]=int(((compteur[i]/total)*100)*10**3)/10**3   #Renvoie le résultat en pourcentage à 4 chiffres significatifs
    
    fichier.close()
    return counter

def bigramme_general():
    """
        Calcule pour chaque bigramme trouvé dans Les Misérables le nombre
        d'occurences divisé par le nombre total de bigrammes de la même 
        famille. Une famille de bigrammes rassemble tous les bigrammes
        commençant par la même lettre. ON obtient ainsi un tableau normalisé
        dont la somme des éléments de chaque ligne vaut 1.

        Par la suite ce tableau servira comme une mesure absolue de la 
        chance d'apparation d'un bigramme dans un texte de langue française.

        Pour simplifier le décodage, on considère que toutes les lettres sont
        des majuscules sans accent. Une lettre peut être suivie d'une autre
        lettre ou d'un espace
        
    """   
    # matrice 26*27 ou la ligne correspont à la première lettre du bigramme et la colonne la seconde
    bigramme=np.zeros((len(lettre),len(lettre2)))       
    compteur=np.zeros((len(lettre)))
    
    fichier = open(r'Les-misérables.txt','r')
    livre= fichier.read()
    
    for i in range(len(livre)-1):
        
        for k in range(len(lettre)):                        #pour chaque lettre, on va regarder celle qui suit et ajouter 1 au bigramme correspondant
            if livre[i].upper()==lettre[k]:
                for j in range(len(lettre2)):
                    if livre[i+1].upper()==lettre2[j]:
                        bigramme[k][j]+=1
                        compteur[k]+=1
    
    for h in range(len(lettre)):
        for f in range(len(lettre2)):
            bigramme[h][f]=bigramme[h][f]/compteur[h]      #on divise par le nombre total de bigrammes rencontrés
            
            
    fichier.close()
    return bigramme

def indice():
    indice=0
    compteur=[]                 #On commence par créer un compteur pour chaque lettre
    total=0                     #compteur pour le nombre total de lettre
    for i in range(26):
        compteur.append(0)

    fichier = open(r'Les-misérables.txt','r')
    livre= fichier.read()   
    
    for i in range(len(livre)):

        if livre[i].upper() in lettre:                  #on ajoute 1 au compteur à chaque fois que l'on croise la lettre correspondante
            for k in range(len(lettre)):
                if livre[i].upper()==lettre[k]:
                    compteur[k]+=1
                    total+=1
       
    for i in range(len(compteur)):
        indice=indice+ (compteur[i]*(compteur[i]-1))/(total*(total-1))  #formule de l'indice de coïcindence
        
    fichier.close()
    return indice
    
if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(name)s:%(levelname)s:%(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Initialisation fréquence des lettres: %s", frequence_generale())
    logging.debug("Initialisation des bigrammes: %s", bigramme_general())
    logging.debug("Initialisation indice de conincidence: %s", indice())
