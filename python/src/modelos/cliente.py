class Cliente:
    def __init__(self, nombre, presupuesto, categoria, uso, marca="ninguna"):
        self.nombre      = nombre
        self.presupuesto = presupuesto
        self.categoria   = categoria
        self.uso         = uso
        self.marca       = marca

    def mostrar(self):
        print("\n  +------------------------------------------+")
        print(f"  | Cliente:      {self.nombre:<27}|")
        print(f"  | Presupuesto:  S/{self.presupuesto:<25}|")
        print(f"  | Categoria:    {self.categoria:<27}|")
        print(f"  | Uso:          {self.uso:<27}|")
        print(f"  | Marca:        {self.marca:<27}|")
        print("  +------------------------------------------+")