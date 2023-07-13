from typing import Tuple
from threading import Lock,Semaphore
from globals import *
from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction, TransactionStatus
from utils.currency import Currency, get_exchange_rate
from utils.logger import LOGGER
from datetime import datetime, timedelta
class Bank():
    """
    Uma classe para representar um Banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do banco.
    currency : Currency
        Moeda corrente das contas bancárias do banco.
    reserves : CurrencyReserves
        Dataclass de contas bancárias contendo as reservas internas do banco.
    operating : bool
        Booleano que indica se o banco está em funcionamento ou não.
    accounts : List[Account]
        Lista contendo as contas bancárias dos clientes do banco.
    transaction_queue : Queue[Transaction]
        Fila FIFO contendo as transações bancárias pendentes que ainda serão processadas.
    
    ---Atributos Criados---
    n_nat_transfers : Int
        Registra o Numero de Transferencias Nacionais
    n_inter_transfers : Int
        Registra o Numero de Transferencias Internacionais
    profits : Int
        Registra o Lucro do Banco
    transactions_total_time : timedelta
        Registra o Tempo Total das Transações Daquele Banco       
    semaforo_transactions : Semaphore
        Semaforo Para Identificar se Há ou Não Transações na Fila para Processamento (transaction_queue)
    reserves_mutex: Lock
        Para proteger as reservas do banco. (Região crítica)
    queue_lock:  Lock
        Para proteger a fila do banco. (Região crítica)
    mutex_account: Lock
        Para proteger o acesso a contas do banco (Região crítica)
    protect_variable: Lock
        Para proteger as variáveis contadoras que serão printadas (Região crítica)


    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_national_transfer(self,origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency, transaction: Transaction) -> None:
        Cria uma nova transação bancária nacional.
    new_international_transfer(self,origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency, transaction: Transaction) -> None:
        Cria uma nova transação bancária internacional.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.
        
    """

    def __init__(self, _id: int, currency: Currency, mutex: Lock):
        self._id                = _id
        self.currency           = currency
        self.reserves           = CurrencyReserves(_id)
        self.reserves_mutex     = Lock()
        self.operating          = False
        self.accounts           = []
        self.transaction_queue  = []
        self.queue_lock         = Lock()
        self.mutex_account      = mutex
        self.semaforo_transactions = Semaphore(value=0)
        self.protect_variables  = Lock()
        
        #Variáveis Printadas
        self.n_nat_transfers    = 0
        self.n_inter_transfers  = 0
        self.profits            = 0
        self.transactions_total_time  =  0

    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado 
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account
        acc_id = len(self.accounts) + 1

        # Cria instância da classe Account
        acc = Account(_id=acc_id, _bank_id=self._id, currency=self.currency, balance=balance, overdraft_limit=overdraft_limit)
  
        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)


    def info(self) -> None:
        """
        Essa função deverá printar os seguintes dados utilizando o LOGGER fornecido:
        1. Saldo de cada moeda nas reservas internas do banco
        2. Número de transferências nacionais e internacionais realizadas
        3. Número de contas bancárias registradas no banco
        4. Saldo total de todas as contas bancárias (dos clientes) registradas no banco
        5. Lucro do banco: taxas de câmbio acumuladas + juros de cheque especial acumulados
        6. Quantidade de transações na lista de espera
        7. Tempo médio que as transações demoraram para serem processadas. 
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        print("\n\n\n\n")
        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:")
        
        print("\n")
        LOGGER.info(f"Saldo das Reservas Internas de Cada Moeda:")
        LOGGER.info(f"Reservas de USD = {self.reserves.USD.balance}")
        LOGGER.info(f"Reservas de EUR = {self.reserves.EUR.balance}")
        LOGGER.info(f"Reservas de GBP = {self.reserves.GBP.balance}")
        LOGGER.info(f"Reservas de JPY = {self.reserves.JPY.balance}")
        LOGGER.info(f"Reservas de CHF = {self.reserves.CHF.balance}")
        LOGGER.info(f"Reservas de BRL = {self.reserves.BRL.balance}")
        
        print("\n")
        LOGGER.info(f"Número de Transferências Processadas por Categoria:")
        LOGGER.info(f"Transferências Nacionais: {self.n_nat_transfers}")
        LOGGER.info(f"Transferências Internacionais: {self.n_inter_transfers}")
        
        print("\n")
        LOGGER.info(f"Número de Contas Bancárias Registradas no Banco: {len(self.accounts)}")

        total_balance = 0
        i = 0
        for account in self.accounts:
            total_balance += account.balance
            i += 1
            
        LOGGER.info(f"Saldo Total das Contas Registradas no Banco: {total_balance}" )
        LOGGER.info(f"Lucro do Banco: {self.profits}")
        LOGGER.info(f"Quantidade de Transações Na Lista de Espera: {len(self.transaction_queue)}")

        if self.n_nat_transfers + self.n_inter_transfers != 0:
            LOGGER.info(f"Tempo Médio de Processamento das Transações do Banco: {self.transactions_total_time/(self.n_nat_transfers + self.n_inter_transfers)} segundos")
        else:
            LOGGER.info(f"Tempo Médio de Proessamento das Transações do Banco: {0.0} segundos")
        


    #Transacoes nacionais ou internacionais e atualizar o doc string
    def new_nacional_transfer(self,origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency, transaction: Transaction) -> None:
        permitir_transacao = True
        taxas_transacao = 0
        conta_origem = banks[origin[0]].accounts[origin[1]]

        self.mutex_account.acquire()
        if conta_origem.balance > 0:
            if conta_origem.balance - amount > 0:
                pass
            else:
                if  (amount + 0.05*abs(conta_origem.balance - amount)) <= conta_origem.balance + conta_origem.overdraft_limit:
                    taxas_transacao = 0.05*abs(conta_origem.balance - amount)
                else:
                    permitir_transacao = False
        else:
            if  conta_origem.overdraft_limit + conta_origem.balance >= 1.05*amount:
                taxas_transacao = 0.05 * amount

            else:
                permitir_transacao = False



        if permitir_transacao == True:
            conta_origem.withdraw(amount + taxas_transacao)
            self.mutex_account.release()
            
            with banks[destination[0]].mutex_account:
                banks[destination[0]].accounts[destination[1]].deposit(amount) #as taxas deposita na conta do banco

            if self.currency == 1:
                depositar_reserva = self.reserves.USD.deposit
            elif self.currency == 2:
                depositar_reserva = self.reserves.EUR.deposit
            elif self.currency == 3:
                depositar_reserva = self.reserves.GBP.deposit
            elif self.currency == 4:
                depositar_reserva = self.reserves.JPY.deposit
            elif self.currency == 5:
                depositar_reserva = self.reserves.CHF.deposit
            else:
                depositar_reserva = self.reserves.BRL.deposit


            with self.reserves_mutex:
                depositar_reserva(taxas_transacao)

            transaction.set_status(TransactionStatus.SUCCESSFUL)
            
            self.protect_variables.acquire()
            self.profits += taxas_transacao
            self.n_nat_transfers += 1
            self.transactions_total_time += transaction.get_processing_time().total_seconds()
            self.protect_variables.release()
            
        else:
            transaction.set_status(TransactionStatus.FAILED)
            LOGGER.warning(f"withdraw({amount}) failed, no balance!")
            self.mutex_account.release()
            
            self.protect_variables.acquire()
            
            self.transactions_total_time += transaction.get_processing_time().total_seconds()
            self.protect_variables.release()



    def new_international_transfer(self,origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency, transaction: Transaction) -> None:

        if currency == 1:
            depositar_reserva = self.reserves.USD.deposit
            retirar_reserva = self.reserves.USD.withdraw
        elif currency == 2:
            depositar_reserva = self.reserves.EUR.deposit
            retirar_reserva = self.reserves.EUR.withdraw
        elif currency == 3:
            depositar_reserva = self.reserves.GBP.deposit
            retirar_reserva =  self.reserves.GBP.withdraw
        elif currency == 4:
            depositar_reserva = self.reserves.JPY.deposit
            retirar_reserva = self.reserves.JPY.withdraw
        elif currency == 5:
            depositar_reserva = self.reserves.CHF.deposit
            retirar_reserva = self.reserves.CHF.withdraw
        else:
            depositar_reserva = self.reserves.BRL.deposit
            retirar_reserva = self.reserves.BRL.withdraw

        if self.currency == 1:
            depositar_taxas = self.reserves.USD.deposit
 
        elif self.currency == 2:
            depositar_taxas = self.reserves.EUR.deposit

        elif self.currency == 3:
            depositar_taxas = self.reserves.GBP.deposit

        elif self.currency == 4:
            depositar_taxas = self.reserves.JPY.deposit

        elif self.currency == 5:
            depositar_taxas = self.reserves.CHF.deposit
        else:
            depositar_taxas = self.reserves.BRL.deposit


        conversao = get_exchange_rate(self.currency, banks[destination[0]].currency)

        permitir_transacao = True
        taxas_transacao = 0
        conta_origem = banks[origin[0]].accounts[origin[1]]

        self.mutex_account.acquire()
        if conta_origem.balance > 0:
            if conta_origem.balance - 1.01 * amount > 0:
                taxas_transacao = 0.01 * amount
            else:
                if 1.01 * (amount + 0.05 * abs(conta_origem.balance - amount)) <= conta_origem.balance + conta_origem.overdraft_limit:
                    taxas_transacao = 0.05 * abs(conta_origem.balance - amount) + 0.01 * (amount + 0.05 * abs(conta_origem.balance - amount))
                else:
                    permitir_transacao = False
        else:

            if conta_origem.overdraft_limit + conta_origem.balance >= 1.01*(1.05 * amount):
                taxas_transacao = 0.05 * amount + 0.01 * (1.05 * amount)

            else:
                permitir_transacao = False


        if permitir_transacao == True:
            dinheiro_convertido = (amount) * conversao
            conta_origem.withdraw(amount + taxas_transacao)
            self.mutex_account.release()

            self.reserves_mutex.acquire()
            depositar_reserva(dinheiro_convertido)
            depositar_taxas(taxas_transacao)
            retirar_reserva(dinheiro_convertido)
            self.reserves_mutex.release()

            with banks[destination[0]].mutex_account:
                banks[destination[0]].accounts[destination[1]].deposit(dinheiro_convertido)
                transaction.set_status(TransactionStatus.SUCCESSFUL) 
            self.protect_variables.acquire()
            self.profits += taxas_transacao
            self.n_inter_transfers += 1
            self.transactions_total_time += transaction.get_processing_time().total_seconds()
            self.protect_variables.release()
        else:
            transaction.set_status(TransactionStatus.FAILED)
            LOGGER.warning(f"withdraw({amount}) failed, no balance!")
            self.mutex_account.release()

            self.protect_variables.acquire()
           
            self.transactions_total_time += transaction.get_processing_time().total_seconds()
            self.protect_variables.release()


