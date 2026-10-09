from google_sheets_sinais import ler_sinais


def main():
    sinais = ler_sinais()

    print("\n========== SINAIS LIDOS ==========")

    for sinal in sinais:
        print(sinal)

    print(f"\nTotal de sinais: {len(sinais)}")


if __name__ == "__main__":
    main()
