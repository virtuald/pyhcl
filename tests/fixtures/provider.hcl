provider "aws" {
  region  = "${var.active_region}"
  version = "~> 1.28.0"
}
 
provider "aws" {
  region  = "${var.active_region-2}"
  version = "~> 1.28.0"
  alias = "dr"
}
