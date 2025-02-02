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
    key    = "api-terraform.tfstate"
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
  project_slug    = "kumaximbot-api"
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

variable "TELEGRAM_SECRET_TOKEN" {
  type      = string
  sensitive = true
  nullable  = false
}

variable "YANDEX_OAUTH_CLIENT_ID" {
  type      = string
  sensitive = true
  nullable  = false
}

variable "YANDEX_OAUTH_CLIENT_SECRET" {
  type      = string
  sensitive = true
  nullable  = false
}

variable "PRIVILEGED_USER_LOGIN" {
  type      = string
  sensitive = true
  nullable  = false
}

output "gateway-domain" {
  value = yandex_api_gateway.gw.domain
}

output "telegram-webhook" {
  value = {
    status_code = data.http.setup-tg-webhook.status_code
    body        = data.http.setup-tg-webhook.response_body
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

module "template_files" {
  source   = "github.com/hashicorp/terraform-template-dir.git"
  base_dir = "${path.module}/assets"
}

resource "yandex_storage_object" "tgbot" {
  access_key = yandex_iam_service_account_static_access_key.sa-keys.access_key
  secret_key = yandex_iam_service_account_static_access_key.sa-keys.secret_key
  bucket     = yandex_storage_bucket.s3.bucket

  for_each = module.template_files.files

  key          = each.key
  source       = each.value.source_path
  source_hash  = each.value.digests.md5
  content_type = each.value.content_type
}

data "archive_file" "dist" {
  type        = "zip"
  source_dir  = path.module
  excludes    = ["*__pycache__*/*", "*terraform*", "dist/*", "assets/*", ".git/*", ".idea/*", ".github/*", ".env*"]
  output_path = "${path.module}/dist/archive.zip"
  depends_on  = [yandex_storage_object.tgbot]
}

resource "yandex_function" "handler" {
  name               = local.project_slug
  user_hash          = data.archive_file.dist.output_sha512
  runtime            = "python312"
  entrypoint         = "app.main.handler"
  memory             = "256"
  execution_timeout  = "180"
  service_account_id = var.SERVICE_ACCOUNT_ID
  content {
    zip_filename = data.archive_file.dist.output_path
  }
  environment = {
    DEV_MODE                   = "False"
    ASSETS_PATH                = "//function/storage/assets"
    SQLITE_PATH                = "//function/storage/assets/${local.sqlite_filename}"
    BOT_TOKEN                  = trimspace(var.BOT_TOKEN)
    TELEGRAM_SECRET_TOKEN      = trimspace(var.TELEGRAM_SECRET_TOKEN)
    YANDEX_OAUTH_CLIENT_ID     = trimspace(var.YANDEX_OAUTH_CLIENT_ID)
    YANDEX_OAUTH_CLIENT_SECRET = trimspace(var.YANDEX_OAUTH_CLIENT_SECRET)
    PRIVILEGED_USER_LOGIN      = trimspace(var.PRIVILEGED_USER_LOGIN)
  }
  mounts {
    name = "assets"
    mode = "rw"
    object_storage {
      bucket = yandex_storage_bucket.s3.bucket
    }
  }
}

resource "yandex_api_gateway" "gw" {
  name = local.project_slug
  spec = templatefile("${path.module}/gw-spec.yaml", {
    function_id : yandex_function.handler.id
    service_account_id : var.SERVICE_ACCOUNT_ID
  })
}

data "http" "setup-tg-webhook" {
  url    = "https://api.telegram.org/bot${var.BOT_TOKEN}/setWebhook"
  method = "POST"
  request_headers = {
    Content-Type : "application/x-www-form-urlencoded"
  }
  request_body = "url=https://${yandex_api_gateway.gw.domain}/telegram/webhook&drop_pending_updates=True&secret_token=${var.TELEGRAM_SECRET_TOKEN}"
}