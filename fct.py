import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
import timeit
from random import uniform
from matplotlib import animation, rc
from random import randint


def plotSalle(S):
    cmap = matplotlib.colors.ListedColormap(['white','black',"red", "gray", "yellow"])
    boundaries = [-0.2, 0.5, 1.5, 2.5, 3.5, 4.5]
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)
    plt.figure(figsize=(np.shape(S)[1]/2,np.shape(S)[0]/2))
    plt.pcolor(S,cmap=cmap,norm=norm)
    plt.show()

#Creation d'une pièce remplit d'automate
def creerSalle(densite,Ly,Lx):
    ligneMur = [3]*(Lx+2)
    colonneMur = [3]*Ly
    #rempli la salle avec des gens aleatoirement placés
    salle=np.random.binomial(1, densite, size=(Ly,Lx))
    
    #créer des murs en gris
    salle = np.column_stack((colonneMur, salle, colonneMur))
    salle = np.vstack((ligneMur, salle, ligneMur))

    #créer une porte representée en rouge
    salle[0,int(Lx/2)]=2
    salle[0,int((Lx-1)/2)]=2
    return salle


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


#Initialisation de la pièce :
def Init(Ly,Lx):
    piece=np.zeros(shape=(Ly,Lx))
    ligneMur = [3]*(Lx+2)
    colonneMur = [3]*Ly
    piece = np.column_stack((colonneMur, piece, colonneMur))
    piece = np.vstack((ligneMur, piece, ligneMur))
    piece[0,int(Lx/2)]=piece[0,int((Lx/2)+1)]=2
            
    return piece


#Définition du SFF d'une pièce donnée :
def SFF(T):
    dx=0.4
    R=np.copy(T)
    R=np.array([[max(abs(np.sqrt((((i-0.5)*dx-(((T[0].size-2)/2)-0.5)*dx)**2)+(((j-0.5)*dx)**2))),abs(np.sqrt((((i-0.5)*dx-(((T[0].size-1)/2)-0.5)*dx)**2)+(((j-0.5)*dx)**2)))) for i in range(1,np.shape(T)[1]-1)] for j in range(1,np.shape(T)[0]-1)])
    ligneMur = [0]*np.shape(T)[1]
    colonneMur = [0]*(np.shape(T)[0]-2)
    R = np.column_stack((colonneMur, R, colonneMur))
    R = np.vstack((ligneMur, R, ligneMur))
    return R


#Fonction permettant de calculer w :
def w(x,y,k,TM,TS,t):
    d=((TM[x,y]!=3 and TM[x,y]!=1) or t==1)
    return np.exp(-k*TS[x,y])*d

#Fonction permettant de calculer le poids selon W et Z(somme des W):
def p(Z,W):
    return (1/Z)*W


#Fonction alternative calculant directement le poids d'une direction a partir des coordonnées de base et de la direction:
def p2(x,y,k,TM,TS,u,v):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1]]
    wt=[]
    #wt=[w(x+H[i][0],y+H[i][1],k,TM,t) for i in range(len(H))]
    for i in range(len(H)):
        if (i==0):
            t=1
        else:
            t=0
        wt.append(w(x+H[i][0],y+H[i][1],k,TM,TS,t))
    
    Z=np.sum(wt)
    
    return p(Z,w(u,v,k,TM,TS,t))

#Fonction permettant d'obtenir le mouvement d'un automate :
def Mouvement(x,y,k,TM,TS):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1]]
    wt=[]
    pt=[]
    for i in range(len(H)): #a optimiser
        if (i==0):
            t=1
        else:
            t=0
        wt.append(w(x+H[i][0],y+H[i][1],k,TM,TS,t))
    
    Z=np.sum(wt)
    pt=[p(Z,i) for i in wt]
        
    A=uniform(0,sum(pt))
    B=0
    for i in range(5):
        B+=pt[i]
        if (A<=B):
            return [x+H[i][0],y+H[i][1]]

#Fonction permettant de récuperer tout les mouvements des automates :
def update(TM,TS,k):
    x,y = np.where(TM==1)
    base=np.vstack([x,y]).T
    Mouv=np.array([Mouvement(x[i],y[i],k,TM,TS) for i in range(x.size)])
    return Mouv,base

#Fonction permettant si il y a conflit de les résoudre en utilisant la méthode de friction :
def friction(TM,k,u):
    TS=SFF(TM)
    M,B = update(TM,TS,k)
    M=M.astype(np.int64)
    B=B.astype(np.int64)
    unique,indices,count=np.unique(M,return_inverse=True,return_counts=True,axis=0)
    if(not (count==np.ones(count.size)).all()):
        I=np.where(count>1)[0]
        for i in I:
            J=np.where(indices==i)[0]
            for j in range(J.size-1):
                if(np.random.binomial(1,u,size=None)==1):
                    M[J[j]]=B[J[j]].copy()
                    M[J[j+1]]=B[J[j+1]].copy()
                elif(p2(B[J[j],0],B[J[j],1],k,TM,TS,M[J[j],0],M[J[j],1])>p2(B[J[j+1],0],B[J[j+1],1],k,TM,TS,M[J[j+1],0],M[J[j+1],1])):
                    M[J[j+1]]=B[J[j+1]].copy()
                else:
                    M[J[j]]=B[J[j]].copy()               
    return M


