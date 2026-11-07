package app.modelos

case class ItemCarrito(producto: Producto, cantidad: Int) {
    def subtotal: Int = producto.precio * cantidad
}