bar "foo" {

    name = "terraform_example"

    ingress {
        from_port = 22
    }

    ingress {
        from_port = 80
    }

    ingress {
        from_port = 51
    }

}
