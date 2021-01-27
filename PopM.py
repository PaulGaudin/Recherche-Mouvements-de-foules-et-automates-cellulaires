from fct import w,p,SFF,Init,timer
import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
import timeit
from random import uniform
from matplotlib import animation, rc
from random import randint
from Graphes import ecartType

def creerSalle(densite,ProportionPop,Ly,Lx):
    ligneMur = [3]*(Ly+2)
    colonneMur = [3]*Lx
    #rempli la salle avec des gens aleatoirement placés
    salle=np.random.binomial(1, densite, size=(Ly,Lx))
    

    
    #créer des murs en gris
    salle = np.column_stack((colonneMur, salle, colonneMur))
    salle = np.vstack((ligneMur, salle, ligneMur))

    x,y=np.where(salle==1)
    salle[x,y]=1+np.random.binomial(1, ProportionPop, size=x.size)*3

    #créer une porte representée en rouge
    salle[0,int(Lx/2)]=2
    salle[0,int((Lx+2)/2)]=2
    return salle

#Fonction alternative calculant directement le poids d'une direction a partir des coordonnées de base et de la direction:
def p2(x,y,k1,k2,TM,TS,u,v):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1]]
    wt=[]
    k=0
    if(TM[x,y]==1):
        k=k1
    else:
        k=k2

    for i in range(len(H)):
        if (i==0):
            t=1
        else:
            t=0
        wt.append(w(x+H[i][0],y+H[i][1],k,TM,TS,t))
    
    Z=np.sum(wt)
    
    return p(Z,w(u,v,k,TM,TS,t))

#Fonction permettant d'obtenir le mouvement d'un automate :
def Mouvement(x,y,k1,k2,TM,TS):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1]]
    wt=[]
    pt=[]
    k=0
    if(TM[x,y]==1):
        k=k1
    else:
        k=k2

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
            return [x+H[i][0],y+H[i][1],TM[x,y]]


def update(TM,TS,k1,k2):
    x,y = np.concatenate((np.where(TM==1),np.where(TM==4)),axis=1)
    k=TM[x,y]
    base=np.vstack([x,y,k]).T
    Mouv=np.array([Mouvement(x[i],y[i],k1,k2,TM,TS) for i in range(x.size)])
    return Mouv,base


#Fonction permettant si il y a conflit de les résoudre en utilisant la méthode de friction :
def friction(TM,k1,k2,u):
    TS=SFF(TM)
    M,B = update(TM,TS,k1,k2)
    Mt=np.vstack([M.T,np.arange(np.shape(M)[0])]).T
    Mt=Mt[np.lexsort(([Mt[:, i] for i in range(Mt.shape[1]-1, -1, -1)]))]
    C=B.copy()
    Ind=Mt[:,3:4].T
    Ind=Ind.astype(np.int64)
    B=C[Ind[0]]
    M=Mt[:,0:3]
    M1=M[:,0:2]
    M=M.astype(np.int64)
    B=B.astype(np.int64)
    unique,indices,count=np.unique(M1,return_inverse=True,return_counts=True,axis=0)
    if(not (count==np.ones(count.size)).all()):
        I=np.where(count>1)[0]
        for i in I:
            J=np.where(indices==i)[0]
            for j in range(J.size-1):
                if(np.random.binomial(1,u,size=None)==1):
                    M[J[j]]=B[J[j]].copy()
                    M[J[j+1]]=B[J[j+1]].copy()
                elif(p2(B[J[j],0],B[J[j],1],k1,k2,TM,TS,M[J[j],0],M[J[j],1])>p2(B[J[j+1],0],B[J[j+1],1],k1,k2,TM,TS,M[J[j+1],0],M[J[j+1],1])):
                    M[J[j+1]]=B[J[j+1]].copy()
                else:
                    M[J[j]]=B[J[j]].copy()
    return M


