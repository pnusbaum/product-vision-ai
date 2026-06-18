resource "google_project_service" "services" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "docker_repo" {
  depends_on = [google_project_service.services]

  location      = var.region
  repository_id = "docker-images"
  description   = "Docker images"
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "product_api" {
  name                = "product-api"
  location            = var.region
  deletion_protection = false
  template {
    containers {      
      image = "europe-central2-docker.pkg.dev/${var.project_id}/docker-images/product-api:v1"      

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }
      env {
        name  = "DATABASE_URL"
        value = "postgresql+psycopg://dummy:dummy@localhost:5432/dummy"
      }

    }    
    timeout = "300s"
  }

  depends_on = [
    google_project_service.services
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  location = google_cloud_run_v2_service.product_api.location
  name     = google_cloud_run_v2_service.product_api.name

  role   = "roles/run.invoker"
  member = "allUsers"
}