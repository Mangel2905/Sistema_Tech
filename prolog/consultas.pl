% consultas.pl

% Cargar hechos y reglas
:- consult('hechos.pl').
:- consult('reglas.pl').

% recomendar por presupuesto y categoria
% Uso: ?- recomendar(mangel, Producto).

%recomendar por uso
% Uso: ?- recomendar_por_uso(mangel, Producto).

% ver productos por categoria
% Uso: ?- categoria(Producto, laptop).

% ver productos de menos de 1000 soles
% Uso: ?- precio(Producto, P), P =< 1000.