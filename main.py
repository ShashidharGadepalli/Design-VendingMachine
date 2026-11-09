from vending import VendingMachine, Item

machine = VendingMachine()
machine.stock(Item(1, "Cola", 10))
machine.stock(Item(2, "Chips", 6))

print(machine.select_item(1))
print(machine.insert_money(20))
print(machine.select_item(1))
print(machine.dispense())
print(machine.select_item(2))
print(machine.dispense())
print(machine.cancel())
print(machine.get_state_name())