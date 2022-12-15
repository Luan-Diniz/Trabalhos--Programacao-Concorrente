import argparse, time, sys
from logging import INFO, DEBUG
from random import randint

from globals import *
from payment_system.bank import Bank
from payment_system.payment_processor import PaymentProcessor
from payment_system.transaction_generator import TransactionGenerator
from utils.currency import Currency
from utils.logger import CH, LOGGER

from threading import Lock

if __name__ == "__main__":
    # Verificação de compatibilidade da versão do python:
    if sys.version_info < (3, 5):
        sys.stdout.write('Utilize o Python 3.5 ou mais recente para desenvolver este trabalho.\n')
        sys.exit(1)

    # Captura de argumentos da linha de comando:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_unit", "-u", help="Valor da unidade de tempo de simulação")
    parser.add_argument("--total_time", "-t", help="Tempo total de simulação")
    parser.add_argument("--debug", "-d", help="Printar logs em nível DEBUG")
    args = parser.parse_args()
    if args.time_unit:
        time_unit = float(args.time_unit)
    if args.total_time:
        total_time = int(args.total_time)
    if args.debug:
        debug = True

    # Configura logger
    if debug:
        LOGGER.setLevel(DEBUG)
        CH.setLevel(DEBUG)
    else:
        LOGGER.setLevel(INFO)
        CH.setLevel(INFO)

    # Printa argumentos capturados da simulação
    LOGGER.info(f"Iniciando simulação com os seguintes parâmetros:\n\ttotal_time = {total_time}\n\tdebug = {debug}\n")
    time.sleep(3)

    # Inicializa variável `tempo`:
    t = 0

    mutex_banco_0 = Lock()
    mutex_banco_1 = Lock()
    mutex_banco_2 = Lock()
    mutex_banco_3 = Lock()
    mutex_banco_4 = Lock()
    mutex_banco_5 = Lock()

    mutexes_bancos = [mutex_banco_0,mutex_banco_1,mutex_banco_2,mutex_banco_3,mutex_banco_4,mutex_banco_5]

    # Cria os Bancos Nacionais e popula a lista global `banks`:
    for i, currency in enumerate(Currency):
        
        # Cria Banco Nacional
        bank = Bank(_id=i, currency=currency, mutex = mutexes_bancos[i])
        
        # Deposita valores aleatórios nas contas internas (reserves) do banco
        bank.reserves.BRL.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.CHF.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.EUR.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.GBP.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.JPY.deposit(randint(100_000_000, 10_000_000_000))
        bank.reserves.USD.deposit(randint(100_000_000, 10_000_000_000))
        
        # Adiciona banco na lista global de bancos
        banks.append(bank)
    
    #Cria contas para cada banco E inicializa as operações
    for bank in banks:
        for i in range(100):
            bank.new_account(randint(0, 1000000), randint(500, 50000))
        bank.operating = True

    # Inicializa gerador de transações e processadores de pagamentos para os Bancos Nacionais:
    transactions_list = []
    payment_pro_list = []

    for i, bank in enumerate(banks):
        # Inicializa um TransactionGenerator thread por banco:
        transaction_gen = TransactionGenerator(_id=i, bank=bank)
        transactions_list.append(transaction_gen)
        transaction_gen.start()
        
        # Inicializa um PaymentProcessor thread por banco.
        # Sua solução completa deverá funcionar corretamente com múltiplos PaymentProcessor threads para cada banco.

        for j in range(10):      #Alterar Depois
            payment_pro = PaymentProcessor(_id=10*i+j, bank=bank)
            payment_pro_list.append(payment_pro)
            payment_pro.start()
        
    # Enquanto o tempo total de simuação não for atingido:
    while t < total_time:
        dt = randint(0, 3)
        time.sleep(dt * time_unit)
        t += dt
    
    for bank in banks:
        bank.operating = False

    # Finaliza todas as threads
    for transaction in transactions_list:
        transaction.join()
    
    for bank in banks:
        for i in range (10):
            bank.semaforo_transactions.release()    #Evita deadlocks no final liberando as últimas payment processors

    for payment_processor in payment_pro_list:
        payment_processor.join()
    
    # Termina simulação. Após esse print somente dados devem ser printados no console.
    LOGGER.info(f"A simulação chegou ao fim!\n")
    

    for bank in banks:
        bank.info()
    print()
