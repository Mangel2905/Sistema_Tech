"""Carrito de compras con UNA sola regla de calculo (igual que CarritoService.scala):

    IGV      = 18% del subtotal, truncado a soles enteros
    TOTAL    = subtotal + IGV
    RESTANTE = presupuesto - TOTAL   (lo que realmente paga el cliente)
"""

IGV_PORCENTAJE = 18


class StockInsuficiente(ValueError):
    pass


class Carrito:
    def __init__(self):
        self.items = []  # [{'codigo','nombre','precio','cantidad','stock'}]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def vacio(self):
        return not self.items

    def cantidad_de(self, codigo):
        return sum(i["cantidad"] for i in self.items if i["codigo"] == codigo)

    def disponible(self, producto):
        """Unidades que aun se pueden agregar sin pasar el stock."""
        return producto["stock"] - self.cantidad_de(producto["codigo"])

    def agregar(self, producto, cantidad):
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        disp = self.disponible(producto)
        if cantidad > disp:
            raise StockInsuficiente(f"Stock insuficiente. Puedes agregar como maximo {max(disp, 0)}.")
        existente = next((i for i in self.items if i["codigo"] == producto["codigo"]), None)
        if existente:
            existente["cantidad"] += cantidad
        else:
            self.items.append({
                "codigo": producto["codigo"],
                "nombre": producto.get("nombre", producto["codigo"]),
                "precio": producto["precio"],
                "cantidad": cantidad,
                "stock": producto["stock"],
            })

    def eliminar(self, codigo):
        """Quita el producto del carrito. Devuelve el item eliminado o None."""
        for idx, item in enumerate(self.items):
            if item["codigo"] == codigo:
                return self.items.pop(idx)
        return None

    def eliminar_por_indice(self, indice):
        return self.items.pop(indice)

    def vaciar(self):
        self.items.clear()

    # ── calculos ──
    def subtotal(self):
        return sum(i["precio"] * i["cantidad"] for i in self.items)

    def igv(self):
        return self.subtotal() * IGV_PORCENTAJE // 100

    def total(self):
        return self.subtotal() + self.igv()

    def restante(self, presupuesto):
        return presupuesto - self.total()

    def resumen(self, presupuesto):
        return {
            "items": [dict(i, subtotal=i["precio"] * i["cantidad"]) for i in self.items],
            "unidades": sum(i["cantidad"] for i in self.items),
            "subtotal": self.subtotal(),
            "igv": self.igv(),
            "igv_porcentaje": IGV_PORCENTAJE,
            "total": self.total(),
            "presupuesto": presupuesto,
            "restante": self.restante(presupuesto),
        }
