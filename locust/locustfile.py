from locust import HttpUser, task, between
import random

addresses = [
    "485 ROUTE DE WINDSOR",
    "473 ROUTE DE WINDSOR",
    "3747 RUE DUNANT",
    "3135 RUE DES ARTISANS",
    "2955 BOULEVARD DE L'UNIVERSITE",
    "2965 BOULEVARD DE L'UNIVERSITE",
    "2745 RUE DE LA SHERWOOD",
    "135 RUE DON BOSCO N",
    "3400 BOULEVARD DE PORTLAND",
    "2875 RUE DU MANOIR",
    "2775 RUE DU MANOIR",
    "2835 RUE DU MANOIR",
    "3110 CHEMIN DES ECOSSAIS",
    "35 RUE DU CURE LAROCQUE",
    "160 RUE RENE",
    "156 RUE CLARK",
    "611 RUE POULIN",
    "2160 RUE DES CERISIERS",
    "2165 RUE DES CERISIERS",
    "2625 RUE DES CYPRES",
    "2615 RUE DES CYPRES",
    "2605 RUE DES CYPRES",
    "2595 RUE DES CYPRES",
    "2585 RUE DES CYPRES",
    "2562 RUE DES CYPRES"
]


class FlaskAppUser(HttpUser):
    # Temps d'attente entre les tâches (1 à 5 secondes pour simuler un comportement réaliste)
    wait_time = between(1, 5)
    
    # URL de base de l'application
    host = "http://xxx.xxx.xxx.xxx"
    
    @task(2)  # Poids de 2 : les GET sont plus fréquents
    def get_home(self):
        response = self.client.get("/")
        if response.status_code != 200:
            response.failure(f"GET /points failed with status {response.status_code}")
    
    @task(1)  # Poids de 1 : les POST sont moins fréquents
    def findpath(self):
        # Générer des coordonnées aléatoires pour simuler des données variées
        start = random.choices(addresses)
        end = random.choice(addresses)
        
        response = self.client.get("/findpath", params={"start": start, "end": end})
                
        if response.status_code != 200:
            response.failure(f"GET /findpath failed with status {response.status_code}")