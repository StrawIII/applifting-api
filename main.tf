# render.com currently does not support terraform for free plan
terraform {
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "1.3.4"
    }
  }
}

provider "render" {
  wait_for_deploy_completion = true
}

resource "render_postgres" "applifting_api_database" {
  name          = "applifting-api-db"
  plan          = "free"
  region        = "frankfurt"
  version       = "16"
  database_name = "applifting"
  database_user = "applifting"
}

resource "render_web_service" "applifting_api_app" {
  name   = "applifting-api-app"
  plan   = "free"
  region = "frankfurt"
  runtime_source = {
    docker = {
      branch          = "main"
      repo_url        = "https://github.com/StrawIII/applifting-api"
      auto_deploy     = true
      context         = "."
      dockerfile_path = "./Dockerfile"
    }
  }
  secret_files = {
    ".env" = { content = file("${path.module}/.env") }
  }
  # TODO: set environment variables to match "applifting_api_database" (e.g. adress, user, etc.)
  env_vars = {
    "key1" = { value = "val1" },
    "key2" = { value = "val2" },
  }
}
