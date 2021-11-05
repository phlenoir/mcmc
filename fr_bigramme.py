# -*- coding: utf-8 -*-

import logging
import re
from typing import Iterable
import numpy as np
import random as rd

alphabet  = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphabet_ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

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
    
    logging.info("Simplification du texte terminée: %d caractères", len(res))
    return res


def frequence(texte):
    """
        Compte le nombre d'occurences de chaque lettre dans un texte simplifié
        puis retourne un tableau de pourcentages sous la forme d'un dict trié
        par valeur de la plus petite (W) à la plus grande (E)
    """

    # 1 compteur par lettre de l'alphabet
    freq={x: 0 for x in alphabet}

    # total = nombre de lettres dans le texte, non compris les espaces             
    total=0
    
    # pour chaque lettre de l'alphabet 
    for k in alphabet:
        freq[k]=texte.count(k)
        total+=freq[k]
        logging.debug("comptage des %s : %d", k, freq[k])

    for k in alphabet:
        freq[k]=freq[k]/total

    # trie le dict par valeurs
    # REFERENCE: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    sorted_by_values = dict(sorted(freq.items(), key=lambda item:item[1]))

    logging.debug("Occurences des lettres dans le texte analysé : %s", sorted_by_values)
    return sorted_by_values  

def bigramme(texte):
    """
        Calcule pour chaque bigramme trouvé dans un texte le nombre
        d'occurences divisé par le nombre total de bigrammes de la même 
        famille. Une famille de bigrammes rassemble tous les bigrammes
        commençant par la même lettre. ON obtient ainsi un tableau normalisé
        dont la somme des éléments de chaque ligne vaut 1.
    """   

    # matrice 26*27 ou la ligne correspond à la première lettre du bigramme et la colonne à la seconde
    big=np.zeros((26, 27))       
    cpt=np.zeros((26))
    
    # parcourt du text en lisant un caractère (current) et le suivant (next_)
    # on découpe ainsi le texte en bigrammes
    # pour cahque bigramme rencontré on incrémente le compteur associé dans le tableau big
    # et le compteur de la famille
    s=list(texte)
    current = s[0]
    for next_ in s[1:] :
        if current != ' ' :
            i = char_to_id(current)
            j = char_to_id(next_)
            big[i][j]+=1
            cpt[i]+=1
        current = next_

    for i in range(26):
        if cpt[i] != 0:
            for j in range(27):
                big[i][j] = big[i][j] / cpt[i]    

    logging.debug("Initialisation des bigrammes terminées : %s", big)   
    return big


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
    for f in list(freq.values()):
        # ici on retrouve le nb d'occurences de chaque lettre en multipliant 
        # le frequence par le nombre total de caractères dans la chaine
        occ=f*total
        sum = sum + occ*(occ - 1) 

    res = sum/den

    logging.info("Indice de coincidence du texte (vaut environ 0.0746 en français) : %f", res)
    return res


def plausibilite(texte, big_ref = []):
    """
        Caclul de la plausibilité p d'un texte à partir du tableau des bigrammes
        issu de l'analyze des Misérables.

        La plausibilite c'est la somme des probabilités de rencontrer un bigramme 
        multipliée par le nombre de fois qu'on le rencontre.
    """
    epsilon = 10e-6

    # repérage des bigrammes dans le texte, à chaque occurence on ajoute le log
    # de la propabilité (+ epsilon pour traiter les nuls)
    big=np.zeros((26, 27))
    s=list(texte)
    current = s[0]
    for next_ in s[1:] :
        if current != ' ' :
            i = char_to_id(current)
            j = char_to_id(next_)
            big[i][j]+=np.log(big_ref[i,j] + epsilon)
        current = next_

    plau=np.sum(big)/len(texte)

    logging.debug("Plausibilité du texte : %f", plau)
    return plau


def proposition(texte, code_ref: list):
    """
        Prend un texte chiffré en argument et renvoie une proposition de 
        dechiffrement basée sur la fréquence des caractères
    """
    
    # dict des lettres triées par occurence croissante
    freq = frequence(texte)
    code = list(freq.keys())

    # copie du texte sur lequel on travaille
    res = list(texte)

    # chaque lettre du texte est remplacée par son équivalente dans le 
    # tableau des fréquences de référence issues de Victor Hugo.

    # i est l'indice global de res
    i=0  
    for c in res:
        if c != ' ' :
            # indice du caractère dans le tableau des fréqeunces
            indice = code.index(c)
            # sub = caractère du même indice dans les fréquences de référence
            sub = code_ref[indice]
            res[i]=sub
        i+=1

    return ''.join(res)


def echange(texte, i , j):
    """
        échange 2 éléments d'indice i et j dans une chaine
    """
    liste=list(texte)
    liste[i], liste[j] = liste[j], liste[i]

    return ''.join(liste)


