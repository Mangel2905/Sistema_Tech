package app.servicios

import app.modelos.Cliente

object ClienteService {

    def registrar(): Cliente = {
        println("\n  === Registro ===")
        val nombre      = Validacion.pedirTexto("  Tu nombre: ")
        val presupuesto = Validacion.pedirPresupuesto("  Presupuesto (S/): ")
        println(s"  Categorias: ${CatalogoService.categorias.mkString(", ")}")
        val categoria   = Validacion.pedirOpcion("  Que buscas: ", CatalogoService.categorias)
        val uso         = Validacion.pedirOpcion("  Para que (estudio/trabajo/gaming): ", CatalogoService.usos)
        println("  Marca preferida o escribe 'ninguna'")
        val marca       = Validacion.pedirTexto("  Marca: ").toLowerCase
        Cliente(nombre, presupuesto, categoria, uso, marca)
    }

    def mostrar(c: Cliente): Unit = {
        println("\n  +------------------------------------------+")
        println(f"  | Cliente:      ${c.nombre}%-27s|")
        println(f"  | Presupuesto:  S/${c.presupuesto}%-25d|")
        println(f"  | Categoria:    ${c.categoria}%-27s|")
        println(f"  | Uso:          ${c.uso}%-27s|")
        println(f"  | Marca:        ${c.marca}%-27s|")
        println("  +------------------------------------------+")
    }
}