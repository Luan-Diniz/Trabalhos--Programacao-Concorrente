from random import randint
import time
from threading import Thread

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER


class TransactionGenerator(Thread):
    """
    Uma classe para gerar e simular clientes de um banco por meio da geracão de transações bancárias.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do gerador de transações.
    bank: Bank
        Banco sob o qual o gerador de transações operará.

    Métodos
    -------
    run():
        ....
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id  = _id
        self.bank = bank


    def run(self):
        """
        Esse método deverá gerar transacões aleatórias enquanto o banco (self._bank_id)
        estiver em operação.
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        LOGGER.info(f"Inicializado TransactionGenerator para o Banco Nacional {self.bank._id}!")

        i = 0
        while banks[self.bank._id].operating:
            origin = (self.bank._id, randint(0,99))
            destination_bank = randint(0, 5)
            destination = (destination_bank, randint(0, 99))      
            amount = randint(100, 100000)
            new_transaction = Transaction(i, origin, destination, amount, currency=Currency(destination_bank+1))
            with banks[self.bank._id].queue_lock:
                banks[self.bank._id].transaction_queue.append(new_transaction)
                LOGGER.info(f"Transaction_queue do Banco {self.bank._id}: {len(self.bank.transaction_queue)}")
                banks[self.bank._id].semaforo_transactions.release()
            
            i += 1
            time.sleep(0.2 * time_unit)

        LOGGER.info(f"O TransactionGenerator {self._id} do banco {self.bank._id} foi finalizado.")

