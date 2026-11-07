from integracion.prolog_service import recomendar, alternativas, catalogo_categoria, extras
from integracion.scala_service   import listar_todo, listar_categoria, reporte

NOMBRES = {
    # laptops
    "laptop_acer_asp3":    "Acer Aspire 3",
    "laptop_hp_pav15":     "HP Pavilion 15",
    "laptop_lenovo_idea":  "Lenovo IdeaPad 3",
    "laptop_asus_vivo":    "ASUS VivoBook 15",
    "laptop_dell_ins15":   "Dell Inspiron 15",
    "laptop_msi_gf63":     "MSI GF63 Thin",
    # celulares
    "cel_motorola_g84":    "Motorola Moto G84",
    "cel_xiaomi_redmi":    "Xiaomi Redmi Note 12",
    "cel_samsung_a54":     "Samsung Galaxy A54",
    "cel_iphone13":        "iPhone 13",
    "cel_samsung_s23":     "Samsung Galaxy S23",
    "cel_iphone14":        "iPhone 14",
    # tablets
    "tab_lenovo_m10":      "Lenovo Tab M10",
    "tab_samsung_a8":      "Samsung Tab A8",
    "tab_xiaomi_pad6":     "Xiaomi Pad 6",
    "tab_ipad_9gen":       "iPad 9na Generacion",
    "tab_samsung_s7":      "Samsung Tab S7 FE",
    "tab_ipad_air":        "iPad Air",
    # auriculares
    "auri_jbl_tune510":    "JBL Tune 510BT",
    "auri_samsung_buds":   "Samsung Galaxy Buds 2",
    "auri_sony_wh1000":    "Sony WH-1000XM5",
    "auri_jabra_elite":    "Jabra Elite 85h",
    "auri_bose_qc45":      "Bose QuietComfort 45",
    "auri_apple_pods":     "AirPods Pro 2",
    # accesorios
    "acc_xiaomi_band8":    "Xiaomi Mi Band 8",
    "acc_teclado_redra":   "Teclado Redragon K552",
    "acc_mouse_logi":      "Mouse Logitech MX Master",
    "acc_samsung_watch5":  "Samsung Galaxy Watch 5",
    "acc_apple_watchse":   "Apple Watch SE",
    "acc_apple_watch9":    "Apple Watch Series 9",
    # monitores
    "mon_aoc_24":          "AOC 24B2XH 24\"",
    "mon_lg_24mk":         "LG 24MK430H 24\"",
    "mon_samsung_27t":     "Samsung 27T350 27\"",
    "mon_dell_27":         "Dell S2722DC 27\"",
    "mon_lg_ultraw":       "LG UltraWide 29\"",
    "mon_asus_rog":        "ASUS ROG Swift 27\"",
    # almacenamiento
    "alm_sandisk_usb":     "SanDisk USB 64GB",
    "alm_seagate_1tb":     "Seagate Externo 1TB",
    "alm_wd_2tb":          "WD My Passport 2TB",
    "alm_samsung_ssd":     "Samsung SSD T7 1TB",
    "alm_seagate_4tb":     "Seagate Externo 4TB",
    "alm_wd_ssd_2tb":      "WD My Passport SSD 2TB",
}

def nombre(codigo):
    return NOMBRES.get(codigo, codigo)

def buscar_recomendaciones(cliente):
    productos = recomendar(cliente)
    es_alternativa = False
    if not productos:
        productos = alternativas(cliente)
        es_alternativa = True
    return productos, es_alternativa

def mostrar_productos(lista):
    if not lista:
        print("  Sin resultados.")
        return
    print(f"\n  {'#':>3}  {'Codigo':<22} {'Nombre':<32} {'Precio':>8}  {'Uso':<8}  Stock")
    print("  " + "-" * 85)
    for i, p in enumerate(lista, 1):
                print(f"  {i:>3}  {p['codigo']:<22} {nombre(p['codigo']):<32} S/{p['precio']:>6}  {p.get('uso', 'accesorio'):<8}  {p['stock']}")