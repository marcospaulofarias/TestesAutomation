from use_cases.UiAutomationClass import UiAutomationClass
from utils.serial_killer import kill_program_by_name

class Calculadora(UiAutomationClass):
    """Automação da calculadora do Windows usando uiautomation."""

    def __init__(self, process_id: str, process_type: str, process_machine: str, apps_needed_for_process: list[str]):
        super().__init__(process_id=process_id, 
                         process_type=process_type, 
                         process_machine=process_machine, 
                         apps_needed_for_process=apps_needed_for_process)

    def sum_1_1(self) -> None:
        """Realiza a soma 1 + 1 na calculadora do Windows.

        :return: None.
        """
        self.window_calculadora = self.find_element(element_type="Window", params={"name": "Calculadora"})
        button_1 = self.find_element(element_type="Button", params={"name": "Um"})
        self.interact_element(button_1)
        button_plus = self.find_element(screen=self.window_calculadora, element_type="Button", params={"name": "Mais"})
        self.interact_element(button_plus)
        button_1 = self.find_element(screen=self.window_calculadora, element_type="Button", params={"name": "Um"})
        self.interact_element(button_1)
        equal_to = self.find_element(screen=self.window_calculadora, element_type="Button", params={"name": "Igual a"})
        self.interact_element(equal_to)

    def multiply_dolar_value(self, multiply_valor: str, dolar_value: str) -> str:
        """Multiplica um valor pela cotação do dólar exibida na calculadora.

        :param multiply_valor: Valor a ser multiplicado pelo dólar.
        :param dolar_value: Cotação do dólar a ser usada na operação.
        :return: Texto exibido no resultado da calculadora após a operação.
        """
        self.window_calculadora = self.find_element(element_type="Window", params={"name": "Calculadora"})
        text_field = self.find_element(screen=self.window_calculadora, element_type="EditText", params={"automationid": "NormalOutput"})
        self.interact_element(text_field, value=dolar_value.replace(".", ","))
        button_multiply = self.find_element(screen=self.window_calculadora, element_type="Button", params={"name": "Multiplicar por"})
        self.interact_element(button_multiply)
        result_field = self.find_element(screen=self.window_calculadora, element_type="EditText", params={"automationid": "CalculatorResults"})
        self.interact_element(result_field, value=multiply_valor.replace(".", ","))
        equal_to = self.find_element(screen=self.window_calculadora, element_type="Button", params={"name": "Igual a"})
        self.interact_element(equal_to)
        result_text = self.find_element(screen=self.window_calculadora, element_type="EditText", params={"automationid": "CalculatorResults"})
        return result_text.Name

    def close(self, process_name: str = "CalculatorApp.exe") -> bool:
        """Finaliza o programa aberto na construção.

        :param process_name: Nome do processo a ser finalizado quando nome do processo for diferente do que está em apps_needed_for_process.
        :return: True se o encerramento foi solicitado com sucesso.
        """
        if not process_name:
            raise ValueError('Nenhum processo configurado para finalizar')
        return kill_program_by_name(process_name=process_name)

    def __enter__(self) -> "Calculadora":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
