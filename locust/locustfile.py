from locust import HttpUser, task, between
import random

# pool of addresses to simulate user input
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
    # wait_time = between(1, 5)
    wait_time = between(1, 5)
    
    # URL of the Flask app
    host = "http://xxx.xxx.xxx.xxx"
    
    @task(2)  # weights of 2 for the task
    def get_home(self):
        response = self.client.get("/")
        if response.status_code != 200:
            response.failure(f"GET / failed with status {response.status_code}")
    
    @task(1)  # weights of 1 for the task
    def findpath(self):
        # Generate random coordinates to simulate varied data
        start = random.choices(addresses)
        end = random.choice(addresses)
        
        response = self.client.get("/findpath", params={"start": start, "end": end})
                
        if response.status_code != 200:
            response.failure(f"GET /findpath failed with status {response.status_code}")