def Deplacement(TM,k1,k2,Ppop,u):
    New=friction(TM,k1,k2,u)
    Temp=Init(TM.shape[0]-2,TM.shape[1]-2)


    if(np.shape(New)[0]==0):
        return Temp
        
    else:
        x,y,K=New.transpose()
        Temp[x,y]=K
        Temp[0,int(TM.shape[0]/2)]=Temp[0,int((TM.shape[1]/2)-1)]=2
        k=0
        #On veut maintenant reinjecter le nombre de personnes sortantes dans Temp vers le fond
        #On creer un espace de coordonées où reinjecter les personnes = 2 bandes au fond de la salle
        x_reinjection_min=(len(TM)-1)-3
        x_reinjection_max=(len(TM)-1)-1

        y_reinjection_min=1
        y_reinjection_max=len(TM-1)-2

        while((np.sum(TM==0))!=(np.sum(Temp==0))): 


            #Pour chaque personne a reinjectée, on choisit des coordonées au hasard dans la rectangle de respawn
            new_x=new_y=0
            new_x=randint(x_reinjection_min, x_reinjection_max)
            new_y=randint(y_reinjection_min, y_reinjection_max)

            while(Temp[new_x,new_y]!=0):
                new_x=randint(x_reinjection_min, x_reinjection_max)
                new_y=randint(y_reinjection_min, y_reinjection_max)
            
            Temp[new_x,new_y]=1+np.random.binomial(1, Ppop, size=None)*3
            k+=1
    
    return Temp,k

def resolution(d,taille,Ppop,k1,k2,u):
    TM=creerSalle(d,Ppop,taille[0],taille[1])
    evol=[TM]
    Nb=0
    X=(np.sum(TM==1)+np.sum(TM==4))*2
    NStop=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1 and NStop<X):
        TM,n=Deplacement(TM,k1,k2,Ppop,u)
        NStop+=n
        evol.append(TM)
        Nb+=1

    cmap = matplotlib.colors.ListedColormap(['white','black',"red", "gray", "blue"])
    boundaries = [-0.2, 0.5, 1.5, 2.5, 3.5, 4.5]
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)

    fig, ax = plt.subplots(figsize=(5,5))
    cax = ax.pcolormesh(np.array([[]]),cmap=cmap,norm=norm)

    def init():
        cax = ax.pcolormesh(evol[0],cmap=cmap,norm=norm)
        return cax

    def animate(i):
        cax = ax.pcolormesh(evol[i],cmap=cmap,norm=norm)
        
        ax.set_title(f"Tour numéro {i}, il reste {np.sum(evol[i]==1)} Automates 1 et {np.sum(evol[i]==4)} Automates 2")
        return cax

    ani = animation.FuncAnimation(fig, animate, init_func=init, frames=Nb, interval=200, blit=False)

    #video = HTML(ani.to_html5_video())
    plt.show()
    plt.clf()
    return Nb
        
@timer
def resolv(d,taille,Ppop,k1,k2,u):
    TM=creerSalle(d,Ppop,taille[0],taille[1])
    Nb=0
    X=np.sum(TM==1)+np.sum(TM==4)
    NStop=0
    Na=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1 and NStop<(X*3)):
        TM,n=Deplacement(TM,k1,k2,Ppop,u)
        NStop+=n
        if(NStop==(X*2)):
            Na=Nb
        Nb+=1
    return Nb-Na


def SimulationsPpop(d,taille,u,k1,k2,Npas,Nsim):
    p=np.linspace(0,1,Npas)
    #Terrains=np.asarray([creerSalle(d,pt,taille[0],taille[1]) for pt in p])
    Ntours=np.asarray([[resolv(d,taille,pt,k1,k2,u) for i in range(Nsim)] for pt in p])
    print('c')
    N=np.zeros(Npas)
    ecart=np.zeros(Npas)

    for i in range(Npas):
        print('a')
        N[i]=Ntours[i].sum()/Ntours[i].size
        ecart[i]=ecartType(Ntours[i])

    print('b')
    fig = plt.figure(figsize=(15,10))
    plt.plot(p,N)
    plt.xlabel("Proportion de population (0 équivaut a que une population 1 et 1 équivaut a que une population 2)")
    plt.ylabel("Nombre de tours")
    plt.title(f"Nombre de tour mis pour purger une piece de taille {taille} et densité {d}, En fonction de la proportion de population (Pop 1 de k={k1}, Pop 2 de k={k2})")
    plt.errorbar(p, N, yerr=ecart, fmt = 'none', capsize = 10, ecolor = 'red', zorder = 1)
    plt.show()
    return Ntours
