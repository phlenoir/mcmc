# -*- coding: utf-8 -*-

import logging
import re
import numpy as np

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphabet_ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

def char_to_id(c):
    """
        Retourne la position d'une lettre dans l'alphabet, 26 pour l'espace
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


def frequence(texte):
    """
        Compte le nombre d'occurences de chaque lettre dans un texte simplifié
    """

    # 1 compteur par lettre de l'alphabet + l'espace, qu'ici on ne compte pas
    cpt=np.zeros(27)              

    # pour chaque lettre de l'alphabet 
    for k in alphabet:
        cpt[char_to_id(k)]=texte.count(k)
        logging.debug("comptage des %s : %d", k, cpt[char_to_id(k)])
            
    return cpt  


def frequence_normalisee(compteurs = []):
    """
        Normalise un tableau de compteurs en divisant chaque élément par la
        somme de tous les éléments, puis renvoie le résultat sous la forme 
        d'un tableau de pourcentage.
    """
    total = np.sum(compteurs)
    cpt = np.zeros(27)

    # 0 c'est A, 1 c'est B, etc.
    for i, item in enumerate(compteurs):
        cpt[i] = (item/total)*100
        logging.debug("pct pour %s : %f", id_to_char(i), cpt[i])    

    return cpt


def bigramme(texte):
    """
        Calcule pour chaque bigramme trouvé dans un texte le nombre
        d'occurences divisé par le nombre total de bigrammes de la même 
        famille. Une famille de bigrammes rassemble tous les bigrammes
        commençant par la même lettre. ON obtient ainsi un tableau normalisé
        dont la somme des éléments de chaque ligne vaut 1.
    """   

    # matrice 26*27 ou la ligne correspont à la première lettre du bigramme et la colonne la seconde
    big=np.zeros((26, 27))       
    cpt=np.zeros((26))
    
    # parcourt du text en lisant un caractère (current) et le suivant (next_)
    # on découpe ainsi le texte en bigrammes
    # pour cahque bigramme rencontré on incrémente le compteur associé dans le tableau big
    # et le compteur de la famille
    for (index, thing) in enumerate(texte):
        if index < len(texte):
            current, next_ = thing, texte[index + 1]
            # un bigramme ne commence pas par un espace
            if current != " ":
                i = char_to_id(current)
                j = char_to_id(next_)
                big[i][j]+=1
                cpt[i]+=1

    for i, c in enumerate(cpt):
        if c != 0:
            for j, a in enumerate(alphabet_):
                big[i][j] = big[i][j] / c    
            
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
    for index, x in np.ndenumerate(big_ref):
        if x != 0:
            logging.debug("Indice %s, value 1 %f, value 2 %f ", index, x, np.take(big, index))
            p += np.take(big, index) * np.log( x )

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
    logging.debug("Initialisation des bigrammes des Misérables : %s", big_ref)
    p0 = plausibilite(baba, big_ref)
    logging.info("Vérification de la plausibilité des Misérables : %f", p0)

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
