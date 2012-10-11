#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------#
# RasPyPlayer.py - Movies player for Raspberry Pi
#-------------------------------------------------------------------------#
VERSION = "0.1-dev"
#-------------------------------------------------------------------------#
# Auteur : Julien Pecqueur (JPEC)
# Email : jpec@julienpecqueur.net
# Site : http://julienpecqueur.com
# Sources : https://github.com/jpec/RasPyPlayer
# Bugs : https://github.com/jpec/RasPyPlayer/issues
# License :
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------#

#-------------------------------------------------------------------------#
# IMPORTATION DES MODULES                                                 #
#-------------------------------------------------------------------------#
import os
import tkinter
import sqlite3

#-------------------------------------------------------------------------#
# PARAMETRAGE PROGRAMME                                                   #
#-------------------------------------------------------------------------#
PATH="/home/pi"
PATH="D:/Mes Documents/Vidéos Delivery"
OMXCMD="lxterminal --command \"omxplayer -o hdmi '{0}'\""
EXTENSIONS=[".avi", ".mpg", ".mp4", ".wmv"]
DB="RaspPyPlayer.sqlite3"
DBCREATE = "CREATE TABLE files (file, path)"
DBADD = "INSERT INTO files VALUES (?, ?)"
DBDROP = "DROP TABLE files"
DBALL = "SELECT * FROM files"
DEBUG=1

