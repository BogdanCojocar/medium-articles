provider "kubernetes" {
  load_config_file       = "false"
  host                   = data.aws_eks_cluster.cluster.endpoint
  token                  = data.aws_eks_cluster_auth.cluster.token
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
}

module "eks" {
  source       = "terraform-aws-modules/eks/aws"
  cluster_name = join("-", [var.cluster_name, var.environment, random_string.suffix.result])
  subnets      = module.vpc.private_subnets

  tags = {
    Environment = var.environment
  }

  vpc_id = module.vpc.vpc_id
  cluster_endpoint_private_access = true

  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  worker_groups = [
    {
      name                          = "worker-group-spark"
      instance_type                 = var.cluster_instance_type
      additional_userdata           = "worker nodes"
      asg_desired_capacity          = var.cluster_number_of_nodes
      additional_security_group_ids = [aws_security_group.all_worker_mgmt.id, aws_security_group.inside_vpc_traffic.id]
    }
  ]

  workers_group_defaults = {
    key_name = "eks_key"
    subnets = module.vpc.private_subnets
  }
}

data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
}
