package app.servicios

import app.modelos.Producto

// Serializacion JSON minima (sin dependencias externas) para que Python
// consuma el catalogo y los reportes como datos estructurados.
object JsonService {

    private def texto(s: String): String = {
        val sb = new StringBuilder("\"")
        s.foreach {
            case '"'  => sb.append("\\\"")
            case '\\' => sb.append("\\\\")
            case '\n' => sb.append("\\n")
            case '\r' => sb.append("\\r")
            case '\t' => sb.append("\\t")
            case c if c < ' ' || c > '~' => sb.append(f"\\u${c.toInt}%04x")
            case c    => sb.append(c)
        }
        sb.append('"').toString
    }

    def producto(p: Producto): String =
        s"""{"codigo":${texto(p.codigo)},"nombre":${texto(p.nombre)},"marca":${texto(p.marca)},""" +
        s""""precio":${p.precio},"categoria":${texto(p.categoria)},"uso":${texto(p.uso)},"stock":${p.stock}}"""

    def productos(lista: List[Producto]): String =
        lista.map(producto).mkString("[", ",", "]")

    def reporte(lista: List[Producto]): String = {
        val stockBajo = productos(ReporteService.stockBajo(lista))
        val resumen = ReporteService.resumen(lista).map { r =>
            val barato = r.masBarato.map(producto).getOrElse("null")
            s"""{"categoria":${texto(r.categoria)},"cantidad":${r.cantidad},"masCaro":${producto(r.masCaro)},"masBarato":$barato}"""
        }.mkString("[", ",", "]")
        val agotados = productos(ReporteService.agotados(lista))
        s"""{"stockBajo":$stockBajo,"agotados":$agotados,"resumen":$resumen}"""
    }
}
