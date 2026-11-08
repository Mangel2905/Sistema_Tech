error id: file:///C:/Users/Mangel/Documents/AGOSTO%202026/LENGUAJES%20DE%20PROGRAMACION/Sistema_Tech/scala/src/main/scala/app/servicios/ClienteService.scala:app/modelos/Cliente#marca.
file:///C:/Users/Mangel/Documents/AGOSTO%202026/LENGUAJES%20DE%20PROGRAMACION/Sistema_Tech/scala/src/main/scala/app/servicios/ClienteService.scala
empty definition using pc, found symbol in pc: 
found definition using semanticdb; symbol app/modelos/Cliente#marca.
empty definition using fallback
non-local guesses:

offset: 1177
uri: file:///C:/Users/Mangel/Documents/AGOSTO%202026/LENGUAJES%20DE%20PROGRAMACION/Sistema_Tech/scala/src/main/scala/app/servicios/ClienteService.scala
text:
```scala
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
        println(f"  | Marca:        ${c.m@@arca}%-27s|")
        println("  +------------------------------------------+")
    }
}
```


#### Short summary: 

empty definition using pc, found symbol in pc: 