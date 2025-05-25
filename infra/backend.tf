terraform {
  backend "s3" {
    bucket       = "osouji-reminder-v2-tf-state"
    key          = "osouji-reminder-v2/terraform.tfstate"
    region       = "ap-northeast-1"
    profile      = "scooter_personal"
    use_lockfile = true
    encrypt      = true
  }
}
