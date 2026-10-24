variable "region" {
  type = string
}

variable "github_org" {
  type    = string
  default = "locuyo"
}

variable "github_repo" {
  type    = string
  default = "locuyo"
}

variable "deploy_environment" {
  description = "GitHub Environment whose jobs may assume the deploy role"
  type        = string
  default     = "prod"
}
