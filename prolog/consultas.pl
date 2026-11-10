% consultas.pl - Lo que Python llama directamente
:- consult('reglas.pl').

recomendar_cliente(Nombre, Monto, Cat, Uso, Marca) :-
    retractall(presupuesto_cliente(_, _)),
    retractall(categoria_cliente(_, _)),
    retractall(uso_cliente(_, _)),
    retractall(marca_cliente(_, _)),
    assertz(presupuesto_cliente(Nombre, Monto)),
    assertz(categoria_cliente(Nombre, Cat)),
    assertz(uso_cliente(Nombre, Uso)),
    assertz(marca_cliente(Nombre, Marca)),
    forall(
        recomendar(Nombre, P),
        (precio(P,Pre), categoria(P,C), uso(P,U), stock(P,S),
         format("~w|~w|~w|~w|~w~n", [P,Pre,C,U,S]))
    ).

alternativas_cliente(Nombre, Monto, Cat, Uso, Marca) :-
    retractall(presupuesto_cliente(_, _)),
    retractall(categoria_cliente(_, _)),
    retractall(uso_cliente(_, _)),
    retractall(marca_cliente(_, _)),
    assertz(presupuesto_cliente(Nombre, Monto)),
    assertz(categoria_cliente(Nombre, Cat)),
    assertz(uso_cliente(Nombre, Uso)),
    assertz(marca_cliente(Nombre, Marca)),
    forall(
        alternativa(Nombre, P),
        (precio(P,Pre), categoria(P,C), uso(P,U), stock(P,S),
         format("~w|~w|~w|~w|~w~n", [P,Pre,C,U,S]))
    ).

catalogo_categoria(Cat) :-
    forall(
        listar_categoria(Cat, P),
        (precio(P,Pre), uso(P,U), stock(P,S),
         format("~w|~w|~w|~w|~w~n", [P,Pre,Cat,U,S]))
    ).

verificar_stock(P) :-
    (tiene_stock(P)
    -> stock(P,S), format("disponible|~w~n",[S])
    ;  format("sin_stock|0~n",[])
    ).

extras :-
    forall(
        sugerir_extra(P),
        (precio(P,Pre), categoria(P,Cat), stock(P,S),
         format("~w|~w|~w|~w~n",[P,Pre,Cat,S]))
    ).