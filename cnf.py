import os

def process_cnf_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    filtered_lines = [line for line in lines if not line.strip() in ['%', '0']]
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.cnf'):
                file_path = os.path.join(root, file)
                print(f"Processando: {file_path}")
                process_cnf_file(file_path)

if __name__ == "__main__":
    directory = input("Digite o caminho do diretório: ").strip()

    if os.path.isdir(directory):
        process_directory(directory)
        print("Processamento concluído!")
    else:
        print("O caminho fornecido não é um diretório válido.")
