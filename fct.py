import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt

def plotSalle(S):
    cmap = matplotlib.colors.ListedColormap(['white','black',"red", "gray"])
    boundaries = [-0.2, 0.5, 1.5, 2.5, 3.5 ]
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)
    plt.figure(figsize=(5,5))
    plt.pcolor(S,cmap=cmap,norm=norm)
    plt.show()  

## A GARDER
def creerSalle(densite,Ly,Lx):
    Ly=Ly+2
    Lx=Ly+2
    #rempli la salle avec des gens aleatoirement placés
    salle=np.random.binomial(1, densite, size=(Ly,Lx))
    
    #créer des murs en gris
    for i in range(0, Lx):
        salle[0][i]=3
        salle[Ly-1][i]=3
    for i in range(0, Ly):
        salle[i][0]=3
        salle[i][Lx-1]=3
    #créer une porte representée en rouge
    salle[0][int(Lx/2)]=2
    salle[0][int((Lx-1)/2)]=2
    return salle


def SFF(salle):
    Lx=len(salle)
    Ly=len(salle[0])
    attractionCase=np.zeros((Ly, Lx))
    for i in range(1, Ly-1):
        for j in range(1, Lx-1):
            attractionCase[i][j]=np.sqrt(  pow(  abs(i-int(Lx/2))  ,2  ) + pow((j-0),2))*0.4
            
    return attractionCase

## A GARDER
#Afficher SFF
def afficheSFF(salle):
    Ly=len(salle)
    Lx=len(salle[0])    
    x=np.linspace(0, Lx+1, Lx+1)
    y=np.linspace(0, Ly+1, Ly+1)
    z=SFF(salle)
    fig=plt.figure()
    im=plt.pcolor(x, y, z)
    
    fig.colorbar(im)
    plt.show()

#poid mouvement
def w(K, x, y, salle):
    poids=SFF(salle)
    δ=(salle[x][y]==0) #va renvoyer 1 si c'est vrai, et 0 si c'est faux
    w=np.exp(-K*poids[x][y]) * δ
    return w
