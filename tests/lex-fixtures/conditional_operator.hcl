// objectitem : objectkey EQUAL objectkey QMARK objectkey COLON objectkey
identifier1 = identifier2  ? identifier3 : identifier4
// objectitem : objectkey EQUAL objectkey QMARK objectkey COLON number
identifier1 = identifier2 ? identifier3 : 1
// objectitem : objectkey EQUAL objectkey QMARK objectkey COLON BOOL
identifier1 = identifier2 ? identifier3 : True
// objectitem : objectkey EQUAL objectkey QMARK objectkey COLON function
identifier1 = identifier2 ? identifier3 : element(identifier4, identifier5)
// objectitem : objectkey EQUAL objectkey QMARK number COLON objectkey
identifier1 = identifier2 ? 1 : identifier3
// objectitem : objectkey EQUAL objectkey QMARK BOOL COLON objectkey
identifier1 = identifier2 ? True : identifier3
// objectitem : objectkey EQUAL objectkey QMARK function COLON objectkey
identifier1 = identifier2 ? element(identifier3, identifier4) : identifier5
// objectitem : objectkey EQUAL objectkey QMARK number COLON number
identifier1 = identifier2 ? 1 : 2
// objectitem : objectkey EQUAL objectkey QMARK number COLON BOOL
identifier1 = identifier2 ? 1 : True
// objectitem : objectkey EQUAL objectkey QMARK number COLON function
identifier1 = identifier2 ? 1 : element(identifier3, identifier4)
// objectitem : objectkey EQUAL objectkey QMARK BOOL COLON number
identifier1 = identifier2 ? True : 1
// objectitem : objectkey EQUAL objectkey QMARK BOOL COLON function
identifier1 = identifier2 ? True : element(identifier3, identifier4)
// objectitem : objectkey EQUAL objectkey QMARK BOOL COLON BOOL
identifier1 = identifier2 ? True : False

// objectitem : objectkey EQUAL booleanexp QMARK objectkey COLON objectkey
identifier1 = identifier2 == identifier3 ? identifier4 : identifier5
// objectitem : objectkey EQUAL booleanexp QMARK objectkey COLON number
identifier1 = identifier2 == identifier3 ? identifier4 : 1
// objectitem : objectkey EQUAL booleanexp QMARK objectkey COLON BOOL
identifier1 = identifier2 == identifier3 ? identifier4 : True
// objectitem : objectkey EQUAL booleanexp QMARK objectkey COLON function
identifier1 = identifier2 == identifier3 ? identifier4 : element(identifier5, identifier6)
// objectitem : objectkey EQUAL booleanexp QMARK number COLON objectkey
identifier1 = identifier2 == identifier3 ? 1 : identifier4
// objectitem : objectkey EQUAL booleanexp QMARK BOOL COLON objectkey
identifier1 = identifier2 == identifier3 ? True : identifier4
// objectitem : objectkey EQUAL booleanexp QMARK function COLON objectkey
identifier1 = identifier2 == identifier3 ? element(identifier4, identifier5) : identifier6
// objectitem : objectkey EQUAL booleanexp QMARK number COLON number
identifier1 = identifier2 == identifier3 ? 1 : 2
// objectitem : objectkey EQUAL booleanexp QMARK number COLON BOOL
identifier1 = identifier2 == identifier3 ? 1 : True
// objectitem : objectkey EQUAL booleanexp QMARK number COLON function
identifier1 = identifier2 == identifier3 ? 1 : element(identifier4, identifier5)
// objectitem : objectkey EQUAL booleanexp QMARK BOOL COLON number
identifier1 = identifier2 == identifier3 ? True : 1
// objectitem : objectkey EQUAL booleanexp QMARK BOOL COLON function
identifier1 = identifier2 == identifier3 ? True : element(identifier4, identifier5)
// objectitem : objectkey EQUAL booleanexp QMARK BOOL COLON BOOL
identifier1 = identifier2 == identifier3 ? True : False