#Fonction effectuant un déplacement complet de tout les automates en parallèle (méthode de friction): 
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

#Un timer
def timer(function):
    def inner(*args, **kwargs):
        start = timeit.default_timer()
        result = function(*args, **kwargs)
        end = timeit.default_timer()
        time = end - start
        # print(f"Executed in {round(time,3) if time > 0.001 else 'less than 0.001'} seconds.")
        print(f"Function {function.__name__} executed in {time} seconds.")
        return result
        
    return inner

#Effectue une résolution complète et renvoie le nombre de tour necessaires
@timer
def resolv(TM,k,u):
    Nb=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1):
        TM=Deplacement(TM,k,u)
        Nb+=1
    return Nb


#Affiche chaque tour jusqu'a ce que tout les automates soient sortis
def resolution(TM,k,u):
    evol=[TM]
    Nb=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1):
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

    #video = HTML(ani.to_html5_video())
    plt.show()
    plt.clf()
    return Nb


#Fonction effectuant un déplacement complet de tout les automates en parallèle (méthode de friction): 
def Deplacement2(TM,k,u):
    New=friction(TM,k,u)
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


def resolution2(TM,k,u):
    evol=[TM]
    Nb=0
    X=np.sum(TM==1)*2
    NStop=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1 and NStop<X):
        TM,n=Deplacement2(TM,k,u)
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
        
@timer
def resolv2(TM,k,u):
    Nb=0
    X=np.sum(TM==1)
    NStop=0
    Na=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1 and NStop<(X*3)):
        TM,n=Deplacement2(TM,k,u)
        NStop+=n
        if(NStop==(X*2)):
            Na=Nb
        Nb+=1
    return Nb-Na

@timer    
def SimulationsU(d,taille,k,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    u=np.linspace(0,1,Npas)
    Ntours=np.asarray([[resolv2(Terrain,k,ut) for Terrain in Terrains] for ut in u])
    N=np.zeros(Npas)
    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size

    fig = plt.figure(figsize=(15,10))
    plt.plot(u,N)
    plt.xlabel("U")
    plt.ylabel("Nombre de tours")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille} et densité {d}, en fonction de u (coeff de friction), pour k={k} ({Nsim} simulations par pas, {Npas} pas de u)")
    plt.show()


@timer
def SimulationsK(d,taille,u,kmin,kmax,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    k=np.linspace(kmin,kmax,Npas)
    Ntours=np.asarray([[resolv2(Terrain,kt,u) for Terrain in Terrains] for kt in k])
    N=np.zeros(Npas)
    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size

    fig = plt.figure(figsize=(15,10))
    plt.plot(k,N)
    plt.xlabel("k")
    plt.ylabel("Nombre de tours")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille} et densité {d}, en fonction de k, pour u={u} ({Nsim} simulations par pas, {Npas} pas de k, et k variant de {kmin} a {kmax})")
    plt.show()



@timer    
def SimulationsUR(d,taille,k,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    u=np.linspace(0,1,Npas)
    Ntours=np.asarray([[resolv2(Terrain,k,ut) for Terrain in Terrains] for ut in u])
    N=np.zeros(Npas)
    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size

    fig = plt.figure(figsize=(15,10))
    plt.plot(u,N*0.27)
    plt.xlabel("U")
    plt.ylabel("Temps (en s)")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille[0]*0.4,taille[1]*0.4} mètres et densité {d}, en fonction de u (coeff de friction), pour k={k} ({Nsim} simulations par pas, {Npas} pas de u)")
    plt.show()


@timer
def SimulationsKR(d,taille,u,kmin,kmax,Npas,Nsim):
    Terrains=np.asarray([creerSalle(d,taille[0],taille[1]) for i in range(Nsim)])
    k=np.linspace(kmin,kmax,Npas)
    Ntours=np.asarray([[resolv2(Terrain,kt,u) for Terrain in Terrains] for kt in k])
    N=np.zeros(Npas)
    for i in range(Npas):
        N[i]=Ntours[i].sum()/Ntours[i].size

    fig = plt.figure(figsize=(15,10))
    plt.plot(k,N*0.27)
    plt.xlabel("k")
    plt.ylabel("Temps (en s)")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille[0]*0.4,taille[1]*0.4} mètres et densité {d}, en fonction de k, pour u={u} ({Nsim} simulations par pas, {Npas} pas de k, et k variant de {kmin} a {kmax})")
    plt.show()