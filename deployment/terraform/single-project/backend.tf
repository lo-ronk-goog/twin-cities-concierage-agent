terraform {
  backend "gcs" {
    bucket = "lpr-gemini-enterprise-1-terraform-state"
    prefix = "twin-cities-concierage-agent/dev"
  }
}
