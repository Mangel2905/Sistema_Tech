% consultas.pl - Lo que Python llama directamente
:- consult('reglas.pl').
:- use_module(library(csv)).

% ── Stock actual ─────────────────────────────────────────────
% Python guarda el stock tras cada compra en un CSV (codigo,stock).
% Ruta: variable de entorno TECHPOS_STOCK o, por defecto, ../datos/stock.csv
% Si el archivo no existe se usa el stock inicial de hechos.pl.
:- dynamic ruta_stock_defecto/1.
:- prolog_load_context(directory, Dir),
   atomic_list_concat([Dir, '/../datos/stock.csv'], Ruta),
   assertz(ruta_stock_defecto(Ruta)).

ruta_stock(Ruta) :-
    (   getenv('TECHPOS_STOCK', Ruta), Ruta \== ''
    ->  true
    ;   ruta_stock_defecto(Ruta)
    ).

cargar_stock :-
    ruta_stock(Ruta),
    (   exists_file(Ruta)
    ->  csv_read_file(Ruta, Filas, [functor(fila), arity(2), convert(true)]),
        forall(( member(fila(Codigo, Stock), Filas), integer(Stock) ),
               ( retractall(stock(Codigo, _)), assertz(stock(Codigo, Stock)) ))
    ;   true
    ).

:- cargar_stock.

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