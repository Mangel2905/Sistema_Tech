% ============================================
% hechos.pl
% Base de conocimientos del sistema
% Define los hechos sobre productos y clientes
% ============================================

% --- PRECIOS de productos ---
precio(laptop_lenovo, 1800).
precio(laptop_hp, 1500).
precio(laptop_asus, 1900).
precio(laptop_dell, 2200).
precio(iphone14, 3200).
precio(samsung_a54, 1200).
precio(xiaomi_redmi, 800).
precio(ipad_air, 2800).
precio(samsung_tab, 900).
precio(sony_wh1000, 850).
precio(jbl_tune, 250).
precio(apple_watch, 1100).
precio(samsung_watch, 750).
precio(teclado_redragon, 250).
precio(mouse_logitech, 180).

% --- CATEGORÍAS de productos ---
categoria(laptop_lenovo, laptop).
categoria(laptop_hp, laptop).
categoria(laptop_asus, laptop).
categoria(laptop_dell, laptop).
categoria(iphone14, celular).
categoria(samsung_a54, celular).
categoria(xiaomi_redmi, celular).
categoria(ipad_air, tablet).
categoria(samsung_tab, tablet).
categoria(sony_wh1000, audifono).
categoria(jbl_tune, audifono).
categoria(apple_watch, smartwatch).
categoria(samsung_watch, smartwatch).
categoria(teclado_redragon, accesorio).
categoria(mouse_logitech, accesorio).

% --- USO de productos ---
uso(laptop_lenovo, estudio).
uso(laptop_hp, estudio).
uso(laptop_asus, trabajo).
uso(laptop_dell, trabajo).
uso(iphone14, casual).
uso(samsung_a54, casual).
uso(xiaomi_redmi, casual).
uso(ipad_air, estudio).
uso(samsung_tab, estudio).
uso(sony_wh1000, trabajo).
uso(jbl_tune, casual).
uso(apple_watch, casual).
uso(samsung_watch, casual).
uso(teclado_redragon, gaming).
uso(mouse_logitech, gaming).

% --- CLIENTES de prueba ---
presupuesto(mangel, 2000).
categoria_cliente(mangel, laptop).
uso_cliente(mangel, estudio).