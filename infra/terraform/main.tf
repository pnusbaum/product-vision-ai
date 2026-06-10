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