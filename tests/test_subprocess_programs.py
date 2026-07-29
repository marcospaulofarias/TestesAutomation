from use_cases.Initializator import Initializator
from utils.serial_killer import kill_program_by_name
from time import sleep

if __name__ == '__main__':
    initializator = Initializator(process_id='test', process_type='test', process_machine='local')

    initializator.run_program(name_of_program='calc.exe', name_of_process='CalculatorApp.exe')
    sleep(5)
    kill_program_by_name(process_name='CalculatorApp.exe')
