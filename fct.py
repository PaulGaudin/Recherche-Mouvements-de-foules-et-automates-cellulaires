import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
import timeit
from random import uniform,randint
from matplotlib import animation, rc

"""Affiche la salle (matrice carré) S
@params:
- S la pièce que l'on veut afficher
"""
def plotSalle(S):
    cmap = matplotlib.colors.ListedColormap(['white','black',"red", "gray", "yellow"])
    boundaries = [-0.2, 0.5, 1.5, 2.5, 3.5, 4.5]
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)
    plt.figure(figsize=(np.shape(S)[1]/2,np.shape(S)[0]/2))
    plt.pcolor(S,cmap=cmap,norm=norm)
    plt.show()

"""Creation d'une pièce remplie d'automate
@params:
- densité la densité de population voulue
- Ly la taille verticale de la pièce
- Lx la taille horizontale de la pièce

@return:
- La salle de dimensions Lx*Ly, contenant une densité d de population a l'intérieur
"""
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


"""Afficher le SFF de la salle
@params:
- salle la salle dont on veut calculer le SFF
"""
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


"""Initialisation d'une pièce vide
@params:
- Ly la taille verticale de la pièce
- Lx la taille horizontale de la pièce

@return:
- Une pièce de dimensions Lx*Ly
"""
def Init(Ly,Lx):
    piece=np.zeros(shape=(Ly,Lx))
    ligneMur = [3]*(Lx+2)
    colonneMur = [3]*Ly
    piece = np.column_stack((colonneMur, piece, colonneMur))
    piece = np.vstack((ligneMur, piece, ligneMur))
    piece[0,int(Lx/2)]=piece[0,int((Lx/2)+1)]=2
            
    return piece


"""Définition du SFF d'une pièce donnée :
@params:
- T la salle dont on veut calculer le SFF

@return:
- Le SFF
"""
def SFF(T):
    dx=0.4
    R=np.copy(T)
    R=np.array([[max(abs(np.sqrt((((i-0.5)*dx-(((T[0].size-2)/2)-0.5)*dx)**2)+(((j-0.5)*dx)**2))),abs(np.sqrt((((i-0.5)*dx-(((T[0].size-1)/2)-0.5)*dx)**2)+(((j-0.5)*dx)**2)))) for i in range(1,np.shape(T)[1]-1)] for j in range(1,np.shape(T)[0]-1)])
    ligneMur = [0]*np.shape(T)[1]
    colonneMur = [0]*(np.shape(T)[0]-2)
    R = np.column_stack((colonneMur, R, colonneMur))
    R = np.vstack((ligneMur, R, ligneMur))
    return R


"""Fonction permettant de calculer w le poids associé a un mouvement
@params:
- x la coordonnée en x de l'agent
- y la coordonnée en y de l'agent
- k le kappa voulu
- TM la salle considérée
- TS le SFF de la salle considérée
- t un paramètre indiquant si on calcule le poids d'aucun déplacement (du déplacement [0,0]) ou pas

@return:
- le poids du déplacement
"""
def w(x,y,k,TM,TS,t):
    d=((TM[x,y]!=3 and TM[x,y]!=1) or t==1)
    return np.exp(-k*TS[x,y])*d

"""Fonction permettant de calculer la normalisation de w (afin d'en faire une probabilité d'événement)
@params:
- Z la somme de tout les poids
- W le poids que l'on veut normaliser

@return:
- le poids normalisé
"""
def p(Z,W):
    return (1/Z)*W


"""Fonction alternative calculant directement le poids d'une direction a partir des coordonnées de base et de la direction:
@params:
- x la coordonnée en x de l'agent
- y la coordonnée en y de l'agent
- k le kappa voulu
- TM la salle considérée
- TS le SFF de la salle considérée
- u la coordonnée  en x de déplacement de l'agent
- u la coordonnée  en y de déplacement de l'agent
"""
def p2(x,y,k,TM,TS,u,v):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1],[1,1],[-1,1],[-1,-1],[1,-1]]
    wt=[]
    for i in range(len(H)):
        if (i==0):
            t=1
        else:
            t=0
        wt.append(w(x+H[i][0],y+H[i][1],k,TM,TS,t))
    
    Z=np.sum(wt)
    
    return p(Z,w(u,v,k,TM,TS,t))

"""#Fonction permettant d'obtenir le mouvement d'un automate :
@params:
- x la coordonnée en x de l'agent
- y la coordonnée en y de l'agent
- k le kappa voulu
- TM la salle considérée
- TS le SFF de la salle considérée
"""
def Mouvement(x,y,k,TM,TS):
    H=[[0,0],[-1,0],[1,0],[0,-1],[0,1],[1,1],[-1,1],[-1,-1],[1,-1]]
    wt=[]
    pt=[]
    for i in range(len(H)):
        if (i==0):
            t=1
        else:
            t=0
        wt.append(w(x+H[i][0],y+H[i][1],k,TM,TS,t))
    
    Z=np.sum(wt)
    pt=[p(Z,i) for i in wt]
        
    A=uniform(0,sum(pt))
    B=0
    for i in range(len(H)):
        B+=pt[i]
        if (A<=B):
            return [x+H[i][0],y+H[i][1]]

"""#Fonction permettant de récuperer tout les mouvements des automates :
@params:
- x la coordonnée en x de l'agent
- y la coordonnée en y de l'agent
- k le kappa voulu
- TM la salle considérée
- TS le SFF de la salle considérée
- u la coordonnée  en x de déplacement de l'agent
- u la coordonnée  en y de déplacement de l'agent
"""
def update(TM,TS,k):
    x,y = np.where(TM==1)
    base=np.vstack([x,y]).T
    Mouv=np.array([Mouvement(x[i],y[i],k,TM,TS) for i in range(x.size)])
    return Mouv,base

"""#Fonction permettant si il y a conflit de les résoudre en utilisant la méthode de friction :
@params:
- TM la pièce considérée
-  k le kappa voulu
- u le mu voulu

@return:
- Nb le nombre de tour mis pour purger la salle
"""
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

#Un timer
def timer(function):
    def inner(*args, **kwargs):
        start = timeit.default_timer()
        result = function(*args, **kwargs)
        end = timeit.default_timer()
        time = end - start
        print(f"Function {function.__name__} executed in {time} seconds.")
        return result
        
    return inner