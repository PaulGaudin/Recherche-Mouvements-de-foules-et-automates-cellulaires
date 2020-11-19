import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
from random import uniform

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
    piece=np.eye(Ly+2,Lx+2)
    for i in range(Ly+2):
        for j in range(Lx+2):
            piece[i][j]=0

            if (i==0 or i==Ly+1):
                piece[i][j]=3
            if ((j==0 or j==Lx+1) and i!=Ly+2):
                piece[i][j]=3
            if (i==0):
                if (j==Lx/2 or j==((Lx/2)+1)):
                    piece[0][j]=2
            
    return piece


#Définition du SFF d'une pièce donnée :
def SFF(T):
    dx=0.4
    R=np.copy(T)
    for j in range(1,T[0].size-1):
        for i in range(1,T[0].size-1):
            R[j][i]=max(abs(np.sqrt((((i-0.5)*dx-(((T[0].size-2)/2)-0.5)*dx)**2)+(((j-0.5)*dx)**2))),abs(np.sqrt((((i-0.5)*dx-(((T[0].size-1)/2)-0.5)*dx)**2)+(((j-0.5)*dx)**2))))
            if(i==int(T[0].size/2)):
                R[0][i]=0
            if(i==int((T[0].size/2)-1)):
                R[0][i]=0
    return R


#Fonction permettant de calculer w :
def w(x,y,k,TM,t):
    TS=SFF(TM)
    d=((TM[x][y]!=3 and TM[x][y]!=1) or t==1)
    return np.exp(-k*TS[x][y])*d

#Fonction permettant de calculer le poids selon W et Z(somme des W):
def p(Z,W):
    return (1/Z)*W


#Fonction alternative calculant directement le poids d'une direction a partir des coordonnées de base et de la direction:
def p2(x,y,k,TM,u,v):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1]]
    wt=[]
    for i in range(len(H)):
        if (i==0):
            t=1
        else:
            t=0
        wt.append(w(x+H[i][0],y+H[i][1],k,TM,t))
    
    Z=np.sum(wt)
    
    return p(Z,w(u,v,k,TM,t))

#Fonction permettant d'obtenir le mouvement d'un automate :
def Mouvement(x,y,k,TM):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1]]
    wt=[]
    pt=[]
    for i in range(len(H)): #a optimiser
        if (i==0):
            t=1
        else:
            t=0
        wt.append(w(x+H[i][0],y+H[i][1],k,TM,t))
    
    Z=np.sum(wt)
    for i in range(len(wt)):
        pt.append(p(Z,wt[i]))
        
    A=uniform(0,sum(pt))
    B=0
    for i in range(5):
        B+=pt[i]
        if (A<=B):
            return (x+H[i][0],y+H[i][1])

#Fonction permettant de récuperer tout les mouvements des automates :
def update(TM,k):
    Mouv=np.array([])
    base=np.array([])
    for i in range(TM[0].size):
        for j in range(TM[0].size):
            if (TM[i][j]==1):
                base=np.append(base,(i,j))
                Mouv=np.append(Mouv,Mouvement(i,j,k,TM))
                
    Mouv=Mouv.reshape((int(Mouv.size/2),2))
    base=base.reshape((int(base.size/2),2))
    return Mouv,base

#Fonction permettant si il y a conflit de les résoudre en utilisant la méthode de friction :
def friction(TM,k,u):
    M,B = update(TM,k)
    M=M.astype(np.int64)
    B=B.astype(np.int64)
    for i in range(M.shape[0]):
        for j in range(M.shape[0]):
            if(i!=j and M[i][0]==M[j][0] and M[i][1]==M[j][1]): #A optimiser
                if(np.random.binomial(1,u,size=None)==1):
                    M[i]=B[i].copy()
                    M[j]=B[j].copy()
                else:
                    if(p2(B[i][0],B[i][1],k,TM,M[i][0],M[i][1])>p2(B[j][0],B[j][1],k,TM,M[j][0],M[j][1])):
                        M[j]=B[j].copy()
                    else:
                        M[i]=B[i].copy()
                        
    return M


#Fonction effectuant un déplacement complet de tout les automates en parallèle (méthode de friction): 
def Deplacement(TM,k,u):
    New=friction(TM,k,u)
    Temp=Init(TM.shape[0]-2,TM.shape[1]-2)
    for i in range(TM.shape[0]):
        for j in range(TM.shape[1]):
            for u in range(New.shape[0]):
                if(i==New[u][0] and j==New[u][1]):
                    Temp[i][j]=1
                
                if((i==0 and j==TM.shape[0]/2) or (i==0 and j==(TM.shape[0]/2)-1)):
                    Temp[i][j]=2
    
    return Temp



#Affiche chaque tour jusqu'a ce que tout les automates soient sortis
def resolution(TM,k,u):
    Nb=0
    while((TM==Init(TM.shape[0]-2,TM.shape[1]-2)).all()!=1):
        TM=Deplacement(TM,k,u)
        plotSalle(TM)
        Nb+=1
    return Nb