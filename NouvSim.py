from fct import plotSalle,afficheSFF,Init,SFF,w,p,p2,Mouvement,update,friction,timer
from base import *
import numpy as np
from random import randint

def creerSalle(nb, Ly, Lx): #Attention, nb doit etre inferieur à (Lx)*(Ly)
    ligneMur = [3]*(Ly+2)
    colonneMur = [3]*Lx
    #Rempli la salle avec un nombre nb de gens
    salle=np.zeros((Ly, Lx))
    print(len(salle))
    
    x_reinjection_min=0
    x_reinjection_max=(len(salle)-1)
    y_reinjection_min=0
    y_reinjection_max=len(salle-1)

    new_x=new_y=0
    for i in range(nb):
        new_x=randint(x_reinjection_min, x_reinjection_max)
        new_y=randint(y_reinjection_min, y_reinjection_max)
        
        while(salle[new_x,new_y]!=0):
            new_x=randint(x_reinjection_min, x_reinjection_max)
            new_y=randint(y_reinjection_min, y_reinjection_max) 

        salle[new_x,new_y]=1
            

    #créer des murs en gris
    salle = np.column_stack((colonneMur, salle, colonneMur))
    salle = np.vstack((ligneMur, salle, ligneMur))

    #créer une porte representée en rouge
    salle[0,int(Lx/2)]=2
    salle[0,int((Lx-1)/2)]=2
    return salle