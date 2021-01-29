from fct import plotSalle,afficheSFF,Init,SFF,w,p,p2,Mouvement,update,friction,timer
from Graphes import ecartType
from base import *
import numpy as np
from random import randint


"""Créé une salle contenant un nombre déterminé de personnes a l'intérieur
@params:
- nb le nombre de personne a placer dans la salle
- Ly les dimensions verticales de la salle
- Lx les dimensions horizontales de la salle

@return:
- Une salle de dimension Lx*Ly contenant nb personnes placés aléatoirement
"""
def creerSalle(nb, Ly, Lx): #Attention, nb doit etre inferieur à (Lx)*(Ly)
    ligneMur = [3]*(Ly+2)
    colonneMur = [3]*Lx
    #Rempli la salle avec un nombre nb de gens
    salle=np.zeros((Ly, Lx))
    print(len(salle))
    
    x_reinjection_min=0
    x_reinjection_max=len(salle)-1
    y_reinjection_min=0
    y_reinjection_max=len(salle)-1

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


"""Affiche chaque tour jusqu'a ce que tout les automates soient sortis
@params:
- TM la salle
- k le kappa voulu
- u le mu voulu

@return:
- Nb le nombre de tour mis pour purger la salle
"""
def resolutionSansVideo(TM,k,u):
    evol=[TM]
    Nb=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1):
        TM,A=Deplacement(TM,k,u)
        evol.append(TM)
        Nb+=1
    return Nb

"""fct qui fait tourner un certain nbr de fois resolution 1 pour une piece creée avec creerSalle mais qui ne l'affiche pas
@params:
- nbP le nombre de personne a placer dans la salle
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- k le kappa voulu
- u le mu voulu
- nbSim le nombre de simulations a effectuer

@return:
- Le temps mis par chacune des simulations pour purger la salle
"""
def faisTourner(nbP, taille, k, u, nbSim ):
    temps=[]  
    for i in range(nbSim):
        TM=creerSalle(nbP, taille[0], taille[1])
        #resolution(TM, k, u) renvoi le nombre de tours que prend la resolution pour que tout le monde sorte
        temps.append((resolutionSansVideo(TM, k, u))*0.27)
        #ce qui suit sert a visualiser l'avancée du programme dans la compilation
        if((i%10)==0):
            print("itérations n°",i)

    max=np.max(temps)
    min=np.min(temps)
    #On créé un nombre qui est l'intier directement superieur à max_temps
    sup=int(max)+1
    inf=int(min)
    nbValeurs, moy, mediane, quartils, var, ecart = etudeStat(temps)

    plt.figure(1)
    plt.hist(temps, range = (inf, sup), bins = ((sup-inf)), color = 'blue')
    plt.title(f"Temps du dernier sorti d'une piece {taille[0]*0.4, taille[1]*0.4}en m, pour {nbP} personnes initiales, pour k={k} et u={u}, pour {nbSim} simulations")
    plt.xlabel("temps (s)")
    plt.ylabel("nombre de simulations atteigant un temps égal")
    plt.figure(2)
    plt.figtext(0.05, 0.3, f'ETUDE STATISTIQUE \n  \n Nombre de valeurs: {nbValeurs} \n \n Moyenne={moy}s \n  \n Mediane={mediane}s \n  \n Variance={var} \n  \n Ecart Type={ecart}s  \n  \n Premier quartile={quartils[0]}s \n  \n Deuxième quartile={quartils[1]}s \n  \n Troisième quartile={quartils[2]}s' )
    plt.axis("off")
    plt.plot()
    plt.show()

    return temps

"""Fonction renvoyant l'étude statistique complète d'un ensemble de tableaux 
@params:
- tableau un tableau de données

@return:
- Len(tableau) le nombre de valeurs
- moy la moyenne des valeurs
- mediane la médiane des valeurs
- quartils les quartiles
- var la variance des valeurs
- ecart l'écart type des valeurs contenues dans le tableau
"""
def etudeStat(tableau):

    #On défini la moyenne du tableau:
    moy=0
    for i in range(len(tableau)):
        moy=moy+tableau[i]
    moy=moy/len(tableau)
    #On definit la variance
    var=0
    for i in range(len(tableau)):
        var=var + (tableau[i]-moy)**2
    var=var/len(tableau)
    #Puis on retourn l'écart type qui est la racine carrée de la variance
    ecart=np.sqrt(var)    
    #quartils
    quartils=[]
    quartils.append(np.quantile(tableau, .25))
    quartils.append(np.quantile(tableau, .50))
    quartils.append(np.quantile(tableau, .75))
    #mediane
    mediane=np.median(tableau)
    

    return len(tableau), moy, mediane, quartils, var, ecart #retourne, le nb de valeurs, la moyenne, la variance, l'écart type



"""#Affiche une simulation de Npas de k entre kmin et kmax en fonction de mu et d'une pièce de densité et taille donné, Nsim simulations par pas
@params:
- Nb le nombre de personne a placer dans la salle
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- u le mu voulu
- kmin le kappa minimum a considérer
- kmax le kappa maximum a considérer
- Npas le nombre des pas de kappa
- Nsim le nombre de simulations par pas
"""
@timer
def SimulationsK(Nb,taille,u,kmin,kmax,Npas,Nsim):
    Terrains=np.asarray([creerSalle(Nb,taille[0],taille[1]) for i in range(Nsim)])
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
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille} et contenant {Nb} automates, en fonction de k, pour u={u} ({Nsim} simulations par pas, {Npas} pas de k, et k variant de {kmin} a {kmax})")
    plt.errorbar(k, N, yerr=ecart, fmt = 'none', capsize = 10, ecolor = 'red', zorder = 1)
    plt.show()
    plt.figure(figsize=(15,10))


"""Affiche une simulation de Npas de mu (mu allant de 0 a 1) en fonction de k et d'une pièce de densité et taille donné, Nsim simulations par pas
@params:
- Nb le nombre de personne a placer dans la salle
- taille la taille de la pièce (taille est un tableau de type (Lx,Ly))
- k le kappa voulu
- u le mu voulu
- Npas le nombre des pas de mu
- Nsim le nombre de simulations par pas
"""
@timer    
def SimulationsU(Nb,taille,k,Npas,Nsim):
    Terrains=np.asarray([creerSalle(Nb,taille[0],taille[1]) for i in range(Nsim)])
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
