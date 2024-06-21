hcl
resource "huaweicloud_compute_keypair_v2" "keypair" {
  name = "my_keypair"
}

resource "huaweicloud_compute_instance_v2" "ecs_instance" {
  name            = "my_ecs_instance"
  flavor_id       = "s3.large.2"
  image_id        = "a1b2c3d4-e5f6-7890-1234-56789abcdef0"
  key_pair        = huaweicloud_compute_keypair_v2.keypair.name
  availability_zone = "cn-north-1a"
  security_groups = [huaweicloud_networking_secgroup_v2.secgroup.name]

  network {
    uuid = huaweicloud_vpc_subnet_v1.subnet.id
  }
}
