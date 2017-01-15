#!/usr/bin/python3
# -*- coding: Utf-8 -*
import pygame
from pygame.locals import *
import time
import math
import sys
import random

objects=[]

def drawVector(surface, origin, vector, color=(255,0,0)):
    """ Fonction qui permet de représenter graphiquement un vecteur """
    pygame.draw.line(surface, color, (origin[0], origin[1]),(origin[0]+vector.x, origin[1]+vector.y))
    subtrait1 = vector.rotate(150)
    subtrait1 = subtrait1.normalize() * 8
    pygame.draw.line(surface, color, (origin[0]+vector.x, origin[1]+vector.y),(origin[0]+vector.x+subtrait1.x, origin[1]+vector.y+subtrait1.y))
    subtrait2 = vector.rotate(-150)
    subtrait2 = subtrait2.normalize() * 8
    pygame.draw.line(surface, color, (origin[0]+vector.x, origin[1]+vector.y),(origin[0]+vector.x+subtrait2.x, origin[1]+vector.y+subtrait2.y))

class GameWindow(object):
    """ Game window object """

    def __init__(self):
        # Starting PyGame

        pygame.init()
        pygame.key.set_repeat(1, 10)
        pygame.display.set_caption("Forces", "")
        self.root = pygame.display.set_mode((800, 600))    

class Astre(object):
    """ Objet Astre """

    def __init__(self, surfaceVecteurs, surfacePosition, position=[20.0,20.0], orientation=0.0, speed=1.0, mass=3e7, speedx=1000, speedy=1000,file='red-circle.gif', fixe=False):
        self.fixe = fixe
        # Self.position is in pixels 
        self.position, self.orientation, self.speed, self.mass = position, orientation, speed, mass
        objects.append(self)
        self.id = random.randint(0, 1e6)

        # Loading the file surface
        self.file = file
        self.surface = pygame.image.load(self.file).convert_alpha()
        self.surfaceVecteurs = surfaceVecteurs # Surface sur laquelle sera projetée les tracés des vecteurs d'accélération.
        self.surfacePosition = surfacePosition

        # Vectors
        # La terre à une vitesse de 31,145 km/s au périhélie soit 112122km/h
        self.vitesse = pygame.math.Vector2(speedx,speedy) # vitesse en km/h
        self.acceleration = pygame.math.Vector2(0,0.000000001)
        self.calculAcceleration()

    ### ACCESSEURS ET MUTATEURS ###
    def getID(self):
        return self.id
    def getSpeed(self):
        return self.vitesse.length()
    def getPosition(self):
        return self.position
    def getMass(self):
        return self.mass
    def isFixe(self):
        return self.fixe    
    def blit(self, window):
        """ Méthode de rendu de l'image dans la fenêtre graphique """
        window.root.blit(self.surface, (self.position[0]-8, self.position[1]-8))
        
    def calculAcceleration(self):
        """ Méthode qui calcule le vecteur final d'accélération en fonction des différents corps attracteurs """
        if not self.fixe:
            
            # On part d'un vecteur d'accélération nul :
            force = pygame.math.Vector2(0,0)
            
            for object in objects: # Pour chaque objet présent dans la scène, on va déterminer l'accélération qu'il provoque sur notre objet
                if object.getID() != self.id: # On teste s'il ne s'agit pas de lui même
                    
                    # On calcule les coordonnées du vecteur à partir des coordonnées des objets
                    deltaX = object.getPosition()[0]-self.position[0]
                    deltaY = object.getPosition()[1]-self.position[1]
                    objectAttraction = pygame.math.Vector2(deltaX, deltaY) # Création du vecteur
                    
                    # On calcule la norme de l'attraction suivant la loi de gravitation de Newton
                    norm = 6.67384e-11*((self.mass*object.getMass())/(objectAttraction.length()*1e9)**2) # 1 pixel = 1 million de km = 1.0e9 mètres           

                    # On applique la norme de la force (en N) à notre vecteur "attraction"
                    objectAttraction = objectAttraction.normalize() * norm          
                        
                    # On ajoute l'accélération crée par l'objet au vecteur principal d'accélération
                    force+=objectAttraction 
           
            
            # On applique l'accélération au vecteur vitesse par addition
            # p = m * g <=> g = p / m
            self.acceleration = pygame.math.Vector2(1,1)
            if force.x*force.y != 0:
                self.acceleration = pygame.math.Vector2(force.x/self.mass, force.y/self.mass) * 12960# m.s^-2 --> km.h^-2
            # On applique le vecteur accélération au vecteur vitesse
            self.vitesse += self.acceleration

        
    def move(self):
        """ Méthode qui applique le vecteur vitesse à la position """
        if not self.fixe:
            self.position = ( self.position[0]+self.vitesse.x*1e-6 , self.position[1]+self.vitesse.y*1e-6 ) # km/h --> pixels
            self.surfacePosition.set_at((int(self.position[0]), int(self.position[1])), Color(150, 150, 150, 255))

    def drawVectors(self):
        drawVector(self.surfaceVecteurs, self.position, self.vitesse*1e-3, (0,255,0)) # Vitesse
        drawVector(self.surfaceVecteurs, self.position, self.acceleration*1e0, color=(255,0,0)) # Forces