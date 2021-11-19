# -*- coding: utf-8 -*-

import re
import os
import numpy as np
import random as rd
import codecs
import pickle
import matplotlib.pyplot as plt

alphabet    = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphabet_   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
fr_bigrams  = np.zeros((27, 27))
fr_dico     : list

def charge_dico():
    """
        La première fois que cette fonction est appelée, elle transforme la 
        liste des mots français en leurs versions simplifiés (lettres 
        capitales, pas d'accents, etc.). Elle sauvegarde ensuite le résultat
        dans un fichier fr_dico.dat. Les fois suivantes elle se contente de
        lire le fichier .dat

        Utilise la lib pickle qui peut sauvegarder des structures python 
        directement, sans utiliser leur forme sérialisée (aka une string).
        Permet ensuite de relire ces structures très rapidement.
        -- 
        retourne    : liste des mots simplifiés
    """

    fr_txt    = "fr_dico.txt"   # fichier de références des mots français
    fr_dat    = "fr_dico.dat"   # fichier des mots français simplifiés
    fr_dict   = ""              # mots issus du fichier de référence
    global fr_dico              # liste de mots simplifiés du françcais

    if os.path.isfile(fr_dat) :
        with open(fr_dat, 'rb') as fichier:
            fr_dico = pickle.load(fichier)   
    else :
        with codecs.open(fr_txt, "r", "utf-8") as lignes:
            for ligne in  lignes:
                fr_dict += ligne[:-1] + " "
                
        fr_dico = simplifie(fr_dict)
        # Ajout des lettres et de qu'
        fr_dico = ['QU'] + ['A'] + ['C'] + ['J'] + ['L'] + ['M'] + ['N'] + ['O'] + ['S'] + ['T'] + ['Y'] +fr_dico.split(" ")
        pickle.dump(fr_dico, open( fr_dat, "wb" ))

    cpt_mots = len(fr_dico)
    print("Chargement dictionnaire FR terminé ({} mots)".format(cpt_mots))
    return fr_dico


def char_to_id(c):
    """
        Retourne la position de 0 à 25 d'une lettre dans l'alphabet, 26 pour l'espace
        Rem: char(65)='A' et ord('A')=65
    """
    return 26 if c==" " else ord(c) - 65


def id_to_char(i):
    """
        Retourne la lettre numéro i+1 de l'alphabet 
    """
    return " " if i==26 else chr(i+65)


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
    global alphabet_

    # Substitution des "e dans l'o", minuscules et majuscules
    #   utilisation de la lib re = regular expression
    texte = re.sub(chr(338),"OE", texte)
    texte = re.sub(chr(339),"OE", texte)

    # Substitution des "e dans l'a", minuscules et majuscules
    #   utilisation de la lib re = regular expression
    texte = re.sub(chr(198),"AE", texte)
    texte = re.sub(chr(230),"AE", texte)

    # Remplacement des accents et convertion des signes de ponctuation en espaces
    to_A = [192,195,224,226]
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
        # il peut rester des caractères bizarres, on les élimine ici
        if c2 in alphabet_: 
            maj += c2

    # Plusieurs espaces consécutifs sont regroupés en un seul
    #   utilisation de la lib re = regular expression
    res = re.sub('\s+',' ', maj)
    
    print("Simplification du texte terminée: {} caractères".format(len(res)))
    return res


def frequence(texte):
    """
        Compte le nombre d'occurences de chaque lettre dans un texte simplifié
        puis retourne un tableau de pourcentages sous la forme d'un dict trié
        par valeur de la plus petite (W en français) à la plus grande (E)
    """
    global alphabet

    # 1 compteur par lettre de l'alphabet
    freq={x: 0 for x in alphabet}

    # total = nombre de lettres dans le texte, non compris les espaces             
    total=0
    
    # pour chaque lettre de l'alphabet 
    for k in alphabet:
        freq[k]=texte.count(k)
        total+=freq[k]

    for k in alphabet:
        freq[k]=freq[k]/total

    # trie le dict par valeurs
    # REFERENCE: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    sorted_by_values = dict(sorted(freq.items(), key=lambda item:item[1]))
    return sorted_by_values  


