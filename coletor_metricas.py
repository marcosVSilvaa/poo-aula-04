import psutil
import csv
import time
from datetime import datetime
import sys
import argparse

class Metrica:
    """
    Classe base que define a estrutura comum de uma métrica.
    Define os atributos 'unidade' e 'valor' (Requisito 2).
    """
    def __init__(self, nome, unidade):
        self.nome = nome
        self.unidade = unidade
        self.valor = None
    
    def coletar_valor(self):
        """Método a ser implementado por cada subclasse para coletar o valor."""
        raise NotImplementedError("O método 'coletar_valor' deve ser implementado nas subclasses.")

    def obter_dados(self):
        """Coleta o valor e retorna os dados formatados para o CSV (Requisito 4)."""
        self.coletar_valor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return [agora, self.nome, self.valor, self.unidade]

class CpuMetrica(Metrica):
    """Subclasse que retorna o uso da CPU em porcentagem."""
    def __init__(self):
        super().__init__("CPU", "%") 
    
    def coletar_valor(self):
        self.valor = psutil.cpu_percent(interval=None) 
        
class MemoriaMetrica(Metrica):
    """Subclasse que retorna o uso de memória em MB."""
    def __init__(self):
        super().__init__("Memoria", "MB")
    
    def coletar_valor(self):
        mem = psutil.virtual_memory()
        self.valor = round(mem.used / (1024 * 1024))

class DiscoMetrica(Metrica):
    """Subclasse que retorna o espaço livre em disco em MB."""
    def __init__(self):
        super().__init__("Disco", "MB")
        
    def coletar_valor(self):
        disk = psutil.disk_usage('/')
        self.valor = round(disk.free / (1024 * 1024))

def salvar_dados_csv(arquivo_saida, dados):
    """Salva a lista de dados coletados em um arquivo CSV."""
    with open(arquivo_saida, mode="a", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        if arquivo.tell() == 0:
             escritor.writerow(["datetime", "metrica", "valor", "unidade"])
        escritor.writerow(dados)

def coletar_e_salvar(metricas_a_coletar: list, arquivo_saida):
    """Itera sobre a lista de objetos Metrica e salva no CSV."""
    for metrica_obj in metricas_a_coletar:
        dados = metrica_obj.obter_dados()
        salvar_dados_csv(arquivo_saida, dados)
        print(f"[{dados[0]}] Coletado {dados[1]}: {dados[2]} {dados[3]}")

def loop_coleta(metricas_a_coletar: list, intervalo_seg, max_iteracoes, arquivo_saida):
    """Desafio Extra A: Loop para coleta periódica."""
    print(f"\n--- Iniciando coleta periódica (Intervalo: {intervalo_seg}s) ---")
    
    for i in range(max_iteracoes):
        print(f"\n--- ITERAÇÃO {i + 1}/{max_iteracoes} ---")
        coletar_e_salvar(metricas_a_coletar, arquivo_saida)
        
        if i < max_iteracoes - 1:
            time.sleep(intervalo_seg)

    print("\n--- Coleta finalizada. ---")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Coletor de Métricas do Sistema (POO).")
    parser.add_argument(
        "-i", "--intervalo", type=int, default=5, 
        help="Intervalo de tempo em segundos entre as coletas (default: 5)."
    )
    parser.add_argument(
        "-n", "--iteracoes", type=int, default=10,
        help="Número máximo de iterações do loop de coleta (default: 10)."
    )
    parser.add_argument(
        "-o", "--output", type=str, default="metricas_poo.csv",
        help="Nome do arquivo CSV de saída (default: metricas_poo.csv)."
    )
    parser.add_argument(
        "-m", "--metricas", type=str, default="all",
        help="Métricas a coletar (separadas por vírgula): cpu, memoria, disco ou all (default: all)."
    )
    
    args = parser.parse_args()
    
    todas_metricas = {
        "cpu": CpuMetrica(),
        "memoria": MemoriaMetrica(),
        "disco": DiscoMetrica()
    }
    
    metricas_para_rodar = []
    if args.metricas == "all":
        metricas_para_rodar = list(todas_metricas.values())
    else:
        metricas_solicitadas = [m.strip().lower() for m in args.metricas.split(',')]
        for chave in metricas_solicitadas:
            if chave in todas_metricas:
                metricas_para_rodar.append(todas_metricas[chave])
            else:
                print(f"Aviso: Métrica '{chave}' não reconhecida e será ignorada.")
    
    if not metricas_para_rodar:
        print("Nenhuma métrica válida selecionada. Encerrando.")
        sys.exit(1)

    loop_coleta(
        metricas_para_rodar,
        args.intervalo,
        args.iteracoes,
        args.output
    )