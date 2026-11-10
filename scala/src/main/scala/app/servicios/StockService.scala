package app.servicios

import java.io.File
import scala.io.Source
import scala.util.Using

// Stock actual compartido con Prolog y Python.
// Python guarda el stock tras cada compra en un CSV (codigo,stock).
// Ruta: variable de entorno TECHPOS_STOCK o, por defecto, ../datos/stock.csv
// (relativa a la carpeta scala/). Si no existe se usa el stock inicial del catalogo.
object StockService {

    def ruta: String = sys.env.get("TECHPOS_STOCK").filter(_.nonEmpty).getOrElse("../datos/stock.csv")

    def cargar(): Map[String, Int] = {
        val archivo = new File(ruta)
        if (!archivo.isFile) Map.empty
        else Using.resource(Source.fromFile(archivo, "UTF-8")) { fuente =>
            fuente.getLines().flatMap { linea =>
                linea.split(",").map(_.trim) match {
                    case Array(codigo, stock) => stock.toIntOption.map(codigo -> _)
                    case _                    => None
                }
            }.toMap
        }
    }
}