def bigramme(texte):
    """
        Calcule pour chaque bigramme trouvé dans un texte le nombre
        d'occurences divisé par le nombre total de bigrammes de la même 
        famille. Une famille de bigrammes rassemble tous les bigrammes
        commençant par la même lettre. On obtient ainsi un tableau normalisé
        dont la somme des éléments de chaque ligne vaut 1.

        texte       : texte dont on extrait les bigrammes
        --
        retourne    : probabilité des bigrammes du texte (tableau 2D)
    """   

    #permet d'éviter de prendre log(0) mais reste assez petit pour ne pas influencer le résultat
    epsilon = 10e-7

    # matrice ou la ligne correspond à la première lettre du bigramme et la colonne à la seconde
    big=np.zeros((27, 27))       
    cpt=np.zeros((27))
    
    # parcourt texte en lisant un caractère (current) et le suivant (next_)
    # on découpe ainsi le texte en bigrammes
    # pour chaque bigramme rencontré on incrémente le compteur associé dans le tableau big
    # et le compteur de la famille
    s=list(texte)
    current = s[0]
    for next_ in s[1:] :
        i = char_to_id(current)
        j = char_to_id(next_)
        big[i][j]+=1
        cpt[i]+=1
        current = next_

    # la matrice est normalisée ligne à ligne et mise à l'échelle logarithmique
    for i in range(27):
        if cpt[i] != 0:
            for j in range(27):
                big[i][j] = np.log( (big[i][j] / cpt[i]) + epsilon )    
        else:
            for j in range(27):
                big[i][j] = np.log( epsilon )                 
    return big


def indice(texte):
    """
        Calcul de l'indice de coincidence. Cette indice permet de vérifier que
        le texte décodé est bien (proche) du français.

        En français, l'indice de coïncidence vaut environ 0,0746. 
        En anlgais, cet indice vaut environ 0,0667 (cf exemple dans la fonction main)

        REFERENCE https://fr.wikipedia.org/wiki/Indice_de_co%C3%AFncidence
    """
    global alphabet
    sum = 0.0
    total = 0

    for c in alphabet:
        total += texte.count(c)
    den = float(total)*(float(total)-1)

    freq = frequence(texte)
    for f in list(freq.values()):
        # ici on retrouve le nb d'occurences de chaque lettre en multipliant 
        # le frequence par le nombre total de caractères dans la chaine
        occ=f*total
        sum = sum + occ*(occ - 1) 

    res = sum/den

    print("Indice de coincidence du texte (vaut environ 0.0746 en français): {:10.6f}".format(res))
    return res


def plausibilite(texte):
    """
        Caclul de la plausibilité p d'un texte à partir du tableau des bigrammes
        issu de l'analyze des Misérables.

        La plausibilite c'est la somme des probabilités de rencontrer un bigramme 
        multipliée par le nombre de fois qu'on le rencontre.

        Dans l'algorithme de MH, plausibilite = f, fonction proportionnelle à pi
    """
    global fr_bigrams

    # repérage des bigrammes dans le texte, à chaque occurence on ajoute le log
    # de la probabilité (+ epsilon pour traiter les cas nuls)
    big=np.zeros((27, 27))
    s=list(texte)
    current = s[0]
    for next_ in s[1:] :
        i = char_to_id(current)
        j = char_to_id(next_)
        big[i][j]+=fr_bigrams[i][j]
        current = next_

    plau=np.sum(big)/len(texte)

    return plau

def score(texte):
    """
        Evalue le score de la proposition de déchiffrement en repérant les mots
        réels issus de la liste des mots français.

        Le score est le rapport entre le nombre de lettres de vrais mots sur le 
        nombre de lettres total du texte (sans les espaces)
    """
    global fr_dico
    lettres_ok  = 0
    lettres_tot = 0
    mots = texte.split(" ")
    for mot in mots:
        if mot in fr_dico:
            lettres_ok += len(mot)
        lettres_tot += len(mot)
    return lettres_ok/lettres_tot    


