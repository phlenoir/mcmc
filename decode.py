# -*- coding: utf-8 -*-

import re
import numpy as np

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
        Retourne la i+1e lettre de l'alphabet 
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
    # Utilisation de la lib re = regular expression
    res = re.sub('\s+',' ', maj)
    
    print("Simplification du texte terminée: "+ str(len(res)) + " caractères")
    return res


def frequence(texte):
    """
        Compte le nombre d'occurences de chaque lettre dans un texte simplifié
        puis retourne un tableau de pourcentages sous la forme d'un dict trié
        par valeur de la plus petite (W) à la plus grande (E)
    """

    # 1 compteur par lettre de l'alphabet
    freq={x: 0 for x in alphabet}

    # total = nombre de lettres dans le texte (espace non compris)             
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
        commençant par la même lettre. ON obtient ainsi un tableau normalisé
        dont la somme des éléments de chaque ligne vaut 1.
    """   

    # matrice 26*27 ou la ligne correspond à la première lettre du bigramme et la colonne à la seconde
    #un bigramme ne commence pas par un espace (mais peut se terminer par un)
    big=np.zeros((26, 27))       
    cpt=np.zeros((26))
    
    # parcourt du text en lisant un caractère (current) et le suivant (next_)
    # on découpe ainsi le texte en bigrammes
    # pour chaque bigramme rencontré on incrémente le compteur associé dans le tableau big
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
                
    return big


def indice(texte):
    """
        Calcul de l'indice de coincidence. Cette indice permet en théorie 
        de vérifier l'indice de coïncidence d'une langue. En pratique
        celui-ci permet de vérifier si un texte est chiffré monoalphabétiquement
        ou polyalphabétiquement.

        En français, l'indice de coïncidence vaut environ 0,0778.
        Dans le cas d'une répartition aléatoire (comme en substitution
        polyalphabétique) l'indice vaut environ 0.0385.
        
        REFERENCE https://www.dcode.fr/indice-coincidence
    """
    sum = 0
    total = 0

    for c in alphabet:
        total += texte.count(c)
    denom = total*(total-1)

    freq = frequence(texte)
    for f in list(freq.values()):
        # ici on retrouve le nb d'occurences de chaque lettre en multipliant 
        # le frequence par le nombre total de caractères dans la chaine
        occ=f*total
        sum = sum + occ*(occ-1) 

    res = sum/denom

    print("Indice de coincidence du texte (vaut environ 0.0746 en français) : " + str(res))
    return res


def plausibilite(texte, big_ref):
    #texte -> chaine dont on veut extraire la plausibilité
    #big_ref -> bigramme de référence issu de Victor Hugo
    """
        Caclul de la plausibilité p d'un texte à partir du tableau des bigrammes
        issu de l'analyse des Misérables.

        La plausibilité c'est la somme des ln des probabilités de rencontrer un bigramme
        multipliée par le nombre de fois où on le rencontre.
        
        Le résultat est supérieur à -2 pour un texte plausible
        et peut descendre jusqu'à -8 pour des textes absurdes'
    """
    
    #permet d'éviter de prendre log(0) mais reste assez petit pour ne pas influencer le résultat
    epsilon = 10e-7

    # repérage des bigrammes dans le texte, à chaque occurence on ajoute le log
    # de la probabilité (+ epsilon pour traiter les cas nuls)
    big=np.zeros((26, 27))
    s=list(texte)
    current = s[0]
    for next_ in s[1:] :
        if current != ' ' :
            i = char_to_id(current)
            j = char_to_id(next_)
            big[i][j]+=np.log(big_ref[i][j] + epsilon)
        current = next_

    plau=np.sum(big)/len(texte)

    return plau


def dechiffrer(texte, clef):
    #texte -> chaîne que l'on veut déchiffrer
    #clef -> clé de dechiffrement
    """
        Prend un texte chiffré en argument et renvoie une proposition de 
        dechiffrement basée sur la clef
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
            sub = clef[indice]
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
    #max_iter -> nombre maximale d'itérations maximales de Monte_Carlo
    #plau_init -> plausibilité de la proposition initiale
    #code_init -> clé de dechiffremnt initiale basée sur la fréquence des lettres
    #big_ref -> bigramme de référence issu de Victor Hugo
    #texte_init -> Texte à dechiffrer
    
    #plausibilité de VH :-1.65 on estime qu'au deça de -1.6 on est suffisement proche pour s'arrêter
    #Pas forcément très utile surtout lorsqu'on utilisera le dico
    break_plau = -1.60

    cur_code  = code_init
    cur_texte = str(texte_init) #copie
    cur_plau  = plau_init

    best_code = code_init
    best_text = str(texte_init)
    best_plau = plau_init
    
    cpt=0
    while cpt < max_iter :

        cpt+=1 
        # sortie prématurée de la boucle en cas de résultat satisfaisant
        if best_plau > break_plau:
            break

        # échange de 2 éléments au hasard
        i = np.random.randint(0,26)
        j = np.random.randint(0,26)
        while i==j:
            j = np.random.randint(0,26)
        new_code  = echange(cur_code, i, j)
        new_texte = dechiffrer(cur_texte, new_code)
        new_plau  = plausibilite(new_texte, big_ref)
        
        x = np.random.rand()
        # si la plausibilité est meilleure on garde le nouveau texte,
        # sinon soit on garde le nouveau texte, soit on revient au texte précédent.
        # On le garde selon un lancé de pièce truqué
        if new_plau > cur_plau:
            cur_plau  = new_plau
            cur_texte = new_texte
            cur_code  = new_code
            if new_plau > best_plau:
                best_text = new_texte
                best_plau = new_plau                
                best_code = new_code
        else:            
            if ( (cur_plau / new_plau) * 0.001) > x :
                print("itération " + str(cpt) + " saut de " + str(cur_plau) + " vers " + str(new_plau))
                cur_texte = new_texte
                cur_plau  = new_plau
                cur_code  = new_code

    print("Proposition finale " + str(best_plau) + " " + best_text)
    return best_code


