package app.servicios

import app.modelos.Producto

object CatalogoService {

    // Catalogo con el stock ACTUAL (stock inicial + compras registradas por Python)
    lazy val productos: List[Producto] = {
        val stockActual = StockService.cargar()
        base.map(p => stockActual.get(p.codigo).fold(p)(s => p.copy(stock = s)))
    }

    // Datos de los productos con el stock INICIAL
    val base: List[Producto] = List(

        // LAPTOPS (estudio, trabajo, gaming)
        Producto("laptop_acer_asp3",    "Acer Aspire 3",           "Acer",    1200, "laptop", "estudio", 7),
        Producto("laptop_hp_pav15",     "HP Pavilion 15",          "HP",      1500, "laptop", "estudio", 4),
        Producto("laptop_lenovo_idea",  "Lenovo IdeaPad 3",        "Lenovo",  1800, "laptop", "estudio", 5),
        Producto("laptop_asus_vivo",    "ASUS VivoBook 15",        "ASUS",    1900, "laptop", "estudio", 3),
        Producto("laptop_dell_ins15",   "Dell Inspiron 15",        "Dell",    2200, "laptop", "trabajo", 2),
        Producto("laptop_msi_gf63",     "MSI GF63 Thin",           "MSI",     2800, "laptop", "gaming",  3),

        // CELULARES
        Producto("cel_motorola_g84",    "Motorola Moto G84",       "Motorola", 750, "celular", "estudio", 7),
        Producto("cel_xiaomi_redmi",    "Xiaomi Redmi Note 12",    "Xiaomi",   800, "celular", "estudio", 10),
        Producto("cel_samsung_a54",     "Samsung Galaxy A54",      "Samsung", 1200, "celular", "estudio", 8),
        Producto("cel_iphone13",        "iPhone 13",               "Apple",   2600, "celular", "trabajo", 3),
        Producto("cel_samsung_s23",     "Samsung Galaxy S23",      "Samsung", 2900, "celular", "trabajo", 2),
        Producto("cel_iphone14",        "iPhone 14",               "Apple",   3200, "celular", "trabajo", 4),

        // TABLETS
        Producto("tab_lenovo_m10",      "Lenovo Tab M10",          "Lenovo",   650, "tablet", "estudio", 6),
        Producto("tab_samsung_a8",      "Samsung Tab A8",          "Samsung",  900, "tablet", "estudio", 5),
        Producto("tab_xiaomi_pad6",     "Xiaomi Pad 6",            "Xiaomi",  1100, "tablet", "estudio", 4),
        Producto("tab_ipad_9gen",       "iPad 9na Generacion",     "Apple",   1500, "tablet", "estudio", 3),
        Producto("tab_samsung_s7",      "Samsung Tab S7 FE",       "Samsung", 1800, "tablet", "trabajo", 2),
        Producto("tab_ipad_air",        "iPad Air",                "Apple",   2800, "tablet", "estudio", 3),

        // AURICULARES
        Producto("auri_jbl_tune510",    "JBL Tune 510BT",          "JBL",      250, "auricular", "estudio", 12),
        Producto("auri_sony_wh1000",    "Sony WH-1000XM5",         "Sony",     850, "auricular", "trabajo",  4),
        Producto("auri_bose_qc45",      "Bose QuietComfort 45",    "Bose",    1100, "auricular", "trabajo",  2),
        Producto("auri_apple_pods",     "AirPods Pro 2",           "Apple",   1200, "auricular", "trabajo",  5),
        Producto("auri_samsung_buds",   "Samsung Galaxy Buds 2",   "Samsung",  450, "auricular", "estudio",  8),
        Producto("auri_jabra_elite",    "Jabra Elite 85h",         "Jabra",    950, "auricular", "trabajo",  3),

        // ACCESORIOS
        Producto("acc_xiaomi_band8",    "Xiaomi Mi Band 8",        "Xiaomi",   180, "accesorio", "estudio", 15),
        Producto("acc_teclado_redra",   "Teclado Redragon K552",   "Redragon", 250, "accesorio", "gaming",   8),
        Producto("acc_mouse_logi",      "Mouse Logitech MX Master","Logitech", 420, "accesorio", "trabajo",  6),
        Producto("acc_samsung_watch5",  "Samsung Galaxy Watch 5",  "Samsung",  750, "accesorio", "trabajo",  5),
        Producto("acc_apple_watchse",   "Apple Watch SE",          "Apple",   1100, "accesorio", "trabajo",  3),
        Producto("acc_apple_watch9",    "Apple Watch Series 9",    "Apple",   1900, "accesorio", "trabajo",  2),

        // MONITORES
        Producto("mon_aoc_24",          "AOC 24B2XH 24\"",         "AOC",      550, "monitor", "estudio", 5),
        Producto("mon_lg_24mk",         "LG 24MK430H 24\"",        "LG",       650, "monitor", "trabajo", 4),
        Producto("mon_samsung_27t",     "Samsung 27T350 27\"",     "Samsung",  780, "monitor", "trabajo", 3),
        Producto("mon_dell_27",         "Dell S2722DC 27\"",       "Dell",    1100, "monitor", "trabajo", 2),
        Producto("mon_lg_ultraw",       "LG UltraWide 29\"",       "LG",      1400, "monitor", "trabajo", 3),
        Producto("mon_asus_rog",        "ASUS ROG Swift 27\"",     "ASUS",    2200, "monitor", "gaming",  2),

        // ALMACENAMIENTO
        Producto("alm_sandisk_usb",     "SanDisk USB 64GB",        "SanDisk",  80, "almacenamiento", "estudio", 20),
        Producto("alm_seagate_1tb",     "Seagate Externo 1TB",     "Seagate", 280, "almacenamiento", "trabajo",  9),
        Producto("alm_wd_2tb",          "WD My Passport 2TB",      "WD",      420, "almacenamiento", "trabajo",  6),
        Producto("alm_samsung_ssd",     "Samsung SSD T7 1TB",      "Samsung", 550, "almacenamiento", "trabajo",  5),
        Producto("alm_seagate_4tb",     "Seagate Externo 4TB",     "Seagate", 650, "almacenamiento", "trabajo",  3),
        Producto("alm_wd_ssd_2tb",      "WD My Passport SSD 2TB",  "WD",      950, "almacenamiento", "trabajo",  2)
    )

    def buscarPorCodigo(codigo: String): Option[Producto] =
        productos.find(_.codigo == codigo)

    def porCategoria(cat: String): List[Producto] =
        productos.filter(p => p.categoria == cat && p.stock > 0)

    def mostrarTabla(lista: List[Producto]): Unit = {
        if (lista.isEmpty) {
            println("  No se encontraron productos.")
        } else {
            println(f"\n  ${"#"}%3s  ${"Codigo"}%-22s ${"Nombre"}%-32s ${"Marca"}%-10s ${"Precio"}%8s  ${"Uso"}%-8s  ${"Stock"}%5s")
            println("  " + "-" * 100)
            lista.zipWithIndex.foreach { case (p, i) =>
                println(f"  ${i+1}%3d  ${p.codigo}%-22s ${p.nombre}%-32s ${p.marca}%-10s S/${p.precio}%6d  ${p.uso}%-8s  ${p.stock}%5d")
            }
        }
    }

    val categorias = List("laptop","celular","tablet","auricular","accesorio","monitor","almacenamiento")
    val usos = List("estudio","trabajo","gaming")
}