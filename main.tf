# terraform is not supported in render.com free plan
terraform {
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "1.3.4"
    }
  }
}

variable "plan" {
  type    = string
  default = "free"
}

variable "region" {
  type    = string
  default = "frankfurt"
}

provider "render" {
  wait_for_deploy_completion = true
}

resource "render_postgres" "applifting_api_database" {
  name          = "applifting-api-db"
  plan          = var.plan
  region        = var.region
  version       = "16"
  database_name = "applifting"
  database_user = "applifting"
}

resource "render_web_service" "applifting_api_app" {
  name   = "applifting-api-app"
  plan   = var.plan
  region = var.region
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
  # TODO: set environment variables to match "applifting_api_database" (e.g. address, user, etc.)
  env_vars = {
    "key1" = { value = "val1" },
    "key2" = { value = "val2" },
  }
}
