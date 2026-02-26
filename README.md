# robocup

## Structure du projet

### Modules principaux

- camera.py  : initialisation de la caméra
- click_and_go.py : affiche une image, se déplace au point sur lequel on double clic
- enregistrement.py : enregistrement d'une video dans un second thread + avance en fonction des entrées clavier (curses)
- intersections.py : détection et affichage des lignes sur une image
- ligne_droite_spike2.py: PROGRAMME PRINCIPAL suivi d'une ligne avec enregistrement de la trajectoire 

### Programmes de tests

- tutoriels: stocke les fichiers de découverte des différents éléments, pour mémoire
  - Barycentre: calcul du barycentre
  - tuto_opencv: afficher une image
  - tutoriel.py: exercice 2, question 4
  - commandes.py: découverte des commandes des moteurs pipounesques
  - chess: calibration de la caméra (effet de perspectives)
- Intersection
  - intersection.py: détection et affichage des lignes sur une image (intersection1.jpg)
  - inter_vid.py: détection et affichage des lignes sur une video
- Moteurs
  - controle.py: actionner les moteurs en fonction de l'entrée clavier 
  - deplacements_robot.py: fonctions pour déplacer le robot
  - stop.py: programme pour arreter les moteurs en cas d'urgence
- Suivi
  - suivi_droit.py et ligne_droite.py: suivi d'une ligne (barycentre) avec les moteurs pipounesques
  - ligne_droite_spike.py: suivi d'une ligne avec enregistrement de la trajectoire et les moteurs spike
- thread
  - enregistrement.py : enregistrement d'une video dans un second thread
  - enregistrement_maitrise.py: idem + avance en fonction des entrées clavier (avec input: ne fonctionne pas)

  
  
## TODO

- [ ] supprimer le répertoire data
- [ ] déplacer le répertoire Barycentre dans tutoriels
- [ ] déplacer le programme calibre.py dans le répertoire chess
- [ ] supprimer le programme p1.py
- [ ] déplacer prise_image.py dans chess
- [ ] déplacer test_curses.py et test_pynput.py et video_lecture.py dans tutoriels


## Journal

- Janvier: suivi de ligne avec la caméra (barycentre), controle des moteurs pour prendre des videos de tests
- Fevrier: détection des lignes, se rendre à un point donné (click and go)
- Mars: calcul des intersections 