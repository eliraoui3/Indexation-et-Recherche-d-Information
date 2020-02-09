# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:49:29 2019

@author: amine el iraoui
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.messagebox as MB
from tkinter import Spinbox 
from tkinter.filedialog import askopenfilename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import glob

from nltk import stem

import pandas as pd

fen = Tk()
fen.title("Myapp")
fen.geometry('800x600')
fen.config(bg='skyblue')



"""*************************************** Les Fonctions ************************************************"""

def pretraitement_fichiers(nom_fichier):#pretraitement de chaque fichier et retourner liste des mots cadicale de tt les term de la fichier
    
    file=open(nom_fichier,"r")
    text=file.read()
    file.close()
    
    stop_words = set(stopwords.words('english'))
    mots = word_tokenize(text)

    liste_mots = []
    for word in mots:
        if word.lower() not in stop_words:
            liste_mots.append(word)
 
    mots_final=[]
    for tokenize in liste_mots:
        if tokenize not in string.punctuation:
            mots_final.append(tokenize)
    return limmatiser_mots(mots_final)

def limmatiser_mots(liste_mots):#fonction pour rendre les mots en radicale : (limmatisation)
    for i in range(len(liste_mots)):
        liste_mots[i]=stem.WordNetLemmatizer().lemmatize(liste_mots[i])
    return liste_mots

"""******************************************* Le Corps ***************************************************"""
var=StringVar()
sais= Entry(fen,textvariable = var,width=50)
sais.pack()

frame = Frame(fen,width=100, height=20, background='sky blue', colormap="new")
frame.pack()
T = tk.Text(frame, height=20, width=100)

def execute():
    synonyms = []  
    for syn in wordnet.synsets(var.get()): #pour retourner les synonymes de la requete
        for l in syn.lemmas(): #limatiser les synonymes
            synonyms.append(l.name())
    file=open("./files/requet.txt","w")
    file.write(var.get())
    file.write(" ")
    file.write(synonyms[1])#ecriture du premier synonym dans la fichier request 
    file.close()
    noms_fichiers=glob.glob('./files/corpus/*.txt') #liste des nom de toutes les fichiers .txt qui dans la repertoire "corpus"
    nom_fichier_req=glob.glob('./files/*.txt')[0]  #nom de premier fichier(qui contient requet)
    """ limatization de la requet """
    req_limatizer=pretraitement_fichiers(nom_fichier_req)
    chaine_req_limatizer=""
   
    for mot in req_limatizer:     
        chaine_req_limatizer=chaine_req_limatizer+" "+mot
    """ limatization de la corpus tout entier fichier par fichier """
    corpus_avec_lemmatizer=[]
    for file in noms_fichiers:
        chaine_limatizer=""
        d_limatizer=pretraitement_fichiers(file) # fonction retourn une liste des termes qui sont  limatizer 
        for mot in d_limatizer:
            chaine_limatizer=chaine_limatizer+" "+mot       #concatination des mots de chaque corpus et metre dans un liste
        corpus_avec_lemmatizer.append(chaine_limatizer)  #pour chaque doc en ajoute les chaines qui sont limatizer dans corpus_avec_lemmatizer
    """l'ajoute de chaine qui contient la requet qui deja limatizer à la liste des chaines des documents qui sont aussi deja limatizer """
    corpus_avec_lemmatizer.append(chaine_req_limatizer)
    """  creation d'une matrice de terme par documents à partir de nos chaines des caratere limatiser (corpus_avec_lemmatizer) """
    vect =TfidfVectorizer()
    #dtm : document term matrix
    """transformons notre objet TfidfVectorizer , Dans notre cas, nous allons nommer la sortie représentant cette matrice dtm """
    dtm = vect.fit_transform(corpus_avec_lemmatizer)
    """Simple afficher de la matrice pour la vusialisation"""
    #"print("\n\n\n \t\t\t************ Visualisation ************")
    T.insert(tk.END,"\n\n\n \t\t\t************ Visualisation ************\n")
    #print(pd.DataFrame(dtm.toarray(), columns=vect.get_feature_names()) )
    T.insert(tk.END ,pd.DataFrame(dtm.toarray(), columns=vect.get_feature_names()))
    
    #print("\t\t--------  Remarque!! 'doc",len(noms_fichiers),"' c'est la requet  --------")
    T.insert(tk.END ,"\t\t\n--------  Remarque!! 'doc"+str(len(noms_fichiers))+"' c'est la requet et Synonyme est "+str(synonyms[1])+"--------\n")
    """associe la similarite de la requet avec chaque document  et stocker dans un dictionnaire 'dict_similarite' """
    dict_similarite={}
    i=0
    for sim in cosine_similarity(dtm[len(corpus_avec_lemmatizer)-1],dtm)[0]:
        dict_similarite[i]=sim
        i=i+1
    """trier le dictionnaire des similarite par ordre decroissante (le premier c'est le plus similaire) """
    dict_items_simil = dict_similarite.items()
    similarite_final_desc = sorted(dict_items_simil, key=lambda x: x[1],reverse=True)
    """retirer la premiere la similarite i.e la similarite de la requet elle meme """
    similarite_final_desc.pop(0)  
    #print("\n\n \t\t\t************ Resultat ************")
    T.insert(tk.END ,"\n\n \t\t\t************ Resultat ************\n")
    #noms_fichiers.append(nom_fichier_req)
    """Affichage des nom des fichiers par ordre de similarite (le premier le plus similaire) """
    for s in similarite_final_desc:  
        #print("doc",s[0],"--->",noms_fichiers[s[0]],"---> similarite =",s[1])
        T.insert(tk.END ,"doc"+str(s[0])+"--->"+str(noms_fichiers[s[0]])+"---> similarite ="+str(s[1])+"\n")
    T.pack()
