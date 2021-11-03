# -*- coding: utf-8 -*-
"""
Created on Fri May 14 13:58:23 2021

@author: jerem
"""
import numpy as np
import random as rd

lettre=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
lettre2=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',' ']

def frequence_generale():
    compteur=[]                 #On commence par créer un compteur pour chaque lettre
    total=0                     #compteur pour le nombre total de lettre
    for i in range(26):
        compteur.append(0)

    fichier = open(r'C:\Users\jerem\OneDrive\Documents\Cours\Spé\TIPE\Les-misérables.txt','r')
    livre= fichier.read()
    
    for i in range(len(livre)):

        if livre[i].upper() in lettre:                  #upper() permet de convertir les caractères en majuscule
            for k in range(len(lettre)):
                if livre[i].upper()==lettre[k]:         #On ajoute 1 au compteur à chaque fois que l'on croise la lettre correspondante
                    compteur[k]+=1
                    total+=1

    
    for i in range(len(compteur)):
        compteur[i]=int(((compteur[i]/total)*100)*10**3)/10**3   #Renvoie le résultat en pourcentage à 4 chiffres significatifs
    
    fichier.close()
    return compteur


def indice():
    indice=0
    compteur=[]                 #On commence par créer un compteur pour chaque lettre
    total=0                     #compteur pour le nombre total de lettre
    for i in range(26):
        compteur.append(0)

    fichier = open(r'C:\Users\jerem\OneDrive\Documents\Cours\TIPE\Les-misérables.txt','r')
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


def bigramme_general():
    
    bigramme=np.zeros((len(lettre),len(lettre2)))       #on crée un matrice 26*27 ou la ligne correspont à la première lettre et la colonne la seconde
    compteur=np.zeros((len(lettre)))
    
    fichier = open(r'C:\Users\jerem\OneDrive\Documents\Cours\Spé\TIPE\Les-misérables.txt','r')
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



def min_matrice(A):
    res=1
    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j]!=0:
                if res > A[i][j]:
                    res=A[i][j]
    return res

def echange(liste,i,j):
    
    temp=liste[i]
    liste[i]=liste[j]
    liste[j]=temp
    return liste


proba=np.load("ProbaV3.npy")


def plausibilite(texte):
    
    p=0                                                     #définiera la plausibilite
    bigramme=np.zeros((len(lettre),len(lettre2)))
    compteur_lettre=np.zeros(len(lettre))
    
    for i in range(len(texte)-1):
        
        for k in range(len(lettre)):                        #pour chaque lettre, on va regarder celle qui suit et ajouter 1 au bigramme correspondant
            if texte[i].upper()==lettre[k]:
                for j in range(len(lettre2)):
                    if texte[i+1].upper()==lettre2[j]:
                        bigramme[k][j]+=1
                        compteur_lettre[k]+=1
        
    """
    for h in range(len(lettre)):
        for f in range(len(lettre2)):
            if compteur_lettre[h]!=0:
                bigramme[h][f]=bigramme[h][f]/compteur_lettre[h]
    """

    for h in range(len(lettre)):
        for f in range(len(lettre2)):            
            if proba[h][f]!=0:
                p+=bigramme[h][f]*np.log(proba[h][f])     #la plausibilite c'est la somme des probabilités de rencontrer un bigramme multipliées par le nombre de fois qu'on le rencontre

    p=p/len(texte)
    
    """
    if p > -5:
        p+=(1-p%1)*10                   #après quelques tests, on a clairement une barrière entre les textes ayant une plausibilité inférieure à -5 et les autres, on essaie d'exploiter cette barrière
    else:
        p+=-(p%1)*10
    """
    return p

frequ=np.load("Fréquence.npy")
frequ2=frequ.copy()
frequ2.sort()

frequ_lettre=[]

for i in range(len(frequ)):
    for j in range(len(frequ)):
        if frequ2[i]==frequ[j]:
            frequ_lettre.append(j)

def frequence(texte):
    
    compteur=[]                 #On commence par créer un compteur pour chaque lettre
                                
    for i in range(26):
        compteur.append(0)
    
    for i in range(len(texte)):
        for k in range(len(lettre)):
            if texte[i].upper()==lettre[k]:
                compteur[k]+=1

    return np.argsort(compteur)    
    

def proposition_initiale(texte): #prend un texte chiffré en argument et renvoie une proposition de dechiffrement initial (basé sur la fréquence)
    
    frequ_texte=frequence(texte)
    res=[char for char in texte]  #copie du texte sur lequel on travaille
    for i in range(len(res)):
        if res[i]!= ' ':
            
            indice=0
            temp=res[i]
            indice_bis=0
            
            for j in range(len(lettre)):
                if temp.upper()==lettre[j]:
                    indice=j
                    
            for k in range(len(frequ_texte)):
                if frequ_texte[k]==indice:
                    indice_bis=k
                    
            res[i]=lettre[frequ_lettre[indice_bis]]
            
    res="".join(res)
    return res
    
def Monte_Carlo(texte):
    
    sample=[]
    for i in range(26):
        sample.append(i)
    
    compteur=0
    liste_pl=[]
    
    
    proposition=frequence(texte)
    res=proposition_initiale(texte)
    p=plausibilite(res)
    print(res,p)
    
    while compteur<3000:
        transposition=rd.sample(sample,2)
        echange(proposition,transposition[0],transposition[1])
        
        essaie=[char for char in res]  #copie du texte sur lequel on travaille
        for i in range(len(essaie)):
            if essaie[i]!= ' ':
                
                indice=0
                temp=essaie[i]
                indice_bis=0
                
                for j in range(len(lettre)):
                    if temp.upper()==lettre[j]:
                        indice=j
                        
                for k in range(len(proposition)):
                    if proposition[k]==indice:
                        indice_bis=k
                        
                essaie[i]=lettre[frequ_lettre[indice_bis]]
                
        essaie="".join(essaie)
        
        p2=plausibilite(essaie)
        compteur+=1
        #liste_pl.append((p,p2))
        
        
        if p<p2:
            p=p2
            res=essaie

            
        else:
            f=rd.random()
            a=max(abs(p),abs(p2))
            b=min(abs(p),abs(p2))
            
            if a-b>0.5:
                echange(proposition,transposition[0],transposition[1])
                
            elif f>b/a:
                p=p2
                res=essaie
                
            else:
                echange(proposition,transposition[0],transposition[1])
               
    
    return res,p #,liste_pl

print(plausibilite('On fait un petit essai mais sur un texte plus long car l utilisation d un texte de trois mots ne semble pas fonctionner allons plus long pour voir jusqu ou ca va'))
#print(Monte_Carlo('Gf yaom wf htmom tllaot daol lwk wf mtvmt hswl sgfu eak s wmosolamogf r wf mtvmt rt mkgol dgml ft ltdzst hal ygfemogfftk assgfl hswl sgfu hgwk xgok pwljw gw ea xa'))
print(plausibilite('zwxz wxzkml nbvxc'))
    
    
    
