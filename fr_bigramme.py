# -*- coding: utf-8 -*-

import logging
from pickle import INT, STRING
import re
import numpy as np

lettre=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
lettre2=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',' ']

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphabet_ = alphabet + " "

def simplifie(texte):
    """
        Pour simplifier le décodage, toutes les lettres du texte sont  
        transformées en majuscules sans accent, les autres caractères en  
        espaces, enfin plusieurs espaces consécutifs sont regroupés en un seul.

        Le résultat est une chaine de lettres capitales (ascii 65-90) et 
        d'espaces (ascii 32).

        REFERENCE - liste des caractères unicodes : 
        https://unicode-table.com/fr/#basic-latin

    """

    # Substitution des "e dans l'o", minuscules et majuscules
    #   utilisation de la lib re = regular expression
    texte = re.sub(chr(338),"OE", texte)
    texte = re.sub(chr(339),"OE", texte)

    # Substitution des "e dans l'a", minuscules et majuscules
    #   utilisation de la lib re = regular expression
    texte = re.sub(chr(198),"AE", texte)
    texte = re.sub(chr(230),"AE", texte)

    # Remplacement des accents et convertion des signes de ponctuation en espaces
    to_A = [192,224,226]
    to_C = [199,231]
    to_E = [200,201,202,232,233,234,235]
    to_I = [238,239]
    to_O = [244]
    to_U = [249,251,252]
    # les nombres, la ponctuation et les caractères spéciaux comme les 
    # guillemets d'imprimeur (171,187), ou les trois petits points (8230)
    to_SPACE = list(range(33,65)) + [171,187,8217,8230]

    maj = ""
    for c in texte:
        c2 = c
        # traitement des minuscules a=97 et A=65, a-A=32
        if(ord(c2) in range(97,123)):
            c2 = chr(ord(c2)-32)
        if ord(c2) in to_SPACE:
            c2 = " "
        if ord(c2) in to_A:
            c2 = "A"
        if ord(c2) in to_C:
            c2 = "C"
        if ord(c2) in to_E:
            c2 = "E"
        if ord(c2) in to_I:
            c2 = "I"
        if ord(c2) in to_O:
            c2 = "O"
        if ord(c2) in to_U:
            c2 = "U"  
        maj += c2

    # Plusieurs espaces consécutifs sont regroupés en un seul
    #   utilisation de la lib re = regular expression
    res = re.sub('\s+',' ', maj)
    
    return res


def frequence(texte: STRING):
    """
        Compte le nombre d'occurences de chaque lettre dans un texte
    """

    # A la fin on aura 1 compteur par lettre de l'alphabet
    compteur=[]                 

    # pour chaque lettre de l'alphabet 
    for k in alphabet:
        c=texte.count(k)
        logging.debug("comptage des %s : %d", k, c)
        compteur.append(c)
            
    return compteur  


def frequence_normalisee(compteurs = []):
    """
        Normalise un tableau de compteur en divisant chaque élément par la
        somme de tous les éléments, puis renvoie le résultat sous la forme 
        d'un tableau de pourcentage.
    """
    total = 0
    for cpt in compteurs:
        total+=cpt

    res = []
    for i in range(len(compteurs)):
        res.append ( (compteurs[i]/total)*100 )   
    
    return res


def bigramme(texte):
    """
        Calcule pour chaque bigramme trouvé dans un texte le nombre
        d'occurences divisé par le nombre total de bigrammes de la même 
        famille. Une famille de bigrammes rassemble tous les bigrammes
        commençant par la même lettre. ON obtient ainsi un tableau normalisé
        dont la somme des éléments de chaque ligne vaut 1.
   
    """   
    # matrice 26*27 ou la ligne correspont à la première lettre du bigramme et la colonne la seconde
    bigramme=np.zeros((len(lettre),len(lettre2)))       
    compteur=np.zeros((len(lettre)))
    
    for i in range(len(texte)-1):
        
        for k in range(len(lettre)):                        #pour chaque lettre, on va regarder celle qui suit et ajouter 1 au bigramme correspondant
            if texte[i].upper()==lettre[k]:
                for j in range(len(lettre2)):
                    if texte[i+1].upper()==lettre2[j]:
                        bigramme[k][j]+=1
                        compteur[k]+=1
    
    for h in range(len(lettre)):
        if compteur[h] != 0:
            for f in range(len(lettre2)):
                bigramme[h][f]=bigramme[h][f]/compteur[h]      #on divise par le nombre total de bigrammes rencontrés
            
    return bigramme


def indice(texte):
    """
        Calcul de l'indice de coincidence. Cette indice permet de vérifier que
        le texte décodé est bien (proche) du français.

        En français, l'indice de coïncidence vaut environ 0,0746. 
        En anlgais, cet indice vaut environ 0,0667 (cf exemple dans la fonction main)

        REFERENCE https://fr.wikipedia.org/wiki/Indice_de_co%C3%AFncidence
    """
    sum = 0.0
    total = 0

    for c in alphabet:
        total += texte.count(c)
    den = float(total)*(float(total)-1)

    freq = frequence(texte) 
    for cpt in freq:
        sum = sum + float(cpt)*(float(cpt)-1)

    return (sum/den)


def plausibilite(texte, big_ref = []):
    """
        Caclul de la plausibilité p d'un texte à partir du tableau des bigrammes
        issu de l'analyze des Misérables
    """
    p=0
    big = bigramme(texte)

    # la plausibilite c'est la somme des probabilités de rencontrer un bigramme 
    # multipliée par le nombre de fois qu'on le rencontre
    for i in (0, 25, 1):
        for j in (0, 26, 1):            
            if big_ref[i][j] != 0:
                p += big[i][j] * np.log(big_ref[i][j])     
   
    return (p/len(texte))


# Point d'entrée du programme, utilisation depuis la ligne de commande:
# python3 fr_bigramme.py
if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(name)s:%(levelname)s:%(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.DEBUG)

    logging.info("Lecture des Misérables")
    fichier = open(r'Les-misérables.txt','r')
    livre = fichier.read()
    fichier.close

    logging.info("Simplification des Misérables")
    baba = simplifie(livre)

    freq = frequence(baba)
    logging.debug("Occurences des lettres dans Les Misérables : %s", freq)

    freq_norm = frequence_normalisee(freq)
    logging.debug("Fréquences normalisée dans Les Misérables : %s", freq_norm)

    ic = indice(baba)
    logging.info("Indice de coincidence des Misérables (vaut environ 0.0746 en français) : %f", ic)

    big_ref = bigramme(baba)
    #logging.debug("Initialisation des bigrammes des Misérables : %s", big_ref)

    t1 = "Bonjour: c'est la salutation de base en français et peut être utilisé par tout le monde. C'est un mot à la fois formel et informel"
    baba = simplifie(t1)
    ic1 = indice(baba)
    p1 = plausibilite(baba, big_ref)
    logging.info("[IC1 = %f] [P1 = %f] ==> [%s]", ic1, p1, baba)

    #print(Monte_Carlo('Gf yaom wf htmom tllaot daol lwk wf mtvmt hswl sgfu eak s wmosolamogf r wf mtvmt rt mkgol dgml ft ltdzst hal ygfemogfftk assgfl hswl sgfu hgwk xgok pwljw gw ea xa'))
    
    t3 = 'Thanks so much. This is a simple sentence you can use to thank someone'
    baba = simplifie(t3)
    ic3 = indice(baba)
    p3 = plausibilite(baba, big_ref)
    logging.info("[IC3 = %f] [P3 = %f] ==> [%s]", ic3, p3, baba)
