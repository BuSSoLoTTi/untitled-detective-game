import logging



# Define o nível de logging global
logging.basicConfig(level=logging.DEBUG)

# Cria um handler para escrever os logs em um arquivo
file_handler = logging.FileHandler('app.log')
file_format = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler.setFormatter(file_format)
file_handler.setLevel(logging.DEBUG)

# Cria um handler para escrever os logs no console
console_handler = logging.StreamHandler()
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)
console_handler.setLevel(logging.DEBUG)

# Adiciona os handlers ao logger principal
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)
