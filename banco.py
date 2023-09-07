import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Usuario:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Usuario):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, usuario):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._usuario = usuario
        self._historico = Historico()
    @classmethod
    def nova_conta(cls, usuario, numero):
        return cls(numero, usuario)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def usuario(self):
        return self._usuario

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n Operação falhou! Você não tem saldo suficiente. ")

        elif valor > 0:
            self._saldo -= valor
            print("\n Saque realizado com sucesso! ")
            return True

        else:
            print("\n Operação falhou! O valor informado é inválido. ")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n Depósito realizado com sucesso! ")
        else:
            print("\n Operação falhou! O valor informado é inválido. ")
            return False

        return True
class ContaCorrente(Conta):
    def __init__(self, numero, usuario, limite=500, limite_saques=3):
        super().__init__(numero, usuario)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n Operação falhou! O valor do saque excede o limite. ")

        elif excedeu_saques:
            print("\n Operação falhou! Número máximo de saques excedido. ")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.usuario.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = """\n
--------Bem Vindo ao Seu Banco --------
======Digite o serviço desejado:=======
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [7]\tSair
    => """
    return input(textwrap.dedent(menu))

def depositar(usuarios):
    cpf = input("Informe o CPF do usuário (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("\n Usuário não encontrado! ")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    usuario.realizar_transacao(conta, transacao)

def sacar(usuarios):
    cpf = input("Informe o CPF do usuário (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("\n Usuário não encontrado! ")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    usuario.realizar_transacao(conta, transacao)

def exibir_extrato(usuarios):
    cpf = input("Informe o CPF do usuario (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("\n Usuário não encontrado! ")
        return

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def recuperar_conta_usuario(usuario):
    if not usuario.contas:
        print("\n Usuário não possui conta! ")
        return

    # FIXME: não permite usuario escolher a conta
    return usuario.contas[0]

def criar_conta(contas, numero_conta, usuarios):
    cpf = input("Informe o CPF do usuário (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("\nUsuário não encontrado. O fluxo de criação de conta foi encerrado. ")
        return
    
    conta = ContaCorrente.nova_conta(usuario=usuario, numero=numero_conta)
    contas.append(conta)
    usuario.contas.append(conta)

    print("\n Conta criada com sucesso! ")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n Já existe um usuário com esse CPF! ")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuario = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    usuarios.append(usuario)

    print("\n Usuário criado com sucesso! ")


def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(usuarios)
        elif opcao == "2":
            sacar(usuarios)
        elif opcao == "3":
            exibir_extrato(usuarios)
        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)
        elif opcao == "5":
            listar_contas(contas)
        elif opcao == "6":
            criar_usuario(usuarios)
        elif opcao == "7":
            break

        else:
            print("\n Operação inválida. Selecione novamente a operação desejada.")

main()