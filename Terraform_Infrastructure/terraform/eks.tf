provider "aws" {
   region = var.region  # Substitua pela região que você deseja usar
}

# Declaração do data source para obter as zonas de disponibilidade
 data "aws_availability_zones" "available" {
   state = "available"  # Filtra para zonas de disponibilidade que estão ativas
}

# 1. Criar a VPC para o cluster EKS
 resource "aws_vpc" "eks_vpc" {
   cidr_block = "10.0.0.0/16"
  
   tags = {
        Name = "eks-vpc"
   }
}

# 2. Criar subnets para o EKS
resource "aws_subnet" "eks_subnet_public" {
   count = 2  # Cria duas subnets
   vpc_id            = aws_vpc.eks_vpc.id
   cidr_block        = cidrsubnet(aws_vpc.eks_vpc.cidr_block, 8, count.index)
   availability_zone = element(data.aws_availability_zones.available.names, count.index)
   map_public_ip_on_launch = true  # Habilita a atribuição de IP público automaticamente
   
   tags = {
        Name = "eks-public-subnet-${count.index}"
   }
}

# 3. Criar o Internet Gateway
 resource "aws_internet_gateway" "eks_igw" {
   vpc_id = aws_vpc.eks_vpc.id
  
   tags = {
        Name = "eks-igw"
  }
}

# 4. Criar tabela de rotas para as subnets públicas
resource "aws_route_table" "eks_public_route_table" {
   vpc_id = aws_vpc.eks_vpc.id

   route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.eks_igw.id
   }

   tags = {
        Name = "eks-public-route-table"
   }
}

resource "aws_route_table_association" "eks_subnet_route_assoc" {
   count          = 2
   subnet_id      = aws_subnet.eks_subnet_public[count.index].id
   route_table_id = aws_route_table.eks_public_route_table.id
}


# 5. Criar o Cluster EKS
resource "aws_eks_cluster" "eks_cluster" {
   name     = "eks-cluster"
   role_arn = "arn:aws:iam::386283720018:role/eks_cluster_role_tcc"
  
   vpc_config {
        subnet_ids = aws_subnet.eks_subnet_public[*].id
   }

   depends_on = [
        aws_vpc.eks_vpc,
        aws_subnet.eks_subnet_public
   ]
  
   tags = {
        Name = "eks-cluster"
   }
}


# 6. Grupo de nós de trabalho gerenciado
resource "aws_eks_node_group" "eks_node_group" {
   cluster_name    = aws_eks_cluster.eks_cluster.name
   node_group_name = "eks-node-group"
   node_role_arn   = "arn:aws:iam::386283720018:role/eks_cluster_role_tcc"
   subnet_ids      = aws_subnet.eks_subnet_public[*].id
   
   scaling_config {
        desired_size = 2
        max_size     = 3
        min_size     = 1
   }

   depends_on = [
        aws_eks_cluster.eks_cluster
   ]
  
    tags = {
        Name = "eks-node-group"
   }
}

# 7. Saída do nome do Cluster EKS
output "eks_cluster_name" {
    value = aws_eks_cluster.eks_cluster.name
}

output "eks_cluster_endpoint" {
   value = aws_eks_cluster.eks_cluster.endpoint
}

output "eks_cluster_arn" {
   value = aws_eks_cluster.eks_cluster.arn
}

