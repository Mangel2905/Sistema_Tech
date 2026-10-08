% ============================================
% reglas.pl
% Reglas lógicas de recomendación
% Define cuándo un producto es recomendado
% para un cliente según su perfil
% ============================================

% Cargar hechos
:- consult('hechos.pl').

% --- REGLA 1 ---
% Recomienda por presupuesto y categoría
% Un producto es recomendado si:
% - El precio está dentro del presupuesto
% - La categoría coincide con la del cliente
recomendar(Cliente, Producto) :-
    presupuesto(Cliente, Monto),
    precio(Producto, Precio),
    Precio =< Monto,
    categoria_cliente(Cliente, Cat),
    categoria(Producto, Cat).

% --- REGLA 2 ---
% Recomienda por presupuesto, categoría y uso
% Un producto es recomendado si además
% el uso coincide con el del cliente
recomendar_por_uso(Cliente, Producto) :-
    presupuesto(Cliente, Monto),
    precio(Producto, Precio),
    Precio =< Monto,
    categoria_cliente(Cliente, Cat),
    categoria(Producto, Cat),
    uso_cliente(Cliente, Uso),
    uso(Producto, Uso).