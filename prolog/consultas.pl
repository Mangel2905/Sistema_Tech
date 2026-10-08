% ============================================
% consultas.pl
% Consultas de prueba del sistema
% Aquí se realizan las preguntas al motor
% de inferencia de Prolog
% ============================================

% Cargar hechos y reglas
:- consult('hechos.pl').
:- consult('reglas.pl').

% --- CONSULTA 1 ---
% ¿Qué productos están dentro del presupuesto
% y categoría del cliente mangel?
% Uso: ?- recomendar(mangel, Producto).

% --- CONSULTA 2 ---
% ¿Qué productos coinciden además con el uso
% principal del cliente mangel?
% Uso: ?- recomendar_por_uso(mangel, Producto).

% --- CONSULTA 3 ---
% ¿Qué productos existen en la categoría laptop?
% Uso: ?- categoria(Producto, laptop).

% --- CONSULTA 4 ---
% ¿Qué productos cuestan menos de 1000 soles?
% Uso: ?- precio(Producto, P), P =< 1000.