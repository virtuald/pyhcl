foo "bar" "baz" {
	key = 4
}

foo "bar" "qux" {
	key = 5
}

foo "bar" "biz" {
	key = 11
}

bar "foo" "qux" {
	key = 8
}

bar "foo" "biz" {
	key = 9
	key2 = 3
}

baz "foo" "biz" {
	key = 9
	key5 = "somestring"
}
