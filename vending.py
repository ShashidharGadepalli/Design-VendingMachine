from abc import ABC, abstractmethod


class Item:

    def __init__(self, item_id, name, price):
        self._item_id = item_id
        self._name = name
        self._price = price

    def get_itemId(self):
        return self._item_id

    def get_name(self):
        return self._name

    def get_price(self):
        return self._price


class State(ABC):

    @abstractmethod
    def insert_money(self, machine, amount):
        pass

    @abstractmethod
    def select_item(self, machine, item_id):
        pass

    @abstractmethod
    def cancel(self, machine):
        pass

    @abstractmethod
    def dispense(self, machine):
        pass


class IdleState(State):

    def insert_money(self, machine, amount):
        machine.add_balance(amount)
        machine.set_state(HasMoneyState())
        return f"Balance: {machine.get_balance()}"

    def select_item(self, machine, item_id):
        return "Insert money first"

    def cancel(self, machine):
        return "Nothing to cancel"

    def dispense(self, machine):
        return "Select an item first"


class HasMoneyState(State):

    def insert_money(self, machine, amount):
        machine.add_balance(amount)
        return f"Balance: {machine.get_balance()}"

    def select_item(self, machine, item_id):
        item = machine.find(item_id)
        if item is None:
            return "Unknown item"
        if machine.get_balance() < item.get_price():
            return "Not enough money"
        machine.select(item)
        machine.set_state(DispensingState())
        return f"Selected {item.get_name()}"

    def cancel(self, machine):
        amount = machine.refund()
        machine.set_state(IdleState())
        return f"Refunded {amount}"

    def dispense(self, machine):
        return "Select an item first"


class DispensingState(State):

    def insert_money(self, machine, amount):
        return "Please wait"

    def select_item(self, machine, item_id):
        return "Please wait"

    def cancel(self, machine):
        return "Please wait"

    def dispense(self, machine):
        item, change = machine.release_item()
        if machine.get_balance()>0:
            machine.set_state(HasMoneyState())
        else:
            machine.set_state(IdleState())
        return f"Dispensed {item.get_name()}, change {change}"


class VendingMachine:

    def __init__(self):
        self._items = {}                    # item_id -> item
        self._balance = 0
        self._selected = None
        self._state = IdleState()

    def stock(self, item):
        self._items[item.get_itemId()] = item

    def insert_money(self, amount):
        return self._state.insert_money(self, amount)

    def select_item(self, item_id):
        return self._state.select_item(self, item_id)

    def cancel(self):
        return self._state.cancel(self)

    def dispense(self):
        return self._state.dispense(self)

    def get_state_name(self):
        return type(self._state).__name__

    # helpers the states use
    def set_state(self, state):
        self._state = state

    def add_balance(self, amount):
        self._balance += amount

    def get_balance(self):
        return self._balance

    def find(self, item_id):
        return self._items.get(item_id)

    def select(self, item):
        self._selected = item

    def refund(self):
        amount = self._balance
        self._balance = 0
        return amount

    def release_item(self):
        item = self._selected
        change = self._balance - item.get_price()
        self._balance -= item.get_price()
        self._selected = None
        return item, change

# The five groups: S, B, M, I, S
    #
    # 1. Setup (1)    stock
    #                 puts items in the machine
    # 2. Buttons (4)  insert_money, select_item, cancel, dispense
    #                 what the customer presses; each one only hands the press to the state
    # 3. Money (3)    add_balance, get_balance, refund
    #                 adds money, reads the money, gives the money back
    # 4. Items (3)    find, select, release_item
    #                 looks an item up, marks it as chosen, gives it out with the change
    # 5. State (2)    set_state, get_state_name
    #                 switches the state, and reports which one it is