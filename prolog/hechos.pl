:- dynamic presupuesto_cliente/2.
:- dynamic categoria_cliente/2.
:- dynamic uso_cliente/2.
:- dynamic marca_cliente/2.

% Los hechos de cada producto estan en una misma linea (precio, categoria, uso,
% marca, stock); se declaran discontiguos para evitar las advertencias de SWI-Prolog.
:- discontiguous precio/2, categoria/2, uso/2, marca/2, stock/2.

% LAPTOPS
precio(laptop_acer_asp3,   1200). categoria(laptop_acer_asp3,   laptop). uso(laptop_acer_asp3,   estudio). marca(laptop_acer_asp3,   acer).    stock(laptop_acer_asp3,   7).
precio(laptop_hp_pav15,    1500). categoria(laptop_hp_pav15,    laptop). uso(laptop_hp_pav15,    estudio). marca(laptop_hp_pav15,    hp).      stock(laptop_hp_pav15,    4).
precio(laptop_lenovo_idea, 1800). categoria(laptop_lenovo_idea, laptop). uso(laptop_lenovo_idea, estudio). marca(laptop_lenovo_idea, lenovo).  stock(laptop_lenovo_idea, 5).
precio(laptop_asus_vivo,   1900). categoria(laptop_asus_vivo,   laptop). uso(laptop_asus_vivo,   estudio). marca(laptop_asus_vivo,   asus).    stock(laptop_asus_vivo,   3).
precio(laptop_dell_ins15,  2200). categoria(laptop_dell_ins15,  laptop). uso(laptop_dell_ins15,  trabajo). marca(laptop_dell_ins15,  dell).    stock(laptop_dell_ins15,  2).
precio(laptop_msi_gf63,    2800). categoria(laptop_msi_gf63,    laptop). uso(laptop_msi_gf63,    gaming).  marca(laptop_msi_gf63,    msi).     stock(laptop_msi_gf63,    3).

% CELULARES
precio(cel_motorola_g84,  750).  categoria(cel_motorola_g84,  celular). uso(cel_motorola_g84,  estudio). marca(cel_motorola_g84,  motorola). stock(cel_motorola_g84,  7).
precio(cel_xiaomi_redmi,  800).  categoria(cel_xiaomi_redmi,  celular). uso(cel_xiaomi_redmi,  estudio). marca(cel_xiaomi_redmi,  xiaomi).   stock(cel_xiaomi_redmi,  10).
precio(cel_samsung_a54,   1200). categoria(cel_samsung_a54,   celular). uso(cel_samsung_a54,   estudio). marca(cel_samsung_a54,   samsung).  stock(cel_samsung_a54,   8).
precio(cel_iphone13,      2600). categoria(cel_iphone13,      celular). uso(cel_iphone13,      trabajo). marca(cel_iphone13,      apple).    stock(cel_iphone13,      3).
precio(cel_samsung_s23,   2900). categoria(cel_samsung_s23,   celular). uso(cel_samsung_s23,   trabajo). marca(cel_samsung_s23,   samsung).  stock(cel_samsung_s23,   2).
precio(cel_iphone14,      3200). categoria(cel_iphone14,      celular). uso(cel_iphone14,      trabajo). marca(cel_iphone14,      apple).    stock(cel_iphone14,      4).

% TABLETS
precio(tab_lenovo_m10,  650).  categoria(tab_lenovo_m10,  tablet). uso(tab_lenovo_m10,  estudio). marca(tab_lenovo_m10,  lenovo).  stock(tab_lenovo_m10,  6).
precio(tab_samsung_a8,  900).  categoria(tab_samsung_a8,  tablet). uso(tab_samsung_a8,  estudio). marca(tab_samsung_a8,  samsung). stock(tab_samsung_a8,  5).
precio(tab_xiaomi_pad6, 1100). categoria(tab_xiaomi_pad6, tablet). uso(tab_xiaomi_pad6, estudio). marca(tab_xiaomi_pad6, xiaomi).  stock(tab_xiaomi_pad6, 4).
precio(tab_ipad_9gen,   1500). categoria(tab_ipad_9gen,   tablet). uso(tab_ipad_9gen,   estudio). marca(tab_ipad_9gen,   apple).   stock(tab_ipad_9gen,   3).
precio(tab_samsung_s7,  1800). categoria(tab_samsung_s7,  tablet). uso(tab_samsung_s7,  trabajo). marca(tab_samsung_s7,  samsung). stock(tab_samsung_s7,  2).
precio(tab_ipad_air,    2800). categoria(tab_ipad_air,    tablet). uso(tab_ipad_air,    estudio). marca(tab_ipad_air,    apple).   stock(tab_ipad_air,    3).

