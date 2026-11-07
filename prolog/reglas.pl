% reglas.pl - Reglas de recomendacion
:- consult('hechos.pl').

disponible(P) :-
    stock(P, S), S > 0.

cumple_marca(_, Cliente) :-
    marca_cliente(Cliente, ninguna), !.
cumple_marca(P, Cliente) :-
    marca_cliente(Cliente, M),
    marca(P, M).

recomendar(Cliente, P) :-
    presupuesto_cliente(Cliente, Monto),
    categoria_cliente(Cliente, Cat),
    uso_cliente(Cliente, Uso),
    precio(P, Precio),
    Precio =< Monto,
    categoria(P, Cat),
    uso(P, Uso),
    disponible(P),
    cumple_marca(P, Cliente).

alternativa(Cliente, P) :-
    presupuesto_cliente(Cliente, Monto),
    categoria_cliente(Cliente, Cat),
    uso_cliente(Cliente, Uso),
    Limite is round(Monto * 1.2),
    precio(P, Precio),
    Precio > Monto,
    Precio =< Limite,
    categoria(P, Cat),
    uso(P, Uso),
    disponible(P),
    cumple_marca(P, Cliente).

sugerir_extra(P) :-
    categoria(P, accesorio),
    precio(P, Precio),
    Precio =< 500,
    disponible(P).

listar_categoria(Cat, P) :-
    categoria(P, Cat),
    disponible(P).

tiene_stock(P) :-
    stock(P, S), S > 0.