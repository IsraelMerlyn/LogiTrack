from locust import HttpUser, task, between
import random

class UsuarioLogiTrack(HttpUser):
    wait_time = between(0.1, 0.5) # Espera entre 100ms y 500ms entre peticiones

    @task(3)
    def cotizar_envio(self):
        peso = random.randint(1, 100)
        distancia = random.randint(10, 1000)
        self.client.get(
            f"/api/v1/cotizar?peso={peso}&distancia={distancia}",
            name="/api/v1/cotizar"
        )

    @task(1)
    def consultar_inexistente(self):
        self.client.get("/api/v1/cotizar?peso=-5&distancia=10", name="/api/v1/cotizar_invalid")
