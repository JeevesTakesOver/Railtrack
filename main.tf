provider "aws" {
  region     = "eu-west-1"
}


resource "aws_key_pair" "railtrack" {
  key_name   = "railtrack"
  public_key = "${file("~/.ssh/id_rsa.pub")}"
}


data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}


resource "aws_security_group" "allow_all_tcp" {
  name        = "allow_all_tcp"
  description = "Allow all TCP inbound traffic"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "allow_all_udp" {
  name        = "allow_all_udp"
  description = "Allow all udp inbound traffic"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "core01" {
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = "t1.micro"
  associate_public_ip_address = true
  security_groups = [ "allow_all_tcp", "allow_all_udp" ]
  key_name = "railtrack"

  tags {
    Name = "core01"
  }

  depends_on = [ 
    "aws_key_pair.railtrack",
    "aws_security_group.allow_all_tcp",
    "aws_security_group.allow_all_udp"
  ]
}

resource "aws_instance" "core02" {
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = "t1.micro"
  associate_public_ip_address = true
  security_groups = [ "allow_all_tcp", "allow_all_udp" ]
  key_name = "railtrack"

  tags {
    Name = "core02"
  }

  depends_on = [ 
    "aws_key_pair.railtrack",
    "aws_security_group.allow_all_tcp",
    "aws_security_group.allow_all_udp"
  ]
}

resource "aws_instance" "core03" {
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = "t1.micro"
  associate_public_ip_address = true
  security_groups = [ "allow_all_tcp", "allow_all_udp" ]
  key_name = "railtrack"

  tags {
    Name = "core03"
  }

  depends_on = [ 
    "aws_key_pair.railtrack",
    "aws_security_group.allow_all_tcp",
    "aws_security_group.allow_all_udp"
  ]
}

resource "aws_instance" "git2consul" {
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = "t1.micro"
  associate_public_ip_address = true
  security_groups = [ "allow_all_tcp", "allow_all_udp" ]
  key_name = "railtrack"

  tags {
    Name = "git2consul"
  }

  depends_on = [ 
    "aws_key_pair.railtrack",
    "aws_security_group.allow_all_tcp",
    "aws_security_group.allow_all_udp"
  ]
}


data "aws_route53_zone" "selected" {
  name         = "aws.azulinho.com."
  private_zone = false
}


resource "aws_route53_record" "core01-private" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "core01-private.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.core01.private_ip}"]
  depends_on = [ 
    "aws_instance.core01"
  ]
}

resource "aws_route53_record" "core02-private" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "core02-private.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.core02.private_ip}"]
  depends_on = [ 
    "aws_instance.core02"
  ]
}

resource "aws_route53_record" "core03-private" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "core03-private.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.core03.private_ip}"]
  depends_on = [ 
    "aws_instance.core03"
  ]
}

resource "aws_route53_record" "git2consul-private" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "git2consul-private.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.git2consul.private_ip}"]
  depends_on = [ 
    "aws_instance.git2consul"
  ]
}

resource "aws_route53_record" "core01-public" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "core01-public.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.core01.public_ip}"]
  depends_on = [ 
    "aws_instance.core01"
  ]
}

resource "aws_route53_record" "core02-public" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "core02-public.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.core02.public_ip}"]
  depends_on = [ 
    "aws_instance.core02"
  ]
}

resource "aws_route53_record" "core03-public" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "core03-public.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.core03.public_ip}"]
  depends_on = [ 
    "aws_instance.core03"
  ]
}

resource "aws_route53_record" "git2consul-public" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "git2consul-public.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.git2consul.public_ip}"]
  depends_on = [ 
    "aws_instance.git2consul"
  ]
}