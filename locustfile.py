from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth


class AlmoraUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.auth = HTTPBasicAuth("lake", "12345678")

    @task(3)
    def view_dashboard_stats(self):
        self.client.get("/api/accounts/dashboard-stats/", auth=self.auth)

    @task(3)
    def view_profile(self):
        self.client.get("/api/accounts/profile/", auth=self.auth)

    @task(2)
    def view_courses(self):
        self.client.get("/api/accounts/courses/", auth=self.auth)

    @task(2)
    def view_course_registrations(self):
        self.client.get("/api/accounts/course-registrations/", auth=self.auth)

    @task(2)
    def view_academic_records(self):
        self.client.get("/api/accounts/academic-records/", auth=self.auth)

    @task(2)
    def view_payment_transactions(self):
        self.client.get("/api/accounts/payment-transactions/", auth=self.auth)

    @task(1)
    def view_faculties(self):
        self.client.get("/api/accounts/faculties/", auth=self.auth)

    @task(1)
    def view_departments(self):
        self.client.get("/api/accounts/departments/", auth=self.auth)
