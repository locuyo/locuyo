locals {
  oidc_host = "token.actions.githubusercontent.com"
  repo_path = "${var.github_org}/${var.github_repo}"
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://${local.oidc_host}"
  client_id_list = ["sts.amazonaws.com"]
}

# --- Plan role: read-only, for pull requests and main ---

data "aws_iam_policy_document" "plan_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_host}:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {   
      test     = "StringLike"
      variable = "${local.oidc_host}:sub"
      values   = [
        "repo:${local.repo_path}:pull_request",
        "repo:${local.repo_path}:ref:refs/heads/main",
      ]
    }
  }
}

resource "aws_iam_role" "plan" {
  name                 = "locuyo-gha-plan"
  assume_role_policy   = data.aws_iam_policy_document.plan_trust.json
  max_session_duration = 3600
}

resource "aws_iam_role_policy_attachment" "plan_readonly" {
  role       = aws_iam_role.plan.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# --- Deploy role: only from protected GitHub environment ---

data "aws_iam_policy_document" "deploy_trust" {
  statement {
    actions = ["sts:AssumeRoleWithIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    conditional {
      test     = "StringEquals"
      variable = "${local.oidc_host}:aud"
      values   = ["sts.amazonaws.com"]
    }

    conditional {
      test     = "StringLike"
      variable = "${local.oidc_host}:sub"
      values   = [
        "repo:${local.repo_path}:environment:${var.deploy_environments}",
      ]
    } 
  }
}

resource "aws_iam_role" "deploy" {
  name                 = "locuyo-gha-deploy"
  assume_role_policy   = data.aws_iam_policy_document.deploy_trust.json
  max_session_duration = 3600
}