fen.update()
h=fen.winfo_height()
w=fen.winfo_width()
S = tk.Scrollbar(fen)
T = tk.Text(fen, height=h, width=w)
def limatiser():
    fen1 = Tk() 
    fen1.title("Limatiser File")
    root = ttk.Frame(fen1, borderwidth=2,  relief=tk.RAISED, padding=30)
    sw = fen1.winfo_screenwidth()
    sh = fen1.winfo_screenheight()
    fen1.geometry("%dx%d+%d+%d" % (650, 550, (sw-650)/2, (sh-650)/2))
    fen1.resizable(False,False)
    def fichier_train():
        path = askopenfilename()
        f_training.delete(0, tk.END)
        f_training.insert(0, path)
    def reset():
        f_training.delete(0, tk.END)
    def valider():
        if not f_training.get() :
            tk.messagebox.showinfo("Message","Choisissez un fichier  SVP !") 
        else:
            l=[]
            l=pretraitement_fichiers(f_training.get())
            root.grid_forget()
            fen1.configure(background='#f0f0f0')
            T.delete(1.0,tk.END)
            S.pack(side=tk.RIGHT, fill=tk.Y)
            T.pack(side=tk.LEFT, fill=tk.Y)   
            T.insert(tk.END, l)
            T.config(state = tk.DISABLED)
            S.config(command=T.yview)
            T.config(yscrollcommand=S.set)
            fen1.resizable(False,False)  
    def quit():
        fen1.destroy()
    btn_reset = ttk.Button(root, text="Réinitialiser", command=reset, underline=0) 
    btn_valid = ttk.Button(root, text="Valider", command=valider, underline=0)  
    chose_training = ttk.Label(root, text="Choisir fichier pour limatiser: ", background='#f0f0f0',width=25)
    f_training = ttk.Entry(root, width=33)
    button_trn = ttk.Button(root, text="Parcourir...", command=fichier_train, width=10, cursor="hand2")
    fen1.rowconfigure(0, minsize=75)
    root.grid(row=1, column=0, padx=60,pady=60)
    root.rowconfigure(0, minsize=20)
    root.rowconfigure(5, minsize=60)
    chose_training.grid(row=2, column=0, padx=10,pady=10)
    f_training.grid(row=2, column=1, padx=10,pady=10)
    button_trn.grid(row=2, column=2)
    btn_valid.grid(row=6, column=1, sticky='w')
    btn_reset.grid(row=6, column=1, sticky='e')
    fen1.resizable(False,False)
    fen1.update()
    h=fen1.winfo_height()
    w=fen1.winfo_width()
    S = tk.Scrollbar(fen1)
    T = tk.Text(fen1, height=h, width=w)
    menubar = tk.Menu(fen1)
    menu1 = tk.Menu(menubar, tearoff=0)
    menu1.add_command(label="Réinitialiser", command=reset)
    menu1.add_command(label="Limatiser", command=limatiser)
    menu1.add_separator()
    menu1.add_command(label="Quitter", command= quit)
    fen1.config(menu=menu1)
   
def reset():
        sais.delete(0, tk.END)    
def quit():
    fen.destroy()	
btn_valid = ttk.Button(frame, text="Search", command=execute, underline=0)
btn_valid.grid(row=6, column=3, sticky='w')
menubar = tk.Menu(fen)
menu1 = tk.Menu(menubar, tearoff=0)
menu1.add_command(label="Reset", command=reset)
menu1.add_command(label="Limatiser", command=limatiser)
menu1.add_separator()
menu1.add_command(label="Quitter", command= quit)
fen.config(menu=menu1)
btn_quit = ttk.Button(frame, text="Quitter", command=quit, underline=0) 
btn_quit.grid(row=6, column=0, sticky='e')
mainloop()