% AURICULARES
precio(auri_jbl_tune510,  250).  categoria(auri_jbl_tune510,  auricular). uso(auri_jbl_tune510,  estudio). marca(auri_jbl_tune510,  jbl).     stock(auri_jbl_tune510,  12).
precio(auri_samsung_buds, 450).  categoria(auri_samsung_buds, auricular). uso(auri_samsung_buds, estudio). marca(auri_samsung_buds, samsung). stock(auri_samsung_buds,  8).
precio(auri_sony_wh1000,  850).  categoria(auri_sony_wh1000,  auricular). uso(auri_sony_wh1000,  trabajo). marca(auri_sony_wh1000,  sony).    stock(auri_sony_wh1000,   4).
precio(auri_jabra_elite,  950).  categoria(auri_jabra_elite,  auricular). uso(auri_jabra_elite,  trabajo). marca(auri_jabra_elite,  jabra).   stock(auri_jabra_elite,   3).
precio(auri_bose_qc45,   1100).  categoria(auri_bose_qc45,   auricular). uso(auri_bose_qc45,   trabajo). marca(auri_bose_qc45,   bose).    stock(auri_bose_qc45,    2).
precio(auri_apple_pods,  1200).  categoria(auri_apple_pods,  auricular). uso(auri_apple_pods,  trabajo). marca(auri_apple_pods,  apple).   stock(auri_apple_pods,   5).

% ACCESORIOS
precio(acc_xiaomi_band8,   180).  categoria(acc_xiaomi_band8,   accesorio). uso(acc_xiaomi_band8,   estudio). marca(acc_xiaomi_band8,   xiaomi).   stock(acc_xiaomi_band8,   15).
precio(acc_teclado_redra,  250).  categoria(acc_teclado_redra,  accesorio). uso(acc_teclado_redra,  gaming).  marca(acc_teclado_redra,  redragon). stock(acc_teclado_redra,   8).
precio(acc_mouse_logi,     420).  categoria(acc_mouse_logi,     accesorio). uso(acc_mouse_logi,     trabajo). marca(acc_mouse_logi,     logitech). stock(acc_mouse_logi,      6).
precio(acc_samsung_watch5, 750).  categoria(acc_samsung_watch5, accesorio). uso(acc_samsung_watch5, trabajo). marca(acc_samsung_watch5, samsung).  stock(acc_samsung_watch5,  5).
precio(acc_apple_watchse,  1100). categoria(acc_apple_watchse,  accesorio). uso(acc_apple_watchse,  trabajo). marca(acc_apple_watchse,  apple).    stock(acc_apple_watchse,   3).
precio(acc_apple_watch9,   1900). categoria(acc_apple_watch9,   accesorio). uso(acc_apple_watch9,   trabajo). marca(acc_apple_watch9,   apple).    stock(acc_apple_watch9,    2).

% MONITORES
precio(mon_aoc_24,     550).  categoria(mon_aoc_24,     monitor). uso(mon_aoc_24,     estudio). marca(mon_aoc_24,     aoc).     stock(mon_aoc_24,     5).
precio(mon_lg_24mk,    650).  categoria(mon_lg_24mk,    monitor). uso(mon_lg_24mk,    trabajo). marca(mon_lg_24mk,    lg).      stock(mon_lg_24mk,    4).
precio(mon_samsung_27t, 780). categoria(mon_samsung_27t, monitor). uso(mon_samsung_27t, trabajo). marca(mon_samsung_27t, samsung). stock(mon_samsung_27t, 3).
precio(mon_dell_27,    1100). categoria(mon_dell_27,    monitor). uso(mon_dell_27,    trabajo). marca(mon_dell_27,    dell).    stock(mon_dell_27,    2).
precio(mon_lg_ultraw,  1400). categoria(mon_lg_ultraw,  monitor). uso(mon_lg_ultraw,  trabajo). marca(mon_lg_ultraw,  lg).      stock(mon_lg_ultraw,  3).
precio(mon_asus_rog,   2200). categoria(mon_asus_rog,   monitor). uso(mon_asus_rog,   gaming).  marca(mon_asus_rog,   asus).    stock(mon_asus_rog,   2).

% ALMACENAMIENTO
precio(alm_sandisk_usb,  80).  categoria(alm_sandisk_usb,  almacenamiento). uso(alm_sandisk_usb,  estudio). marca(alm_sandisk_usb,  sandisk). stock(alm_sandisk_usb,  20).
precio(alm_seagate_1tb, 280).  categoria(alm_seagate_1tb,  almacenamiento). uso(alm_seagate_1tb,  trabajo). marca(alm_seagate_1tb,  seagate). stock(alm_seagate_1tb,   9).
precio(alm_wd_2tb,      420).  categoria(alm_wd_2tb,       almacenamiento). uso(alm_wd_2tb,       trabajo). marca(alm_wd_2tb,       wd).      stock(alm_wd_2tb,        6).
precio(alm_samsung_ssd, 550).  categoria(alm_samsung_ssd,  almacenamiento). uso(alm_samsung_ssd,  trabajo). marca(alm_samsung_ssd,  samsung). stock(alm_samsung_ssd,   5).
precio(alm_seagate_4tb, 650).  categoria(alm_seagate_4tb,  almacenamiento). uso(alm_seagate_4tb,  trabajo). marca(alm_seagate_4tb,  seagate). stock(alm_seagate_4tb,   3).
precio(alm_wd_ssd_2tb,  950).  categoria(alm_wd_ssd_2tb,   almacenamiento). uso(alm_wd_ssd_2tb,   trabajo). marca(alm_wd_ssd_2tb,   wd).      stock(alm_wd_ssd_2tb,    2).