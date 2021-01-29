from fct import friction,Init,timer,creerSalle
import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
import timeit
from matplotlib import animation, rc

"""Fonction effectuant un déplacement complet de tout les automates en parallèle (méthode de friction): 
@params:
- TM le tableau dont on veut effectuer le déplacement
- k le kappa a utiliser
- u le mu a utiliser

@return:
- la pièce avec tout les agents déplacés
"""
def Deplacement(TM,k,u):
    New=friction(TM,k,u)
    Temp=Init(TM.shape[0]-2,TM.shape[1]-2)
    if(np.shape(New)[0]==0):
        return Temp
    else:
        x,y=New.transpose()
        Temp[x,y]=1
        Temp[0,int(TM.shape[1]/2)]=Temp[0,int((TM.shape[1]/2)-1)]=2
        return Temp


"""Effectue une résolution complète et renvoie le nombre de tour necessaire a celle-ci
@params:
- TM le tableau dont on veut effectuer la résolution
- k le kappa a utiliser
- u le mu a utiliser

@return:
- Nb le nombre de tour mis pour purger la salle
"""
@timer
def resolv(TM,k,u):
    Nb=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1):
        TM=Deplacement(TM,k,u)
        Nb+=1
    return Nb


"""Affiche une purge complète d'une salle de densité et taille donnée, selon un kappa et mu donné
@params:
- d la densité de population dans la pièce
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- k le kappa a utiliser
- u le mu a utiliser

@return:
- Nb le nombre de tour mis pour purger la salle
"""
def resolution(d,taille,k,u):
    TM=creerSalle(d,taille[0],taille[1])
    evol=[TM]
    Nb=0
    while((TM==Init(taille[0],taille[1])).all()!=1):
        TM=Deplacement(TM,k,u)
        evol.append(TM)
        Nb+=1

    cmap = matplotlib.colors.ListedColormap(['white','black',"red", "gray"])
    boundaries = [-0.2, 0.5, 1.5, 2.5, 3.5 ]
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)

    fig, ax = plt.subplots(figsize=(np.shape(TM)[1]/2,np.shape(TM)[0]/2))
    cax = ax.pcolormesh(np.array([[]]),cmap=cmap,norm=norm)

    def init():
        cax = ax.pcolormesh(evol[0],cmap=cmap,norm=norm)
        return cax

    def animate(i):
        cax = ax.pcolormesh(evol[i],cmap=cmap,norm=norm)
        
        ax.set_title(f"Tour numéro {i}, il reste {np.sum(evol[i]==1)} automates")
        return cax

    ani = animation.FuncAnimation(fig, animate, init_func=init, frames=Nb, interval=200, blit=False)

    plt.show()
    plt.clf()
    return Nb