terraform {
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.0"
    }
  }
}

provider "render" {
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}

variable "render_api_key" {
  type      = string
  sensitive = true
}

variable "render_owner_id" {
  type = string
}

resource "render_web_service" "todo_api" {
  name   = "todo-api"
  plan   = "free"
  region = "ohio"

  # Explicitly disable maintenance mode to prevent the API error
  maintenance_mode = {
    enabled = false
    uri     = null
  }

  # Correct schema structure for the Render Terraform Provider
  runtime_source = {
    docker = {
      repo_url = "https://github.com/Caribbeancool/todo-api"
      branch   = "main"
    }
  }


  env_vars = {
    APP_ENV = {
      value = "production"
    }
    DATABASE_URL = {
      value = var.database_url
    }
  }
}


variable "database_url" {
  type      = string
  sensitive = true
}