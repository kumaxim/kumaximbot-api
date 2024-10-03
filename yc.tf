terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }

  required_version = ">= 1.9.0"

  backend "s3" {
    endpoints = {
      s3 = "https://storage.yandexcloud.net"
    }

    bucket = "kumaximbot-tf-state"
    key    = "terraform.tfstate"
    region = "ru-central1-b"

    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true # Необходимая опция Terraform для версии 1.6.1 и старше.
    skip_s3_checksum            = true # Необходимая опция при описании бэкенда для Terraform версии 1.6.3 и старше.
  }
}

provider "yandex" {
  zone = "ru-central1-b"
}

locals {
  project_slug    = "tg-kumaximbot-t001"
  sqlite_filename = "db.sqlite"
}

variable "SERVICE_ACCOUNT_ID" {
  type      = string
  sensitive = true
  nullable  = false
}

variable "BOT_TOKEN" {
  type      = string
  sensitive = true
  nullable  = false
}

output "domain" {
  value = yandex_api_gateway.gw.domain
}

data "archive_file" "dist" {
  type        = "zip"
  source_dir  = path.module
  excludes    = ["*__pycache__*/*", "*terraform*", ".git/*", ".idea/*", "assets/*", ".env*"]
  output_path = "${path.module}/assets/dist.zip"
  depends_on  = [null_resource.requirements]
}

resource "null_resource" "requirements" {
  provisioner "local-exec" {
    command = "poetry export -o requirements.txt --without-hashes --without=dev"
  }

  triggers = {
    requirements = filesha256("${path.module}/poetry.lock")
  }
}

resource "yandex_iam_service_account_static_access_key" "sa-keys" {
  service_account_id = var.SERVICE_ACCOUNT_ID
  description        = "static access key for object storage"
}

resource "yandex_storage_bucket" "s3" {
  access_key = yandex_iam_service_account_static_access_key.sa-keys.access_key
  secret_key = yandex_iam_service_account_static_access_key.sa-keys.secret_key
  bucket     = local.project_slug
}

resource "yandex_storage_object" "sqlite" {
  access_key = yandex_iam_service_account_static_access_key.sa-keys.access_key
  secret_key = yandex_iam_service_account_static_access_key.sa-keys.secret_key
  bucket     = yandex_storage_bucket.s3.bucket
  key        = local.sqlite_filename
  source     = "${path.module}/assets/${local.sqlite_filename}"
}

resource "yandex_api_gateway" "gw" {
  name = local.project_slug
  spec = templatefile("${path.module}/gw-spec.yaml", {
    function_id : yandex_function.handler.id
    service_account_id : var.SERVICE_ACCOUNT_ID
  })
}

resource "yandex_function" "handler" {
  name               = local.project_slug
  user_hash          = data.archive_file.dist.output_sha
  runtime            = "python312"
  entrypoint         = "app.main.handler"
  memory             = "256"
  execution_timeout  = "30"
  service_account_id = var.SERVICE_ACCOUNT_ID
  labels = {
    tgbot : "staging"
  }
  content {
    zip_filename = data.archive_file.dist.output_path
  }
  environment = {
    DEV_MODE    = "True"
    BOT_TOKEN   = var.BOT_TOKEN
    SQLITE_PATH = "//function/storage/assets/${local.sqlite_filename}"
  }
  mounts {
    name = "assets"
    mode = "rw"
    object_storage {
      bucket = yandex_storage_bucket.s3.bucket
    }
  }
}