"""
    Le texte des Misérables est analysé pour en extraire:
        - les fréquences de référence du français
        - l'indice de coincidence
        - le tableau des probabilités d'occurences des bigrammes en français
"""
print("Analyse des Misérables")
fichier = open(r'Les-misérables.txt','r')
livre = fichier.read()
fichier.close
baba = simplifie(livre)
freq_ref = frequence(baba)
big_ref = bigramme(baba)
p = plausibilite(baba, big_ref)


"""
    Déchiffrement d'un texte codé par substitution.

    Une première proposition est éléborée à partir du % d'occurence des
    lettres dans le texte chiffré qui sont comparées au % de ref. Une 
    première substitution est appliquée.

    Cette proposition initiale est ensuite utilisée comme base de l'algorithme
    de Monte-Carlo que l'on va itérer un certain nombre de fois.
"""
enigme='Lo zotf jwt stl mokaosstwkl rt sa souft kafutl tm a s ayywm rtkkotkt stwk stxtt rt haxtl, tm stl mokaosstwkl rt sa zafsotwt dalltl a s afust rt sa kwt, lt dgfmktktfm lgwraoftdtfm  jwtsjwt eiglt jwo ktdwaom rafl sa ywdtt.'
baba = simplifie(enigme)
prop = dechiffrer(baba, list(freq_ref.keys()))
p = plausibilite(prop, big_ref)
print("Proposition initiale " + prop + str(p))

Monte_Carlo(50000, p, list(freq_ref.keys()), big_ref, prop)

# enigme="Si bien que les tirailleurs de la ligne rangés et à l'affût derrière leur levée de pavés, et les tirailleurs de la banlieue massés à l'angle de la rue, se montrèrent soudainement  quelque chose qui remuait dans la fumée."
# baba = simplifie(enigme)
# p = plausibilite(baba, big_ref)