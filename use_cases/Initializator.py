import subprocess
import time
import psutil
from loguru import logger
from use_cases.PrintAutomation import PrintAutomation
from utils.serial_killer import *

class Initializator:
    def __init__(self, process_id: str, process_type: str, process_machine: str) -> None:
        self.program_in_execute = None
        self.name_of_program = None
        self.name_of_process = None
        self.process_id = process_id
        self.process_type = process_type
        self.process_machine = process_machine
        self.printautomation = PrintAutomation(process_id=self.process_id, 
                                               process_type=self.process_type, 
                                               process_machine=self.process_machine)

    def run_program(self, 
                    name_of_program: str, 
                    name_of_process: str = None,
                    close_existing: bool = False, 
                    wait_existing: float = 0, 
                    new_cmd: bool = False) -> bool:
        """Executa um programa no Windows.

        :param name_of_program: Nome do programa a ser executado (ex: 'calc.exe').
        :param name_of_process: Nome do processo real quando difere do executado — apps UWP/stub
            materializam outro processo (ex: abrir 'calc.exe' resulta em 'CalculatorApp.exe').
            Quando informado, é usado para finalizar instâncias em close_existing.
        :param close_existing: Se True, finaliza instâncias já em execução antes de abrir.
            Usa name_of_process quando informado, senão name_of_program.
        :param wait_existing: Tempo máximo (s) a aguardar o processo alvo aparecer antes de finalizá-lo.
            0 (padrão) não espera. Útil ao reabrir em sequência rápida um app stub/UWP que
            demora a materializar o processo real (evita matar 'antes do tempo').
        :param new_cmd: Se True, abre o cmd.exe em nova janela de console.
        :returns: True se o programa foi iniciado com sucesso, False caso contrário.
        """
        self.name_of_program = name_of_program
        self.name_of_process = name_of_process
        process_name = name_of_process if name_of_process else name_of_program
        if close_existing:
            kill_program_by_name(process_name=process_name, process_id=self.process_id, process_type=self.process_type, process_machine=self.process_machine)
        try:
            self._wait_for_process(process_name, timeout=wait_existing)
        except RuntimeError:
            # Processo não apareceu dentro do timeout — continuar normalmente
            logger.debug(f'Processo "{process_name}" não encontrado antes de fechar; prosseguindo')
        try:
            if new_cmd:
                self.program_in_execute = subprocess.Popen(
                    ["cmd.exe", "/k"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                self.program_in_execute = subprocess.Popen(name_of_program)
                if wait_existing:
                    self._wait_for_process(process_name, timeout=wait_existing)
            return True
        except Exception as error_x:
            logger.critical(f'O programa "{name_of_program}" não pôde ser executado\nError: {error_x}')
            self.printautomation.print_error()
            raise RuntimeError(f'O programa "{name_of_program}" não pôde ser executado\nError: {error_x}') from error_x

    def _wait_for_process(self, process_name: str, timeout: float = 5, interval: float = 0.2) -> bool:
        """Aguarda um processo aparecer em execução.

        :param process_name: Nome do processo a aguardar (ex: 'CalculatorApp.exe').
        :param timeout: Tempo máximo (s) de espera.
        :param interval: Intervalo (s) entre as verificações.
        :returns: True se o processo apareceu dentro do timeout, False caso contrário.
        """
        fim = time.monotonic() + timeout
        while time.monotonic() < fim:
            if any(p.info['name'] == process_name for p in psutil.process_iter(['name'])):
                return True
            time.sleep(interval)
        self.printautomation.print_error()
        raise RuntimeError(f'O processo "{process_name}" não apareceu dentro do timeout')