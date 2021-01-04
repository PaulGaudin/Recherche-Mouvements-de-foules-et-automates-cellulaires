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


    #Affiche chaque tour jusqu'a ce que tout les automates soient sortis
def resolutionSansVideo(TM,k,u):
    evol=[TM]
    Nb=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1):
        TM=Deplacement(TM,k,u)
        evol.append(TM)
        Nb+=1
    return Nb

#fct qui fait tourner un certain nbr de fois resolution 1 pour une piece creée avec creerSalle mais qui ne l'affiche pas
def faisTourner(nbP, taille, k, u, nbSim ):
    temps=[]  
    for i in range(nbSim):
        TM=creerSalle2(nbP, taille[0], taille[1])
        #resolution(TM, k, u) renvoi le nombre de tours que prend la resolution pour que tout le monde sorte
        temps.append((resolutionSansVideo(TM, k, u))*0.27)
        #ce qui suit sert a visualiser l'avancée du programme dans la compilation
        if((i%10)==0):
            print("itérations n°",i)

    max=np.max(temps)
    min=np.min(temps)
    #On creer un nombre qui est l'intier directeent superieur à max_temps
    sup=int(max)+1
    inf=int(min)
    nbValeurs, moy, mediane, quartils, var, ecart = etudeStat(temps)

    plt.figure(1)
    plt.hist(temps, range = (inf, sup), bins = ((sup-inf)), color = 'blue')
    plt.title(f"Temps du dernier sorti d'une piece {taille[0]*0.4, taille[1]*0.4}en m, pour {nbP} personnes initiales, pour k={k} et u={u}, pour {nbSim} simulations")
    plt.xlabel("temps en secondes")
    plt.ylabel("nombre de simulation atteigant le même temps de sorti")
    plt.figure(2)
    plt.figtext(0.05, 0.3, f'ETUDE STATISTIQUE \n  \n Nombre de valeurs: {nbValeurs} \n \n Moyenne={moy}s \n  \n Mediane={mediane}s \n  \n Variance={var} \n  \n Ecart Type={ecart}s  \n  \n Premier quartils={quartils[0]}s \n  \n Deuxième quartils={quartils[1]}s \n  \n Troisième quartils={quartils[2]}s' )
    plt.axis("off")
    plt.plot()
    plt.show()

    return temps


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