def Monte_Carlo(max_iter, plau_init, code_init, big_ref, texte_init):

    break_plau = -1.7

    cur_code  = code_init
    cur_texte = str(texte_init)
    cur_plau  = plau_init

    best_code = code_init
    best_text = str(texte_init)
    best_plau = plau_init
    
    # TODO utiliser la distance à l'indice de plausibilité de référence plutôt qu'un nombre d'itérations fixe
    cpt=0
    while cpt < max_iter :

        # échange de 2 éléments au hasard
        i = np.random.randint(0,26)
        j = np.random.randint(0,26)       
        new_code  = echange(cur_code, i, j)
        new_texte = proposition(cur_texte, new_code)
        new_plau  = plausibilite(new_texte, big_ref)
        
        x = np.random.rand()
        # si la plausibilité est meilleure on garde le nouveau texte,
        # sinon soit on garde le nouveau texte, soit on revient au texte précédent.
        # Dépend du résultat d'un aléa:
        # TODO expliquer l'aléa
        if new_plau > cur_plau:
            cur_plau  = new_plau
            cur_texte = new_texte
            cur_code  = new_code
            if new_plau > best_plau:
                best_text = new_texte
                best_plau = new_plau                
                best_code = new_code
        else:
            if ( (cur_plau / new_plau) * 0.010) > x :
                logging.info("(itération %d)saut de %f vers %f", cpt, cur_plau, new_plau)
                cur_texte = new_texte
                cur_plau  = new_plau
                cur_code  = new_code

        if best_plau > break_plau:
            break
        cpt+=1      
        logging.debug("Proposition %d(%f) [%s]", cpt, cur_plau, cur_texte)

    logging.info("Proposition finale(%f) [%s]", best_plau, best_text)
    return best_code



# Point d'entrée du programme, utilisation depuis la ligne de commande:
# python3 fr_bigramme.py
if __name__ == '__main__':
    FORMAT = '%(asctime)-15s:%(levelname)s:%(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.INFO)

    """
        Le texte des Misérables est analysé pour en extraire:
            - les fréquences de référence du français
            - l'indice de coincidence
            - le tableau des probabilités d'occurences des bigrammes en français
    """
    logging.info("Analyse des Misérables")
    fichier = open(r'Les-misérables.txt','r')
    livre = fichier.read()
    fichier.close
    baba = simplifie(livre)
    freq_ref = frequence(baba)
    ic_ref = indice(baba)
    big_ref = bigramme(baba)
    p = plausibilite(baba, big_ref)
    
    """
        Analyse d'une expression française pour vérifier la validité des fonctions d'analyse
    """
    expr_fr = "Bonjour: c'est la salutation de base en français et peut être utilisé par tout le monde. C'est un mot à la fois formel et informel"
    logging.info("Analyse de [%s]", expr_fr)
    baba = simplifie(expr_fr)
    ic = indice(baba)
    p = plausibilite(baba, big_ref)

    """
        Analyse d'une expression anglaise pour vérifier la non validité des fonctions d'analyse dans ce cas
    """
    expr_en = "Thanks so much. This is a simple sentence you can use to thank someone"
    logging.info("Analyse de [%s]", expr_en)
    baba = simplifie(expr_en)
    ic = indice(baba)
    p = plausibilite(baba, big_ref)

    """
        Déchiffrement d'un texte codé par substitution.

        Une première proposition est éléborée à partir du pct d'occurence des
        lettres dans le texte chiffré qui sont comparées au pct de ref. Une 
        première substitution est appliquée.

        Cette proposition initiale est ensuite utilisée comme base de l'algorithme
        de Monte-Carlo que l'on va itérer un certain nombre de fois.
    """
    enigme='Gf yaom wf htmom tllao daol lwk wf mtvmt hswl sgfu eak s wmosolamogf r wf mtvmt rt mkgol dgml ft ltdzst hal ygfemogfftk assgfl hswl sgfu hgwk xgok pwljw gw ea xa'
    logging.info("Déchiffrement de [%s]", enigme)
    baba = simplifie(enigme)
    prop = proposition(baba, list(freq_ref.keys()))
    p = plausibilite(prop, big_ref)
    logging.info("Proposition initiale [%s]", prop)

    Monte_Carlo(200000, p, list(freq_ref.keys()), big_ref, prop)

    # enigme="On fait un petit essai mais sur un texte plus long car l'utilisation d un texte de trois mots ne semble pas fonctionner. Allons plus loin pour voir jusqu'où ça va"
    # logging.info("Déchiffrement de [%s]", enigme)
    # baba = simplifie(enigme)
    # p = plausibilite(baba, big_ref)
    # logging.info("P = %f [%s]", p, baba)