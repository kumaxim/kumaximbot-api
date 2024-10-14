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

# resource "null_resource" "requirements" {
#   triggers = {
#     requirements = filesha512("${path.module}/poetry.lock")
#   }
#
#   provisioner "local-exec" {
#     command = "poetry export -o requirements.txt --without-hashes --without=dev"
#   }
# }
#
# resource "null_resource" "migrations" {
#   triggers = {
#     sha512sum = sha512(
#       trimspace(
#         join("", [
#           for table in fileset(path.module, "migrations/**/*.py") : file("${path.module}/${table}")
#         ])
#       )
#     )
#   }
#
#   provisioner "local-exec" {
#     command = "[ -f ${path.module}/assets/${local.sqlite_filename} ] && poetry run alembic upgrade head || poetry run alembic init && poetry run alembic upgrade head"
#   }
# }

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

resource "yandex_lockbox_secret" "tgbot" {
  name = local.project_slug
}

resource "yandex_lockbox_secret_version" "tgbot-latest" {
  secret_id = yandex_lockbox_secret.tgbot.id
  entries {
    key        = "BOT_TOKEN"
    text_value = var.BOT_TOKEN
  }
  entries {
    key        = "TELEGRAM_SECRET_TOKEN"
    text_value = var.TELEGRAM_SECRET_TOKEN
  }
  entries {
    key        = "YANDEX_OAUTH_CLIENT_ID"
    text_value = var.YANDEX_OAUTH_CLIENT_ID
  }
  entries {
    key        = "YANDEX_OAUTH_CLIENT_SECRET"
    text_value = var.YANDEX_OAUTH_CLIENT_SECRET
  }
  entries {
    key        = "PRIVILEGED_USER_LOGIN"
    text_value = var.PRIVILEGED_USER_LOGIN
  }
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
    DEV_MODE    = "False"
    ASSETS_PATH = "//function/storage/assets"
    SQLITE_PATH = "//function/storage/assets/${local.sqlite_filename}"
  }
  secrets {
    id                   = yandex_lockbox_secret.tgbot.id
    version_id           = yandex_lockbox_secret_version.tgbot-latest.id
    key                  = "BOT_TOKEN"
    environment_variable = "BOT_TOKEN"
  }
  secrets {
    id                   = yandex_lockbox_secret.tgbot.id
    version_id           = yandex_lockbox_secret_version.tgbot-latest.id
    key                  = "TELEGRAM_SECRET_TOKEN"
    environment_variable = "TELEGRAM_SECRET_TOKEN"
  }
  secrets {
    id                   = yandex_lockbox_secret.tgbot.id
    version_id           = yandex_lockbox_secret_version.tgbot-latest.id
    key                  = "YANDEX_OAUTH_CLIENT_ID"
    environment_variable = "YANDEX_OAUTH_CLIENT_ID"
  }
  secrets {
    id                   = yandex_lockbox_secret.tgbot.id
    version_id           = yandex_lockbox_secret_version.tgbot-latest.id
    key                  = "YANDEX_OAUTH_CLIENT_SECRET"
    environment_variable = "YANDEX_OAUTH_CLIENT_SECRET"
  }
  secrets {
    id                   = yandex_lockbox_secret.tgbot.id
    version_id           = yandex_lockbox_secret_version.tgbot-latest.id
    key                  = "PRIVILEGED_USER_LOGIN"
    environment_variable = "PRIVILEGED_USER_LOGIN"
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
  request_body = "url=${yandex_api_gateway.gw.domain}/webhook&drop_pending_updates=True&secret_token=${var.TELEGRAM_SECRET_TOKEN}"
}