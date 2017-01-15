#!/usr/bin/python3
# -*- coding: Utf-8 -*
import pygame
import sys
from pygame.locals import *
import time
from f_objects import *
import matplotlib.pyplot as plt
import numpy
import _thread
import datetime

window = GameWindow() # Instanciation de la fenêtre graphique
# On crée des surfaces de projection de vecteurs et de position
vecteurs = pygame.Surface((800,600), flags=SRCALPHA)
position = pygame.Surface((800,600))
pygame.key.set_repeat(500,30)

#######################################
# CONFIGURATION
#######################################

# Date initiale
date = datetime.datetime.strptime("4/01/2017", "%d/%m/%Y")

# Secondes d'attente entre 10 calculs de trajectoires :
delaiAttenteCalcul = 0.05

# Mise à jour graphique toutes les (images)
FrequenceMajGraphique = 200
 
soleil = Astre(
    position=[400.0,300.0],
    mass=1.989e30,
    surfacePosition=position,
    surfaceVecteurs=vecteurs,
    file='sun.gif',
    fixe=True
    )

mercure = Astre(
    position=[400.0,300.000000001+46.001272],
    mass=330.2e21,
    speedx=212328,
    surfacePosition=position,
    surfaceVecteurs=vecteurs,
    file='mercure.gif',
    fixe=False
    )

venus = Astre(
    position=[400.0,300.000000001+107.476259],
    mass=4.8685e24,
    speedx=126936,
    surfacePosition=position,
    surfaceVecteurs=vecteurs,
    file='venus.gif',
    fixe=False
    )

terre = Astre(
    position=[400.0,300.000000001+147.100184],
    mass=5.972e24+7.36e22,
    speedx=109033,
    surfacePosition=position,
    surfaceVecteurs=vecteurs,
    file='terre.gif',
    fixe=False
    )

mars = Astre(
    position=[400.0,300.000000001+206.644545],
    mass=641.85e21,
    speedx=95396,
    surfacePosition=position,
    surfaceVecteurs=vecteurs,
    file='mars.gif',
    fixe=False
    )

"""
lune = Ball(
    position=[400.0,300.000000001+147.45+0.3844],
    mass=7.36e22,
    speedx=112122-3679,
    surfacePosition=position,
    surfaceVecteurs=vecteurs,
    fixe=False
)
"""

# L'astre dont la vitesse sera affichée au graphique
astreGraphique = terre

#######################################
#######################################
#######################################
image = 0
run = False

def changeSpeed(arg):
    global delaiAttenteCalcul
    if delaiAttenteCalcul+arg>0:
        delaiAttenteCalcul += arg
    else:
        delaiAttenteCalcul = 0.00001
def playPause():
    global run
    if run == True:
        run = False
        print("Calcul mis en pause. Appyuez sur espace pour relancer.")
    else:
        run = True
        print("Calcul relancé.")
def process():
    """ Fonction qui calcule la trajectoire des astres à l'heure suivante """
    global objects
    for object in objects:
        object.calculAcceleration()
        object.move()

deltaFPS = 0 # Compteur d'image par seconde
def render():
    """ Fonction qui affiche à l'écran les astres et les vecteurs """
    global image, objects
    # Rendu des vecteurs
    vecteurs.fill((0,0,0,0)) # On efface l'affichage des vecteurs
    for object in objects:
        object.drawVectors()

    window.root.blit(position.convert_alpha(), (0, 0))
    window.root.blit(vecteurs.convert_alpha(), (0, 0))

    # Définition des polices 
    title = pygame.font.SysFont("monospace", 32)
    detail = pygame.font.SysFont("monospace", 20)

    # Rendu des textes
    temps = title.render(" Δt = "+str(int(image/(24)))+"j", 1, (255,255,255))
    window.root.blit(temps.convert_alpha(), (0, 7))

    rendu = detail.render(" Image n°"+str(image), 1, (255,255,255))
    window.root.blit(rendu.convert_alpha(), (0, 530))

    v = detail.render(" Calculs/sec = "+str(deltaFPS), 1, (255,255,255))
    window.root.blit(v.convert_alpha(), (0, 560))

    date1 = detail.render("Date (Terre seulement) :", 1, (255,255,255))
    window.root.blit(date1.convert_alpha(), (500, 7))
    date2 = title.render(date.strftime("%d %b %Y"), 1, (255,255,255))
    window.root.blit(date2.convert_alpha(), (515, 27))

    for object in objects:
        object.blit(window)


def update_line(hl, x, y, image):
    """ Fonction qui met à jour la courbe du graphique avec les nouveaux points """
    global plt
    hl.set_xdata(numpy.append(hl.get_xdata(), x))
    hl.set_ydata(numpy.append(hl.get_ydata(), y))
    plt.draw()
    plt.xlim([min(hl.get_xdata()),max(hl.get_xdata())])
    plt.ylim([min(hl.get_ydata()),max(hl.get_ydata())])

def renderThread():
    """ Process de rendu graphique de la fenêtre pygame """
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playPause()
                if event.key == pygame.K_UP:
                    changeSpeed(-0.0005)
                if event.key == pygame.K_DOWN:
                    changeSpeed(0.0005)
        render()
        pygame.display.flip()
        time.sleep(0.0166667) # 1/60 ----> 60 images/seconde

def everySecondLoop():
    global deltaFPS, image
    oldImg = 0
    while True:
        deltaFPS = image - oldImg
        oldImg = image
        time.sleep(1)

def mainThread():
    """ Process Principal """
    global image, run, date
    while True:
        dix = False
        if image%10==0:
            dix = True
        if run == True:
            image+=1
            process()
            if image%FrequenceMajGraphique==0:
                update_line(hl, int(image/(24)), astreGraphique.getSpeed()/1000, image)
            if dix:
                date = date + datetime.timedelta(hours=10)
        if dix:
            time.sleep(delaiAttenteCalcul)

# Création d'un graphique
plt.title("Vitesse de la Terre (ou Astre défini) en fonction du jour")
plt.xlabel('Temps (jour)')
plt.ylabel('Vitesse (10^3 km/h)')
plt.grid(True)

# On place le premier point pour initialiser le graph
hl, = plt.plot([0],[astreGraphique.getSpeed()/1000], linewidth=1, marker="+")

# On lance les threads principaux et de rendu pygame
_thread.start_new_thread(mainThread, ())
_thread.start_new_thread(renderThread, ())
_thread.start_new_thread(everySecondLoop, ())

# On en dernier sur le thread "__main__" le rendu du graphique
plt.legend()
plt.show()