def dechiffre(texte, code):
    """
        Prend un texte chiffré en argument et renvoie une proposition de 
        dechiffrement basée sur la fréquence des caractères.

        texte       : texte à déchiffrer
        code        : clé de déchiffrement = permutations à appliquer 
        --
        retourne    : texte déchiffré (string)
    """

    freq = frequence(texte)
    fk   = list(freq.keys())
    # copie du texte sous forme de tableau
    res = list(texte)
    # chaque lettre du texte est remplacée par son équivalente dans le 
    # tableau des fréquences de référence.
    # i est l'indice global de res
    i=0  
    for c in res:
        if c != ' ' :
            # indice du caractère dans le tableau ordonné par fréqeunce
            indice = fk.index(c)
            # sub = caractère du même indice dans la clef
            sub = code[indice]
            res[i]=sub
        i+=1
    return ''.join(res)


def chiffre(texte):
    """
        Chiffrement d'un texte avec un code tiré au hasard
    """
    global alphabet

    code = rd.sample(alphabet, 26)
    simple = simplifie(texte)
    return code, dechiffre(simple, code)


def echange(clef):
    """
        échange 2 lettres de la clef

        Dans l'algorithme de MH, echange est la fonction de tirage aléatoire
        qui ne dépend que de l'état précédent.
        --
        retourne    : nouvelle clef
    """
    liste=list(clef)

    i = np.random.randint(0,26)
    j = np.random.randint(0,26)
    while i == j:
        j = np.random.randint(0,26)

    liste[i], liste[j] = liste[j], liste[i]
    return ''.join(liste)


def acceptation(cur, new):
    """
        Calcule le taux d'acceptation alpha et le compare à une variable aléatoire x dans [O;1[:
            Si x <= alpha, alors retourne True accepter (donc si alpha > 1}, on accepte nécessairement)
            Si x > alpha, alors retourne False
        --
        
    """
    x = rd.random()
    if x <= np.exp(new - cur) :
        return True
    return False

def metropolis(max_iter, texte_init, code_init):
    """
        Application de l'algorithme de Metropolis-Hastings.

        L'algorithme peut être interprété intuitivement de la manière suivante: à chaque itération, 
        on tente de se déplacer dans l'espace des états possibles (codes), le déplacement peut être 
        accepté ou rejeté. Le taux d'acceptation alpha indique à quel point le nouvel état est probable 
        (plausibilité) étant donné l'état actuel, et selon la distribution pi (les bigrammes). 
        Si l'on cherche à se déplacer vers un état plus probable que l'état actuel, le déplacement est 
        toujours accepté. Cependant, si l'on cherche à se déplacer vers un état moins probable que l'état 
        actuel, alors le déplacement peut être rejeté et le rejet est d'autant plus probable que la chute 
        de densité de probabilité est élevée. Par conséquent, la marche tend à visiter préférentiellement 
        les régions de l'espace des états où la densité pi est élevée mais visite occasionnellement des 
        régions de moindre densité.

        REFERENCE : https://fr.wikipedia.org/wiki/Algorithme_de_Metropolis-Hastings
        --
        retourne    : proposition de déchiffrement
    """
    break_plau = -1.7          # max plausibilité calculée à partir de laquelle on estime le résultat juste
    score_mots = 0             # score calculé du message décodé (c.f. fonction score)

    cur_code  = code_init
    cur_texte = dechiffre(texte_init, cur_code)
    # score_mots = score(cur_texte)
    # cur_plau = 4*score_mots + plausibilite(cur_texte)
    cur_plau = plausibilite(cur_texte)

    best_text  = cur_texte
    best_plau  = cur_plau                
    best_code  = code_init

    cpt=0
    while cpt < max_iter :
        cpt+=1 
        # sortie prématurée de la boucle en cas de résultat satisfaisant
        if best_plau > break_plau:
            break

        # échange de 2 lettres de la clef       
        new_code  = echange(cur_code)
        new_texte = dechiffre(cur_texte, new_code)
        # score_mots = score(new_texte)
        # new_plau  = 4*score_mots + plausibilite(new_texte)
        new_plau  = plausibilite(new_texte)

        if new_plau > cur_plau:
            cur_texte = new_texte
            cur_plau  = new_plau                
            cur_code  = new_code   
            if new_plau > best_plau:
                print("(itération {}) Meilleure plausibilité {:10.6f}".format(cpt, new_plau))
                best_text  = new_texte
                best_plau  = new_plau                
                best_code  = new_code     
        else:
            # fonction d'acceptation de Metropolis-Hastings
            x = rd.random()
            if x <=  (cur_plau / new_plau) * 0.001 : 
            #if x <= np.exp(new_plau - cur_plau) :
                print("(itération {}) Dégradation plausibilité de {:10.6f} vers {:10.6f}".format(cpt, cur_plau, new_plau))
                cur_texte = new_texte
                cur_plau  = new_plau                
                cur_code  = new_code 

    return best_code, best_plau, best_text


