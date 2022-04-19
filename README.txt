Fichier Bargaining.py:
  - code fonctionnel 
  - à exécuter plusieurs fois pour voir des négociations différentes entre les clients et les vendeurs 
  - exécuter dans le Terminal : pade start-runtime --port 2000 Bargaining.py
  - 4 classes et 4 comportements : Client, RandomWalker, CarefulAgent et ImitatingAgent

Fichier Bargaining2.py:
  - code qu'on a réellement voulu faire sauf qu'au moment de l'exécution du code → arrêt lors de l'envoi du prix initial par les vendeurs aux différents clients (le message s'envoie mais aucune reception du côté du client malgré de nombreuses tentatives)
  - 2 classes principales avec leurs comportements correspondant: Client et Vendeur 
  - 3 classes qui héritent de la classe Vendeur: RandomWalker, CarefulAgent et ImitatingAgent
  - 1 classe qui hérite de RandomWalker, CarefulAgent et ImitatingAgent: AdaptiveAgent 
  - exécuter dans le Terminal: page start-runtime --port 2000 Bargaining2.py