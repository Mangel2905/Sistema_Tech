% reglas.pl
% Reglas lógicas de recomendación
% Define cuándo un producto es recomendado
% para un cliente según su perfil

% Cargar hechos
:- consult('hechos.pl').

% regla 1 por presupuesto y categoria
recomendar(Cliente, Producto) :-
    presupuesto(Cliente, Monto),
    precio(Producto, Precio),
    Precio =< Monto,
    categoria_cliente(Cliente, Cat),
    categoria(Producto, Cat).

% regla 2 por presupuesto, categoria y uso
recomendar_por_uso(Cliente, Producto) :-
    presupuesto(Cliente, Monto),
    precio(Producto, Precio),
    Precio =< Monto,
    categoria_cliente(Cliente, Cat),
    categoria(Producto, Cat),
    uso_cliente(Cliente, Uso),
    uso(Producto, Uso).