#-------------------------------------------------------------------------#
# DEFINITION DES CLASSES                                                  #
#-------------------------------------------------------------------------#
class Player(object):
    def __init__(self, path, db):
        """Constructeur de la classe Player"""
        self.path = path
        self.db = db
        self.files = {}
        self.conDB = False
        self.curDB = False
        self.topDB = False
        self.creerGui()
        self.openDB()
        self.listFiles()
        self.displayFiles()

    def openDB(self):
        """Ouvre la base de donnée, la créé le cas échéant"""
        sql = False
        bind = False
        if os.path.isfile(self.db):
            self.topDB = True
        # Ouverture base de donnée :
        self.conDB = sqlite3.connect(self.db)
        self.curDB = self.conDB.cursor()

    def initDB(self):
        """Initialisation de la base de données"""
        if DEBUG:
            print("Initilisation de la base de données")
        if self.topDB:
            self.execDB(DBDROP, False)
        self.execDB(DBCREATE, False)
        self.topDB = True

    def closeDB(self):
        """Ferme la base de données"""
        self.curDB.close()
        self.conDB.close()

    def execDB(self, sql, bind):
        """Exécute une requête dans la base de données"""
        if sql:
            if bind:
                if DEBUG:
                    print(DBADD, sql, bind)
                self.curDB.execute(sql, bind)
            else:
                self.curDB.execute(sql)
            self.conDB.commit() 

    def refreshBase(self):
        """Rafraîchi la base de données"""
        if not self.topDB:
            self.initDB()
        self.scanFiles(self.path)
        self.listFiles()

    def scanFiles(self, path):
        """Scan les répertoires et alimente la base de données"""
        if DEBUG:
            print("Scanning : "+path)
        for file in os.listdir(path):
            filepath = path+"/"+file
            if len(file) > 4 and file[-4: len(file)] in EXTENSIONS:
                # Si c'est un fichier vidéo alors on l'ajoute
                self.execDB(DBADD, (os.path.basename(file), filepath))
            elif os.path.isdir(filepath):
                # Si c'est un répertoire alors on le scanne
                self.scanFiles(filepath)

    def listFiles(self):
        """Liste tous les fichiers présents dans la base"""
        if not self.topDB:
            self.initDB()
        if DEBUG:
            print("Listing :")
        self.curDB.execute(DBALL)
        for file, path in self.curDB:
            if DEBUG:
                print(file, path)
            self.files[file] = path

    def playFile(self, file):
        """Joue le fichier passé en paramètre"""
        if DEBUG:
            print(OMXCMD.format(file))
        os.system(OMXCMD.format(file))

    def displayFiles(self):
        """Affiche la liste des fichiers"""
        for file, path in self.files.items():
            if DEBUG:
                print(file)
            self.w_files.insert(tkinter.END, file)
            
    def refreshFiles(self):
        """Rafraichit la liste des fichiers"""
        self.files = {}
        if self.w_files.size() > 0:
            self.w_files.delete(0, tkinter.END)
        self.refreshBase()
        self.displayFiles()
        
    def playSelection(self):
        """Lire le fichier sélectionné"""
        sel = self.w_files.curselection()
        for i in sel:
            f = self.w_files.get(i)
            self.playFile(self.files[f])
        
    def creerGui(self):
        """Construction de la fenêtre"""
        self.root = tkinter.Tk()
        self.root.title("RasPyPlayer")
        # Centrage fenêtre
        w = 800
        h = 600
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	# Zone nom répertoire
        self.topframe = tkinter.Frame(self.root, borderwidth=2)
        self.topframe.pack({"side": "top"})
        # Label mode
        self.w_label = tkinter.Label(self.topframe, text=self.path)
        self.w_label.grid(row=1, column=0, padx=2, pady=2)        
        # Liste des fichiers
        self.w_files = tkinter.Listbox(self.root)
        self.w_files.pack(fill=tkinter.BOTH, expand=1)
        # Groupe boutons
        self.botframe = tkinter.Frame(self.root, borderwidth=2)
        self.botframe.pack({"side": "left"})
        # Bouton Refresh
        self.w_scan = tkinter.Button(self.botframe,
                                     text="Scanner les médias",
                                     command=self.refreshFiles
                                     )
        self.w_scan.grid(row=1, column=0, padx=2, pady=2)
        # Bouton Play
        self.w_play = tkinter.Button(self.botframe,
                                     text="Lire la vidéo",
                                     command=self.playSelection
                                     )
        self.w_play.grid(row=1, column=1, padx=2, pady=2)        
        # Bouton Help
        self.w_help = tkinter.Button(self.botframe,
                                     text="Aide",
                                     command=self.displayHelp
                                     )
        self.w_help.grid(row=1, column=2, padx=2, pady=2)
        # Bouton Quit
        self.w_quit = tkinter.Button(self.botframe,
                                     text="Quitter",
                                     command=self.closePlayer
                                     )
        self.w_quit.grid(row=1, column=3, padx=2, pady=2)
        
    def displayHelp(self):
        """Affiche l'aide"""
        msg = "RasPyPlayer, v{0}\n"
        msg += "Auteur : Julien Pecqueur (JPEC)\n"
        msg += "Email : jpec@julienpecqueur.net\n"
        msg += "Site : http://julienpecqueur.com\n"
        msg += "Sources : https://github.com/jpec/RasPyPlayer\n"
        msg += "Bugs : https://github.com/jpec/RasPyPlayer/issues\n"
        msg += "License : GNUGPL\n"
        msg += "\n"
        msg += "Raccourcis clavier pendant la lecture :\n"
        msg += "n : Sous-titre précédent\n"
        msg += "m : Sous-titre suivant\n"
        msg += "s : Bascule de sous-titre\n"
        msg += "q : Quitte le lecteur\n"
        msg += "p : Pause/Reprise (espace)\n"
        msg += "- : Baisse le volume\n"
        msg += "+ : Monte le volume\n"
        msg += "Left : Seek -30\n"
        msg += "Right : Seek +30\n"
        msg += "Down : Seek -600\n"
        msg += "Up : Seek +600\n"
        tkinter.messagebox.showinfo("Aide", msg.format(VERSION))
        
    def closePlayer(self):
        """Quitte l'application"""
        self.closeDB()
        self.root.destroy()
        
#-------------------------------------------------------------------------#
# PROGRAMME PRINCIPAL                                                     #
#-------------------------------------------------------------------------#

player = Player(PATH, DB)
player.root.mainloop()

#-------------------------------------------------------------------------#
# EOF                                                                     #
#-------------------------------------------------------------------------#
