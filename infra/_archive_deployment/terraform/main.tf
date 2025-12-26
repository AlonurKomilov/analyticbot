# Terraform Configuration for Contabo VPS
terraform {
  required_version = ">= 1.0"
  required_providers {
    # Note: Use official Contabo provider when available
    # For now, using generic cloud provider
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

# Variables
variable "server_ip" {
  description = "IP address of your Contabo VPS"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for server access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "analyticbot.com"
}

# Local file for inventory
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/inventory.tpl", {
    server_ip = var.server_ip
  })
  filename = "${path.module}/../ansible/inventory.ini"
}

# Generate Kubernetes install script
resource "local_file" "k8s_install_script" {
  content = templatefile("${path.module}/scripts/install-k8s.sh.tpl", {
    domain_name = var.domain_name
  })
  filename = "${path.module}/scripts/install-k8s.sh"
}

# Null resource to run Ansible after Terraform
resource "null_resource" "run_ansible" {
  depends_on = [local_file.ansible_inventory]

  provisioner "local-exec" {
    command = "cd ${path.module}/../ansible && ansible-playbook -i inventory.ini setup-k8s.yml"
  }

  triggers = {
    inventory_content = local_file.ansible_inventory.content
  }
}

# Outputs
output "server_ip" {
  description = "IP address of the VPS server"
  value       = var.server_ip
}

output "kubernetes_setup" {
  description = "Instructions for connecting to Kubernetes"
  value = <<-EOT
    To connect to your Kubernetes cluster:
    1. SSH to server: ssh root@${var.server_ip}
    2. Copy kubeconfig: scp root@${var.server_ip}:/etc/kubernetes/admin.conf ~/.kube/config
    3. Test connection: kubectl get nodes
  EOT
}

output "next_steps" {
  description = "Next steps after infrastructure setup"
  value = <<-EOT
    Phase 0 Infrastructure Setup Complete!

    Next Steps:
    1. Update DNS records to point ${var.domain_name} to ${var.server_ip}
    2. Run deployment script: ./infrastructure/deploy-k8s.sh
    3. Install cert-manager for SSL: kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    4. Setup monitoring stack
  EOT
}
