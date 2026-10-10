# Cores ANSI para o terminal

AZUL = "\033[34m"
VERDE = "\033[32m"
AMARELO = "\033[33m"
VERMELHO = "\033[31m"
CIANO = "\033[36m"
NEGRITO = "\033[1m"
RESET = "\033[0m"


def titulo(texto):
    print(f"\n{AZUL}{NEGRITO} {texto} {RESET}")


def sucesso(texto):
    print(f"{VERDE}✓ {texto}{RESET}")


def aviso(texto):
    print(f"{AMARELO}⚠ {texto}{RESET}")


def error(texto):
    print(f"{VERMELHO}✗ {texto}{RESET}")


def info(texto):
    print(f"{CIANO}{texto}{RESET}")