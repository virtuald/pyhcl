resource "aws_db_instance" "mysqldb" {
    identifier = "${var.environment}-mysqldb"
    allocated_storage = 100
}
resource "aws_db_instance" "mysqldb-readonly" {
    identifier = "${var.environment}-mysqldb-readonly"
    allocated_storage = 100
}

