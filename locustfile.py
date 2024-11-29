from locust import HttpUser, task, between
import random


class FlaskAppUser(HttpUser):
    wait_time = between(1, 2)
    # Wait time between requests (1-2 seconds)

    host = "http://localhost:5000"

    @task(1)
    def index(self):
        self.client.get("/")

    @task(2)
    def generate_otp(self):
        self.client.get("/otp")

    @task(1)
    def error_page(self):
        self.client.get("/charshochar")  # Modify to trigger 404 or other error
