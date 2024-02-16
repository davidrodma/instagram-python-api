import logging
from colorama import Style, Fore, Back,init

init(autoreset=True)


class ColorFormatter(logging.Formatter):
    # Change this dictionary to suit your coloring needs!
    COLORS = {
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "CRITICAL": Fore.RED + Back.WHITE
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        if color:
            record.name = color + record.name
            record.levelname = color + record.levelname
            record.msg = color + record.msg
        return logging.Formatter.format(self, record)


class LoggingUtility:

    @classmethod
    def get_logger(self,name:str):
        #logging.setLoggerClass(ColorLogger)
        logger = logging.getLogger(name)
        
        logger.setLevel(logging.INFO)  # Definindo o nível de registro do logger

        # Configurando um handler para enviar mensagens para a shell
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Definindo o formato das mensagens de log
        formatter = ColorFormatter("%(asctime)s %(message)s")
        console_handler.setFormatter(formatter)

        # Adicionando o handler ao logger
        logger.addHandler(console_handler)
        return logger
