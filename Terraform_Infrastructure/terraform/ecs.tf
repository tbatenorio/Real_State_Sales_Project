provider "aws" {
  region = var.region
}

# 1. Criar a VPC para o cluster ECS
resource "aws_vpc" "ecs_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "ecs-vpc"
  }
}

# 2. Criar subnets para o ECS
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "ecs_subnet_public" {
  count                   = 2
  vpc_id                  = aws_vpc.ecs_vpc.id
  cidr_block              = cidrsubnet(aws_vpc.ecs_vpc.cidr_block, 8, count.index)
  availability_zone       = element(data.aws_availability_zones.available.names, count.index)
  map_public_ip_on_launch = true
  tags = {
    Name = "ecs-public-subnet-${count.index}"
  }
}

# 3. Criar o Internet Gateway
resource "aws_internet_gateway" "ecs_igw" {
  vpc_id = aws_vpc.ecs_vpc.id
  tags = {
    Name = "ecs-igw"
  }
}

# 4. Criar tabela de rotas para as subnets públicas
resource "aws_route_table" "ecs_public_route_table" {
  vpc_id = aws_vpc.ecs_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.ecs_igw.id
  }
  tags = {
    Name = "ecs-public-route-table"
  }
}

resource "aws_route_table_association" "ecs_subnet_route_assoc" {
  count          = 2
  subnet_id      = aws_subnet.ecs_subnet_public[count.index].id
  route_table_id = aws_route_table.ecs_public_route_table.id
}

# 5. Security Group para instâncias EC2 e o ECS
resource "aws_security_group" "ecs_security_group" {
  name   = "ecs_security_group"
  vpc_id = aws_vpc.ecs_vpc.id

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecs-security-group"
  }
}

# 6. Load Balancer
resource "aws_lb" "ecs_lb" {
  name               = "ecs-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_security_group.id]
  subnets            = aws_subnet.ecs_subnet_public[*].id
}

# 7. Target Group
resource "aws_lb_target_group" "ecs_target_group" {
  name        = "ecs-target-group"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = aws_vpc.ecs_vpc.id
  target_type = "instance"
  health_check {
    path                = "/"
    protocol            = "HTTP"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

# 8. Listener para o Load Balancer
resource "aws_lb_listener" "ecs_listener" {
  load_balancer_arn = aws_lb.ecs_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_target_group.arn
  }
}

# 9. ECS Cluster
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "ecs-cluster-ec2"
  tags = {
    Name = "ecs-cluster-ec2"
  }
}

# 10. ECS Task Definition
resource "aws_ecs_task_definition" "ecs_task" {
  family                   = "streamlit-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  
  container_definitions = jsonencode([{
    name      = "streamlit-app-container"
    image     = "386283720018.dkr.ecr.us-east-1.amazonaws.com/real-state-app"
    essential = true
    portMappings = [{
      containerPort = 8501
      hostPort      = 8501
      protocol      = "tcp"
    }]
  }])

  execution_role_arn = "arn:aws:iam::386283720018:role/eks_cluster_role_tcc"
}

# 11. Serviço ECS com Load Balancer
resource "aws_ecs_service" "ecs_service" {
  name            = "streamlit-app-service"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task.arn
  desired_count   = 1
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_target_group.arn
    container_name   = "streamlit-app-container"
    container_port   = 8501
  }

  network_configuration {
    subnets         = aws_subnet.ecs_subnet_public[*].id
    security_groups = [aws_security_group.ecs_security_group.id]
  }

  depends_on = [aws_lb_listener.ecs_listener]
}
