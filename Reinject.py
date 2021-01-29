from fct import friction,Init,timer,creerSalle
from Graphes import ecartType
import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
import timeit
from matplotlib import animation, rc
from random import randint

"""Fonction effectuant un déplacement complet de tout les automates en parallèle (méthode de friction), en ajoutant la réinjection des automates passant la porte 
@params:
- TM le tableau dont on veut effectuer le déplacement
- k le kappa a utiliser
- u le mu a utiliser

@return:
- Temp le nouveau tableau correspondant au tour k+1 a partir de TM, le tableau correspondant au tour k
- k le nombre de personnes ayant été réinjectés
"""
def Deplacement(TM,k,u):
    New,n=friction(TM,k,u)
    Temp=Init(TM.shape[0]-2,TM.shape[1]-2)


    if(np.shape(New)[0]==0):
        return Temp
        
    else:
        x,y=New.transpose()
        Temp[x,y]=1
        Temp[0,int(TM.shape[1]/2)]=Temp[0,int((TM.shape[1]/2)-1)]=2
        k=0
                    
        #On veut maintenant reinjecter le nombre de personnes sortantes dans Temp vers le fond
        #On creer un espace de coordonées ou reinjecter les personnes = 2 bandes au fond de la salle
        x_reinjection_min=(len(TM)-1)-3
        x_reinjection_max=(len(TM)-1)-1

        y_reinjection_min=1
        y_reinjection_max=len(TM-1)-2

        while(np.sum(TM==1)!=np.sum(Temp==1)): 


            #Pour chaque personne a reinjecter, on choisit des coordonées au hasard dans la rectangle de respawn
            new_x=new_y=0

            while(Temp[new_x,new_y]!=0):
                new_x=new_y=0
                new_x=randint(x_reinjection_min, x_reinjection_max)
                new_y=randint(y_reinjection_min, y_reinjection_max) 

            Temp[new_x,new_y]=1
            k+=1
    
    return Temp,k

"""Affiche une purge complète d'une salle de densité et taille donnée, selon un kappa et mu donné (avec réinjection)
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
    X=np.sum(TM==1)*2
    NStop=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1 and NStop<X):
        TM,n=Deplacement(TM,k,u)
        NStop+=n
        evol.append(TM)
        Nb+=1

    cmap = matplotlib.colors.ListedColormap(['white','black',"red", "gray"])
    boundaries = [-0.2, 0.5, 1.5, 2.5, 3.5]
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

    #video = HTML(ani.to_html5_video())
    plt.show()
    plt.clf()
    return Nb
        

"""Effectue une résolution complète et renvoie le nombre de tour necessaire a celle-ci (avec réinjection)
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
    X=np.sum(TM==1)
    NStop=0
    Na=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1 and NStop<(X*3)):
        TM,n=Deplacement(TM,k,u)
        NStop+=n
        if(NStop==(X*2)):
            Na=Nb
        Nb+=1
    return Nb-Na

"""Affiche une simulation de Npas de mu (mu allant de 0 a 1) en fonction de k et d'une pièce de densité et taille donné, Nsim simulations par pas (avec réinjection)
@params:
- d la densité de population dans la pièce
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- k le kappa a utiliser
- le nombre de pas
- le nombre de simulations par pas
"""
@timer    
def SimulationsU(d,taille,k,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    u=np.linspace(0,1,Npas)
    Ntours=np.asarray([[resolv(Terrain,k,ut) for Terrain in Terrains] for ut in u])
    N=np.zeros(Npas)
    ecart=np.zeros(Npas)

    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size
        ecart[i]=ecartType(Ntours[i])

    fig = plt.figure(figsize=(15,10))
    plt.plot(u,N)
    plt.xlabel("U")
    plt.ylabel("Nombre de tours")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille} et densité {d}, en fonction de u (coeff de friction), pour k={k} ({Nsim} simulations par pas, {Npas} pas de u)")
    plt.errorbar(u, N, yerr=ecart, fmt = 'none', capsize = 10, ecolor = 'red', zorder = 1)
    plt.show()


"""Affiche une simulation de Npas de mu (mu allant de 0 a 1) en fonction de k et d'une pièce de densité et taille donné, Nsim simulations par pas (avec réinjection)
@params:
- d la densité de population dans la pièce
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- u le mu a utiliser
- kmin le kappa minimum a considérer
- kmax le kappa maximuma considérer
- Npas le nombre de pas
- Nsim le nombre de simulations par pas

@return:
- Le nombre de tour mis par chacune des simulations pour purger la pièce
"""
@timer
def SimulationsK(d,taille,u,kmin,kmax,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    k=np.linspace(kmin,kmax,Npas)
    Ntours=np.asarray([[resolv(Terrain,kt,u) for Terrain in Terrains] for kt in k])
    N=np.zeros(Npas)
    ecart=np.zeros(Npas)

    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size
        ecart[i]=ecartType(Ntours[i])

    fig = plt.figure(figsize=(15,10))
    plt.plot(k,N)
    plt.xlabel("k")
    plt.ylabel("Nombre de tours")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille} et densité {d}, en fonction de k, pour u={u} ({Nsim} simulations par pas, {Npas} pas de k, et k variant de {kmin} a {kmax})")
    plt.errorbar(k, N, yerr=ecart, fmt = 'none', capsize = 10, ecolor = 'red', zorder = 1)
    plt.show()
    return Ntours