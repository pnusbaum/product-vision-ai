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
    volumes {
      name = "cloudsql"

      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }

    containers {
      image = "europe-central2-docker.pkg.dev/${var.project_id}/docker-images/product-api:v3"

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      env {
        name  = "DATABASE_URL"
        value = "postgresql+psycopg://app:${var.db_password}@/products_db?host=/cloudsql/${google_sql_database_instance.postgres.connection_name}"
      }
    }
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

resource "google_sql_database_instance" "postgres" {
  name             = "products-db"
  region           = var.region
  database_version = "POSTGRES_16"

  settings {
    tier    = "db-f1-micro"
    edition = "ENTERPRISE"

    disk_size = 20
    disk_type = "PD_SSD"
  }

  deletion_protection = false
}

resource "google_sql_database" "app_db" {
  name     = "products_db"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "app_user" {
  name     = "app"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

resource "google_storage_bucket" "product_images" {
  name     = "${var.project_id}-product-images"
  location = var.region

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
resource "google_storage_bucket_iam_member" "product_images_public" {
  bucket = google_storage_bucket.product_images.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_cloud_run_v2_service" "product_streamlit" {
  name                = "product-streamlit"
  location            = var.region
  deletion_protection = false

  template {
    containers {
      image = "europe-central2-docker.pkg.dev/${var.project_id}/docker-images/product-streamlit:v2"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      
      env {
        name  = "IMAGE_SEARCH_API_URL"
        value = google_cloud_run_v2_service.product_api.uri
      }

      env {
        name  = "PRODUCT_DESCRIPTION_API_URL"
        value = "${google_cloud_run_v2_service.product_description_api.uri}/generate-product-description"
      }
    }
  }

  depends_on = [
    google_project_service.services
  ]
}

resource "google_cloud_run_v2_service_iam_member" "streamlit_public" {
  location = google_cloud_run_v2_service.product_streamlit.location
  name     = google_cloud_run_v2_service.product_streamlit.name

  role   = "roles/run.invoker"
  member = "allUsers"
}

resource "google_cloud_run_v2_service" "product_description_api" {
  name                = "product-description-api"
  location            = var.region
  deletion_protection = false

  template {
    containers {
      image = "europe-central2-docker.pkg.dev/${var.project_id}/docker-images/product-description-api:v1"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "OPENAI_API_KEY"
        value = var.openai_api_key
      }

      env {
        name  = "OPENAI_MODEL"
        value = "gpt-4o"
      }
    }
  }

  depends_on = [
    google_project_service.services
  ]
}

resource "google_cloud_run_v2_service_iam_member" "product_description_api_public" {
  location = google_cloud_run_v2_service.product_description_api.location
  name     = google_cloud_run_v2_service.product_description_api.name

  role   = "roles/run.invoker"
  member = "allUsers"
}