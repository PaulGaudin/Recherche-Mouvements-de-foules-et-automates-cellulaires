#from Reinject import resolv,creerSalle
from fct import *
from base import *
import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
import timeit
from matplotlib import animation, rc
from random import randint

    

"""Affiche une simulation de Npas de mu (mu allant de 0 a 1) en fonction de k et d'une pièce de densité et taille donné, Nsim simulations par pas
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


"""Fonction permettant de calculer l'écart type
@params:
- tableau un tableau de valeurs dont on veut calculer l'écart type

@return:
- l'écart type des données contenues dans tableau
"""
def ecartType(tableau):
    #On défini la moyenne du tableau:
    moy=0
    for i in range(len(tableau)):
        moy=moy+tableau[i]
    moy=moy/len(tableau)
    #On definit la variance
    varTableau=0
    for i in range(len(tableau)):
        varTableau=varTableau + (tableau[i]-moy)**2

    varTableau=varTableau/len(tableau)

    #Puis on retourne l'écart type qui est la racine carrée de la variance
    return np.sqrt(varTableau)


"""Affiche une simulation de Npas de mu (mu allant de 0 a 1) en fonction de k et d'une pièce de densité et taille donné, Nsim simulations par pas
@params:
- d la densité de population dans la pièce
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- u le mu a utiliser
- kmin le kappa minimum a considérer
- kmax le kappa maximuma considérer
- Npas le nombre de pas
- Nsim le nombre de simulations par pas

@return:
- le tableau contenant toute les valeurs de nombre de tours mises par chacune des simulations a faire sortir tout les agents
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


"""#Pareil que SimulationsU mais donne les résultats en mètres et en secondes au lieu de cellules et étapes
@params:
- d la densité de population dans la pièce
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- k le kappa a utiliser
- le nombre de pas
- le nombre de simulations par pas
"""
@timer    
def SimulationsUR(d,taille,k,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    u=np.linspace(0,1,Npas)
    Ntours=np.asarray([[resolv(Terrain,k,ut) for Terrain in Terrains] for ut in u])
    N=np.zeros(Npas)
    ecart=np.zeros(Npas)
    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size
        ecart[i]=ecartType(Ntours[i])


    fig = plt.figure(figsize=(15,10))
    plt.plot(u,N*0.27)
    plt.xlabel("U")
    plt.ylabel("Temps (en s)")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille[0]*0.4,taille[1]*0.4} mètres et densité {d}, en fonction de u (coeff de friction), pour k={k} ({Nsim} simulations par pas, {Npas} pas de u)")
    plt.errorbar(u, N*0.27, yerr=ecart, fmt = 'none', capsize = 10, ecolor = 'red', zorder = 1)
    plt.show()


"""Pareil que SimulationsK mais donne les résultats en mètres et en secondes au lieu de cellules et étapes
@params:
- d la densité de population dans la pièce
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- u le mu a utiliser
- kmin le kappa minimum a considérer
- kmax le kappa maximuma considérer
- Npasle nombre de pas
- Nsim le nombre de simulations par pas
"""
@timer
def SimulationsKR(d,taille,u,kmin,kmax,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    k=np.linspace(kmin,kmax,Npas)
    Ntours=np.asarray([[resolv(Terrain,kt,u) for Terrain in Terrains] for kt in k])
    N=np.zeros(Npas)
    ecart=np.zeros(Npas)
    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size
        ecart[i]=ecartType(Ntours[i])

    fig = plt.figure(figsize=(15,10))
    plt.plot(k,N*0.27)
    plt.xlabel("k")
    plt.ylabel("Temps (en s)")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille[0]*0.4,taille[1]*0.4} mètres et densité {d}, en fonction de k, pour u={u} ({Nsim} simulations par pas, {Npas} pas de k, et k variant de {kmin} a {kmax})")
    plt.errorbar(k, N*0.27, yerr=ecart, fmt = 'none', capsize = 10, ecolor = 'red', zorder = 1)
    plt.show()