# Point d'entrée du programme, utilisation depuis la ligne de commande:
# python3 fr_bigramme.py

"""
    Chargement des mots de la langue française
"""
fr_dico     = charge_dico()

"""
    Le texte des Misérables est analysé pour en extraire:
        - les fréquences de référence du français
        - l'indice de coincidence
        - le tableau des fréquences des bigrammes en français
"""
print ("Analyse des Misérables")
fichier = open(r'Les-misérables.txt','r')
#fichier = open(r'swann.txt','r')
livre = fichier.read()
fichier.close
baba = simplifie(livre)
with open('baba.txt', 'w') as f:
    f.write(baba)
# chargement des fréquenes des lettres de référence
fkv_ref = frequence(baba)
fk_ref  = list(fkv_ref.keys())

# Calcul des bigrammes de référence
fr_bigrams = bigramme(baba)
ic_ref = indice(baba)
# p = plausibilite(baba)
# print ("Plausibilité des Misérables {:10.6f}".format(p))

# Génération du graphe de densité de probabilités
x_labels=list(alphabet_)
x_labels[26]='_'
y_labels=list(alphabet_)
y_labels[26]='_'
fig, ax = plt.subplots()
ax.pcolormesh((fr_bigrams))
ax.axis('tight')
plt.xticks(range(len(x_labels)), x_labels)
plt.yticks(range(len(y_labels)), y_labels)
plt.savefig('fr_bigrams.png')

"""
    Analyse d'une expression française pour vérifier la validité des fonctions d'analyse
"""
# expr_fr = "Bonjour: c'est la salutation de base en français et peut être utilisé par tout le monde. C'est un mot à la fois formel et informel"
# print("Analyse de {}".format(expr_fr))
# baba = simplifie(expr_fr)
# ic = indice(baba)
# p = plausibilite(baba)
# print("Plausibilité de expr_fr {:10.6f}".format(p))

"""
    Analyse d'une expression anglaise pour vérifier la non validité des fonctions d'analyse dans ce cas
"""
# expr_en = "Thanks so much. This is a simple sentence you can use to thank someone"
# print("Analyse de {}".format(expr_en))
# baba = simplifie(expr_en)
# ic = indice(baba)
# p = plausibilite(baba)
# print("Plausibilité de expr_en {:10.6f}".format(p))

"""
    Déchiffrement d'un texte codé par substitution.
"""

# Texte initial
emile = """La nature veut que les enfants soient enfants avant que d’être hommes. Si nous voulons 
            pervertir cet ordre, nous produirons des fruits précoces, qui n’auront ni maturité ni saveur, 
            et ne tarderont pas à se corrompre ; nous aurons de jeunes docteurs et de vieux enfants. 
            L’enfance a des manières de voir, de penser, de sentir, qui lui sont propres ; rien n’est moins 
            sensé que d’y vouloir substituer les nôtres ; et j’aimerais autant exiger qu’enfant eût cinq 
            pieds de haut, que du jugement à dix ans. En effet, à quoi lui servirait la raison à cet âge ? 
            Elle est le frein de la force, et l’enfant n’a pas besoin de ce frein."""

# Le texte est chiffré à l'aide d'une clef de chiffrement tirée au hasard
clef, enigme = chiffre(emile)

# Le texte codé est déchiffré à l'aide d'un algorithme de Metropolis-Hastings
code, p, solution = metropolis(10000, enigme, fk_ref)

# Présentation des résultats
print ("# ---------------------------------")
print ("# Texte chiffré                   : {}".format(enigme))
print ("# Clef de chiffrement initiale    : {}".format(clef))
print ("# Code intial (fréquence français): {}".format(fk_ref))
print ("# Meilleur code de dechiffrement  : {}".format(list(code)))
print ("# Plausibilité de la solution     : {:10.6f}".format(p))
print ("# Proposition finale              : {}".format(solution))
print ("# ---------------------------------")

