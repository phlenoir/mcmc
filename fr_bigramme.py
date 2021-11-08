# -*- coding: utf-8 -*-

import logging
import re
import os
import numpy as np
import codecs
import pickle


alphabet    = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphabet_   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
fr_dico     : list
big_ref     : list([])


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
        fr_dico = ['QU'] + ['A'] + ['C'] + ['L'] + ['M'] + ['N'] + ['O'] + ['S'] + ['T'] + ['Y'] +fr_dico.split(" ")
        pickle.dump(fr_dico, open( fr_dat, "wb" ))

    cpt_mots = len(fr_dico)
    logging.info("Chargement dictionnaire FR terminé (%d mots)", cpt_mots)
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
        par valeur de la plus petite (W en français) à la plus grande (E)
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
        commençant par la même lettre. On obtient ainsi un tableau normalisé
        dont la somme des éléments de chaque ligne vaut 1.

        texte       : texte dont on extrait les bigrammes
        --
        retourne    : fréquences des bigrammes du texte (tableau 2D)
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


def plausibilite(texte):
    """
        Caclul de la plausibilité p d'un texte à partir du tableau des bigrammes
        issu de l'analyze des Misérables.

        La plausibilite c'est la somme des probabilités de rencontrer un bigramme 
        multipliée par le nombre de fois qu'on le rencontre.

        La pausibilité est corrigé par un score issu du compte des lettres de
        bons mots, les mots trouvés dans le dictionnaire français.
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

def score(texte):
    """
        Evalue le score de la proposition de déchiffrement en repérant les mots
        réels issus de la liste des mots français.

        Le score est le rapport entre le nombre de lettres de vrais mots sur le 
        nombre de lettres total du texte (sans les espaces)
    """
    lettres_ok  = 0
    lettres_tot = 0
    mots = texte.split(" ")
    for mot in mots:
        if mot in fr_dico:
            lettres_ok += len(mot)
        lettres_tot += len(mot)
    return lettres_ok/lettres_tot    

def dechiffrer(texte, code):
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

    res  = list(texte)  # conversion en list
    i=0                 # i est l'indice global de res
    for c in res:
        if c != ' ' :
            indice = fk.index(c)
            res[i] = code[indice]
        i+=1

    return ''.join(res)


def echange(clef):
    """
        échange 2 lettres de la clef

        --
        retourne    : nouvelle clef (string)
    """
    liste=list(clef) # conversion string en list
    i, j = 0, 0

    i = np.random.randint(0,26)
    while i == j:
        j = np.random.randint(0,26)

    liste[i], liste[j] = liste[j], liste[i]
    return ''.join(liste)


def Monte_Carlo(max_iter, texte_init):
    """
    
        --
        retourne    : proposition de déchiffrement (string)
    """
    break_plau  = -1.6          # max plausibilité calculée à partir de laquelle on estime le résultat juste
    chance      = 0.05          # chance d'accépter un code moins bon pour s'éloigner d'un possible maximum local

    # la première substitution est effectuée sur la base des fréquences de référence
    cur_code    = list(freq_ref.keys())
    cur_texte   = dechiffrer(texte_init, cur_code)
    cur_plau    = plausibilite(cur_texte)

    best_code   = cur_code
    best_text   = cur_texte
    best_plau   = cur_plau
    
    cpt=0
    while cpt < max_iter :

        cpt+=1 
        # sortie prématurée de la boucle en cas de résultat satisfaisant
        if best_plau > break_plau:
            break

        # échange de 2 lettres de la clef       
        new_code  = echange(cur_code)
        new_texte = dechiffrer(cur_texte, new_code)
        new_plau  = plausibilite(new_texte)
        
        x = np.random.rand()
        # si la plausibilité est meilleure on garde le nouveau texte,
        # sinon soit on garde le nouveau texte, soit on revient au texte précédent.
        # Dépend du résultat d'un aléa:
        # TODO expliquer l'aléa
        if new_plau > cur_plau:
            logging.debug("(itération %d) Augmentation plausibilité %f -> %f", cpt, cur_plau, new_plau)
            cur_plau  = new_plau
            cur_texte = new_texte
            cur_code  = new_code
            if new_plau > best_plau:
                logging.info("(itération %d) Meilleure plausibilité %f", cpt, new_plau)
                best_text  = new_texte
                best_plau  = new_plau                
                best_code  = new_code
        else:
            # le facteur chance est d'autant plus petit qu'on avance dans les itérations
            #chance = chance * 0.99

            # plus l'écart est important, moins on a de chance d'accepter la regression
            # cur_score = score(cur_texte)
            # p = np.exp((new_plau - cur_plau) - cur_score)

            if ( (cur_plau / new_plau) * 0.001) > x :
                logging.info("(itération %d) Régression plausibilité %f -> %f", cpt, cur_plau, new_plau)
                cur_texte = new_texte
                cur_plau  = new_plau
                cur_code  = new_code                
     
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
        Chargement des mots de la langue française
    """
    fr_dico     = charge_dico()

    """
        Le texte des Misérables est analysé pour en extraire:
            - les fréquences de référence du français
            - l'indice de coincidence
            - le tableau des fréquences des bigrammes en français
    """
    logging.info("Analyse des Misérables")
    fichier = open(r'Les-misérables.txt','r')
    livre = fichier.read()
    fichier.close
    baba = simplifie(livre)
    # chargement des fréquenes des lettres de référence
    freq_ref = frequence(baba)
    # Chargement des probabilités des bigrammes de référence
    big_ref = bigramme(baba)
    ic_ref = indice(baba)
    p = plausibilite(baba)
    
    """
        Analyse d'une expression française pour vérifier la validité des fonctions d'analyse
    """
    expr_fr = "Bonjour: c'est la salutation de base en français et peut être utilisé par tout le monde. C'est un mot à la fois formel et informel"
    print("Analyse de [%s]", expr_fr)
    baba = simplifie(expr_fr)
    ic = indice(baba)
    p = plausibilite(baba)

    """
        Analyse d'une expression anglaise pour vérifier la non validité des fonctions d'analyse dans ce cas
    """
    expr_en = "Thanks so much. This is a simple sentence you can use to thank someone"
    logging.info("Analyse de [%s]", expr_en)
    baba = simplifie(expr_en)
    ic = indice(baba)
    p = plausibilite(baba)

    """
        Déchiffrement d'un texte codé par substitution.

        Une première proposition est éléborée à partir du pct d'occurence des
        lettres dans le texte chiffré qui sont comparées au pct de ref. Une 
        première substitution est appliquée.

        Cette proposition initiale est ensuite utilisée comme base de l'algorithme
        de Monte-Carlo que l'on va itérer un certain nombre de fois.
    """
    #enigme ='Gf yaom wf htmom tllao daol lwk wf mtvmt hswl sgfu eak s wmosolamogf r wf mtvmt rt mkgol dgml ft ltdzst hal ygfemogfftk assgfl hswl sgfu hgwk xgok pwljw gw ea xa'
    enigme = """NASJX OXH NXH SOE BXYA SJXEA PY SNXYZEA ! YH ZASJSEG BSP ZAEJESG, RSA G SP ZY JY ? OS BAXBXPEZEXH EHRGYZ GS DEPBSAEZEXH, P'SKKASHRUEPPSHZ D'YH SZZAENYZ BSAOE JEHTZ-PEM. BSP RXH ! (XYE C'SE KSEZ KXAZ) 
                JXEGS QYE PSHP PXYBRXH PSYAS ASJEA ZXH RENXYGXZ, XY DY OXEHP ZXH SAZ DY BLZUXH. SY BGSEPEA D'YH CXYA HXYP JXEA SYZXYA D'YH NXRV XY DY KGSRXH D'YH JEH, QY'EG PXEZ NGSHR XY AYNEP. ZXH JEG SOE"""

    logging.info("Déchiffrement de [%s]", enigme)
    baba = simplifie(enigme)
    Monte_Carlo(20000, baba)
